from flask import (
    request,
    flash,
    render_template,
    url_for,
    redirect,
    Blueprint,
    session,
    send_file,
)
from db import mysql
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill
from werkzeug.utils import secure_filename
from cuentas import loguear_requerido, administrador_requerido
from MySQLdb import IntegrityError
import os

equipo = Blueprint("equipo", __name__, template_folder="app/templates")

# Ahora
from flask import send_file
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import os
import time

def get_equipo_data(mysql, filtros=None):
    """
    Obtiene los datos de la base de datos según los filtros proporcionados.
    :param mysql: Conexión a MySQL (Flask-MySQLdb)
    :param filtros: Diccionario con los posibles filtros (provincia, unidad, tipo, estado, fecha_inicio, fecha_fin, etc.)
    :return: Lista de diccionarios con los resultados de la consulta.
    """
    cur = mysql.connection.cursor()

    # Construcción básica de la consulta
    # Ajusta la consulta real según tu necesidad. Aquí usamos 'super_equipo' como ejemplo.
    query = """
    SELECT se.*, 
           u.nombreUnidad, 
           c.nombreComuna, 
           p.nombreProvincia,
           m.nombreModalidad,
           me.nombreModeloequipo,
           mae.nombreMarcaEquipo,
           oc.idOrden_compra,
           pvr.nombreProveedor
    FROM super_equipo se
    INNER JOIN unidad u ON u.idUnidad = se.idUnidad
    INNER JOIN comuna c ON c.idComuna = u.idComuna
    INNER JOIN provincia p ON c.idProvincia = p.idProvincia
    INNER JOIN modalidad m ON u.idModalidad = m.idModalidad
    INNER JOIN modelo_equipo me ON me.idModelo_Equipo = se.idModelo_Equipo
    INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = me.idMarca_Equipo
    INNER JOIN orden_compra oc ON oc.idOrden_compra = se.idOrden_compra
    INNER JOIN proveedor pvr ON pvr.idProveedor = oc.idProveedor
    WHERE 1=1
    """

    # Construir condiciones dinámicas si hay filtros
    params = []
    if filtros:
        # Ejemplo: filtro por provincia
        if filtros.get('provincia'):
            query += " AND p.idProvincia = %s"
            params.append(filtros['provincia'])

        # Ejemplo: filtro por unidad
        if filtros.get('unidad'):
            query += " AND u.idUnidad = %s"
            params.append(filtros['unidad'])

        # Ejemplo: filtro por tipo de equipo
        if filtros.get('tipo'):
            query += " AND se.idTipo_equipo = %s"
            params.append(filtros['tipo'])

        # Ejemplo: filtro por estado
        if filtros.get('estado'):
            query += " AND se.idEstado_equipo = %s"
            params.append(filtros['estado'])

        # Ejemplo: rango de fecha (asumiendo que filtras por la fecha de compra)
        if filtros.get('fecha_inicio'):
            query += " AND oc.fechacompraOrden_compra >= %s"
            params.append(filtros['fecha_inicio'])

        if filtros.get('fecha_fin'):
            query += " AND oc.fechacompraOrden_compra <= %s"
            params.append(filtros['fecha_fin'])

    # Ejecutar la consulta con los parámetros
    cur.execute(query, tuple(params))
    equipo_data = cur.fetchall()
    cur.close()

    return equipo_data

def generar_excel_equipo(equipo_data):
    """
    Genera un archivo Excel con los datos de equipo_data.
    :param equipo_data: Lista de diccionarios con los datos a exportar.
    :return: Ruta del archivo Excel generado.
    """
    # Crea un nuevo Workbook
    wb = Workbook()
    ws = wb.active

    # Encabezados (ajusta según tus columnas)
    encabezado = [
        "Provincia",
        "Comuna",
        "Modalidad",
        "Código Proveedor",
        "Unidad",
        "Tipo de Bien",
        "Marca",
        "Modelo",
        "N° Serie",
        "Cód. Inventario",
        "Proveedor",
    ]

    # Aplicar estilos y ancho de columna
    for idx, titulo in enumerate(encabezado, start=1):
        cell = ws.cell(row=1, column=idx)
        cell.value = titulo
        cell.fill = PatternFill(start_color="000ff000", fill_type="solid")
        ws.column_dimensions[cell.column_letter].width = 20

    # Llenar el Excel con los datos
    fila = 2
    for row in equipo_data:
        # Ajusta la extracción de datos a las llaves de tu diccionario
        ws.cell(row=fila, column=1).value = row["nombreProvincia"]
        ws.cell(row=fila, column=2).value = row["nombreComuna"]
        ws.cell(row=fila, column=3).value = row["nombreModalidad"]
        ws.cell(row=fila, column=4).value = row["codigoproveedor_equipo"]
        ws.cell(row=fila, column=5).value = row["nombreUnidad"]
        ws.cell(row=fila, column=6).value = row["nombreTipo_equipo"]
        ws.cell(row=fila, column=7).value = row["nombreMarcaEquipo"]
        ws.cell(row=fila, column=8).value = row["nombreModeloequipo"]
        ws.cell(row=fila, column=9).value = row["Num_serieEquipo"]
        ws.cell(row=fila, column=10).value = row["Cod_inventarioEquipo"]
        ws.cell(row=fila, column=11).value = row["nombreProveedor"]

        fila += 1

    # Guardar el archivo Excel en disco (puedes usar un nombre dinámico para evitar conflictos)
    filename = f"datos_exportados_{int(time.time())}.xlsx"
    wb.save(filename)

    return filename

# Ejemplo de uso dentro de una ruta Flask
@equipo.route("/equipo/exportar_excel")
def exportar_excel():
    """
    Ruta para exportar datos de equipo a Excel.
    Se pueden recibir filtros vía request.args (GET) o request.form (POST).
    """
    # Aquí recoges los filtros (GET o POST)
    filtros = {
        "provincia": request.args.get("provincia"),
        "unidad": request.args.get("unidad"),
        "tipo": request.args.get("tipo"),
        "estado": request.args.get("estado"),
        "fecha_inicio": request.args.get("fecha_inicio"),
        "fecha_fin": request.args.get("fecha_fin"),
    }

    # Obtener datos según los filtros
    data = get_equipo_data(mysql, filtros)

    # Generar el archivo Excel
    excel_path = generar_excel_equipo(data)

    # Enviar el archivo al usuario para su descarga
    return send_file(excel_path, as_attachment=True)


































# asi esta antes
@equipo.route("/test_excel_form", methods=["POST"])
@loguear_requerido
def test_excel_form():
    # para el uso de la pagina de otros
    tipos = (
        "aio",
        "notebook",
        "impresoras",
        "bam",
        "proyectores",
        "telefonos",
        "disco_duro",
        "tablets",
    )
    todo_check = request.form.get("todo_check")
    # si se imprime todo en una hoja usar la funcion ya creada
    if todo_check == "on":
        print("test")
        return crear_excel()
    # de lo contrario imprimir cada hoja individualmente
    computadora_check = request.form.get("AIO_check")
    notebooks_check = request.form.get("Notebooks")
    impresoras_check = request.form.get("impresoras_check")
    bam_check = request.form.get("bam_check")
    proyectores_check = request.form.get("proyectores_check")
    telefonos_check = request.form.get("telefonos_check")
    HDD_check = request.form.get("HDD_check")
    tablets_check = request.form.get("tablets_check")
    otros_check = request.form.get("otros_check")
    wb = Workbook()
    ws = wb.active
    if computadora_check == "on":
        ws.title = "AIO"
        añadir_hoja_de_tipo("AIO", ws)
        ws = wb.create_sheet("sheet")
    if notebooks_check == "on":
        ws.title = "Notebooks"
        añadir_hoja_de_tipo("Notebooks", ws)
        ws = wb.create_sheet("sheet")
    if impresoras_check == "on":
        ws.title = "Impresoras"
        añadir_hoja_de_tipo("impresoras", ws)
        ws = wb.create_sheet("sheet")
    if bam_check == "on":
        ws.title = "Bam"
        añadir_hoja_de_tipo("bam", ws)
        ws = wb.create_sheet("sheet")
    if proyectores_check == "on":
        ws.title = "Proyectores"
        añadir_hoja_de_tipo("proyectores", ws)
        ws = wb.create_sheet("sheet")
    if telefonos_check == "on":
        ws.title = "Telefono"
        añadir_hoja_de_tipo("telefono", ws)
        ws = wb.create_sheet("sheet")
    if HDD_check == "on":
        ws.title = "Disco Duro"
        añadir_hoja_de_tipo("disco_duro", ws)
        ws = wb.create_sheet("sheet")
    if tablets_check == "on":
        ws.title = "Tablets"
        añadir_hoja_de_tipo("tablets", ws)
        ws = wb.create_sheet("sheet")
    # al ser otro requiere una consulta distinta ya que tendria que ser distinto a
    # todas las categorias anteriores
    if otros_check == "on":
        print("otros")
        ws.title = "Otros"
        añadir_hoja_de_otros(tipos, ws)
        ws = wb.create_sheet("sheet")

        wb.save("test_exportados.xlsx")
        return send_file("test_exportados.xlsx", as_attachment=True)
    return redirect(url_for("equipo.Equipo"))


def añadir_hoja_de_otros(tipos, ws):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    query = """

    SELECT *
    FROM
    (
    SELECT e.idEquipo, e.Cod_inventarioEquipo, 
           e.Num_serieEquipo, e.ObservacionEquipo,
           e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, 
           e.numerotelefonicoEquipo,
           te.idTipo_equipo, 
           te.nombreTipo_Equipo as tipo_equipo, ee.idEstado_equipo, ee.nombreEstado_equipo, 
           u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
           com.nombreComuna, pro.nombreProvincia,
    moe.idModelo_equipo, moe.nombreModeloequipo, "" as nombreFuncionario,
                me.nombreMarcaEquipo, mo.nombreModalidad,
            pr.nombreProveedor
    FROM equipo e
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = moe.idModelo_equipo
    INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    left JOIN marca_equipo me on me.idMarca_Equipo = me.idMarca_Equipo
    LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad

    LEFT JOIN comuna com ON com.idComuna = u.idComuna
    LEFT JOIN provincia pro ON pro.idProvincia = com.idProvincia
    INNER JOIN proveedor pr ON pr.idProveedor = oc.idProveedor

    WHERE ee.nombreEstado_equipo NOT LIKE "En Uso"
    UNION 
    SELECT  e.idEquipo, e.Cod_inventarioEquipo, 
            e.Num_serieEquipo, e.ObservacionEquipo, 
            e.codigoproveedor_equipo, e.macEquipo, 
            e.imeiEquipo, e.numerotelefonicoEquipo,
            te.idTipo_equipo, te.nombreTipo_Equipo,
            ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad,
            u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
            moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario,
            com.nombreComuna, pro.nombreProvincia,
            me.nombreMarcaEquipo, mo.nombreModalidad,
            pr.nombreProveedor
    FROM equipo e
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = moe.idModelo_equipo
    INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
    INNER JOIN unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
     JOIN marca_equipo me on me.idMarca_Equipo = me.idMarca_Equipo
    LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad

    INNER JOIN equipo_asignacion ea on ea.idEquipo = e.idEquipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    LEFT JOIN asignacion a on a.idAsignacion = ea.idAsignacion
    LEFT JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
    LEFT JOIN comuna com ON com.idComuna = u.idComuna
    LEFT JOIN provincia pro ON pro.idProvincia = com.idProvincia
    INNER JOIN proveedor pr ON pr.idProveedor = oc.idProveedor
    WHERE ee.nombreEstado_equipo LIKE "EN USO"
    ) as subquery
    WHERE

"""

    for i in range(0, len(tipos)):
        query += """
        tipo_equipo NOT LIKE '{}'
        """.format(
            tipos[i]
        )
        if i != len(tipos) - 1:
            query += " AND "
    cur.execute(query)
    equipo_data = cur.fetchall()

    encabezado = [
        "Provincia",
        "Comuna",
        "Modalidad",
        "Codigo Proveedor",
        "Nombre",
        "Tipo de Bien",
        "Marca",
        "Modelo",
        "N° Serie",
        "Codigo Inventario",
        "Nombre Proveedor",
    ]
    print("encabezado len: " + str(len(encabezado)))
    print(encabezado[10])
    for i in range(0, len(encabezado)):
        print(i)
        char = chr(65 + i)
        ws[char + str(1)].fill = PatternFill(start_color="000ff000", fill_type="solid")
        ws.column_dimensions[char].width = 20
        ws[char + str(1)] = encabezado[i]

    i = 0

    def fillCell(data, fila):
        nonlocal i
        char = chr(65 + i)
        i += 1
        ws[char + str(fila)] = data

    for fila in range(0, len(equipo_data)):
        i = 0
        # 65 = A en ASCII
        # consegir lista de valores y extraer la lista de valires en cada for interior
        fillCell(equipo_data[fila]["nombreProvincia"], fila + 2)
        fillCell(equipo_data[fila]["nombreComuna"], fila + 2)
        fillCell(equipo_data[fila]["nombreModalidad"], fila + 2)
        fillCell(equipo_data[fila]["codigoproveedor_equipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreUnidad"], fila + 2)
        fillCell(equipo_data[fila]["tipo_equipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreMarcaEquipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreModeloequipo"], fila + 2)
        fillCell(equipo_data[fila]["Num_serieEquipo"], fila + 2)
        fillCell(equipo_data[fila]["Cod_inventarioEquipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreProveedor"], fila + 2)

    pass


def añadir_hoja_de_tipo(tipo, ws):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT *
    FROM
    (
    SELECT DISTINCT e.idEquipo, e.Cod_inventarioEquipo, 
           e.Num_serieEquipo, e.ObservacionEquipo,
           e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, 
           e.numerotelefonicoEquipo,
           te.idTipo_equipo, 
           te.nombreTipo_Equipo as tipo_equipo, ee.idEstado_equipo, ee.nombreEstado_equipo, 
           u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
           com.nombreComuna, pro.nombreProvincia,
    moe.idModelo_equipo, moe.nombreModeloequipo, "" as nombreFuncionario,
                me.nombreMarcaEquipo, mo.nombreModalidad,
                pr.nombreProveedor
    FROM equipo e
     JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
     JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
     JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
     JOIN unidad u on u.idUnidad = e.idUnidad
     JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    RIGHT JOIN marca_equipo me on me.idMarca_Equipo = me.idMarca_Equipo
    LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad

    LEFT JOIN comuna com ON com.idComuna = u.idComuna
    LEFT JOIN provincia pro ON pro.idProvincia = com.idProvincia
     JOIN proveedor pr ON oc.idProveedor = pr.idProveedor

    WHERE ee.nombreEstado_equipo NOT LIKE "EN USO"
    UNION 
    SELECT  e.idEquipo, e.Cod_inventarioEquipo, 
            e.Num_serieEquipo, e.ObservacionEquipo, 
            e.codigoproveedor_equipo, e.macEquipo, 
            e.imeiEquipo, e.numerotelefonicoEquipo,
            te.idTipo_equipo, te.nombreTipo_Equipo,
            ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad,
            u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
            moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario,
            com.nombreComuna, pro.nombreProvincia,
            me.nombreMarcaEquipo, mo.nombreModalidad,
            pr.nombreProveedor
                
    FROM equipo e
     JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
     JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
     JOIN unidad u on u.idUnidad = e.idUnidad
     JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    RIGHT JOIN marca_equipo me on me.idMarca_Equipo = me.idMarca_Equipo
    LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad

     JOIN equipo_asignacion ea on ea.idEquipo = e.idEquipo
     JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    LEFT JOIN asignacion a on a.idAsignacion = ea.idAsignacion
    LEFT JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
    LEFT JOIN comuna com ON com.idComuna = u.idComuna
    LEFT JOIN provincia pro ON pro.idProvincia = com.idProvincia
     JOIN proveedor pr ON oc.idProveedor = pr.idProveedor
    WHERE ee.nombreEstado_equipo LIKE "EN USO"
    ) as subquery
    WHERE tipo_equipo LIKE %s
                """,
        (tipo,),
    )
    equipo_data = cur.fetchall()

    encabezado = [
        "Provincia",
        "Comuna",
        "Modalidad",
        "Codigo Proveedor",
        "Nombre",
        "CodigoUnidad",
        "Tipo de Bien",
        "Marca",
        "Modelo",
        "N° Serie",
        "Codigo Inventario",
        "Nombre Proveedor",
    ]
    for i in range(0, len(encabezado)):
        char = chr(65 + i)
        ws[char + str(1)].fill = PatternFill(start_color="000ff000", fill_type="solid")
        ws.column_dimensions[char].width = 20
        ws[char + str(1)] = encabezado[i]

    i = 0

    def fillCell(data, fila):
        nonlocal i
        char = chr(65 + i)
        i += 1
        ws[char + str(fila)] = data

    for fila in range(0, len(equipo_data)):
        i = 0
        # 65 = A en ASCII
        # consegir lista de valores y extraer la lista de valires en cada for interior
        fillCell(equipo_data[fila]["nombreProvincia"], fila + 2)
        fillCell(equipo_data[fila]["nombreComuna"], fila + 2)
        fillCell(equipo_data[fila]["nombreModalidad"], fila + 2)
        fillCell(equipo_data[fila]["codigoproveedor_equipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreUnidad"], fila + 2)
        fillCell(equipo_data[fila]["idUnidad"], fila + 2)
        fillCell(equipo_data[fila]["tipo_equipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreMarcaEquipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreModeloequipo"], fila + 2)
        fillCell(equipo_data[fila]["Num_serieEquipo"], fila + 2)
        fillCell(equipo_data[fila]["Cod_inventarioEquipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreProveedor"], fila + 2)

    # ingresar datos
    return


# exportar a pdf
@equipo.route("/equipo/crear_excel")
@loguear_requerido
def crear_excel():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    # buscar columnas
    wb = Workbook()
    ws = wb.active

    # consulta datos
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT * 
    FROM super_equipo se
    INNER JOIN unidad u ON u.idUnidad = se.idUnidad
    INNER JOIN modalidad m ON u.idModalidad = m.idModalidad
    INNER JOIN comuna c ON c.idComuna = u.idComuna
    INNER JOIN provincia p ON c.idProvincia = p.idProvincia
    INNER JOIN modelo_equipo me ON me.idModelo_Equipo = se.idModelo_Equipo
    INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = me.idMarca_Equipo
    INNER JOIN orden_compra oc ON oc.idOrden_compra = se.idOrden_compra
    INNER JOIN proveedor pvr ON pvr.idProveedor = oc.idProveedor
    """
    )
    equipo_data = cur.fetchall()

    print(equipo_data)
    # generar encabezado
    # encabezado

    encabezado = [
        "Provincia",
        "Comuna",
        "Modalidad",
        "Codigo Proveedor",
        "Nombre",
        "Tipo de Bien",
        "Marca",
        "Modelo",
        "N° Serie",
        "Codigo Inventario",
        "Nombre Proveedor",
    ]
    for i in range(0, len(encabezado)):
        char = chr(65 + i)
        ws[char + str(1)].fill = PatternFill(start_color="000ff000", fill_type="solid")
        ws.column_dimensions[char].width = 20
        ws[char + str(1)] = encabezado[i]

    i = 0

    def fillCell(data, fila):
        nonlocal i
        char = chr(65 + i)
        i += 1
        ws[char + str(fila)] = data

    for fila in range(0, len(equipo_data)):
        i = 0
        # 65 = A en ASCII
        # consegir lista de valores y extraer la lista de valires en cada for interior
        fillCell(equipo_data[fila]["nombreProvincia"], fila + 2)
        fillCell(equipo_data[fila]["nombreComuna"], fila + 2)
        fillCell(equipo_data[fila]["nombreModalidad"], fila + 2)
        fillCell(equipo_data[fila]["codigoproveedor_equipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreUnidad"], fila + 2)
        fillCell(equipo_data[fila]["nombreTipo_equipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreMarcaEquipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreModeloequipo"], fila + 2)
        fillCell(equipo_data[fila]["Num_serieEquipo"], fila + 2)
        fillCell(equipo_data[fila]["Cod_inventarioEquipo"], fila + 2)
        fillCell(equipo_data[fila]["nombreProveedor"], fila + 2)

    # ingresar datos
    wb.save("datos_exportados.xlsx")
    return send_file("datos_exportados.xlsx", as_attachment=True)


def crear_pagina_todojunto(wb):
    return wb
