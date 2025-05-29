from flask import Blueprint, render_template, request, url_for, redirect, flash, send_file, session, jsonify
from . import mysql
from fpdf import FPDF
from .funciones import getPerPage
import os
import shutil
from werkzeug.utils import secure_filename
from datetime import date
from .cuentas import loguear_requerido, administrador_requerido
from .traslado import crear_traslado_generico
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import fitz
from env_vars import paths, inLinux
from cerberus import Validator
from MySQLdb import IntegrityError

schema_asignacion = {
    'fecha_asignacion': {
        'type': 'string',
        'regex': r'^\d{4}-\d{2}-\d{2}$',  # Formato YYYY-MM-DD
    },
    'rut_funcionario': {
        'type': 'string',
        'minlength': 6,
        'maxlength': 10,
        'regex': r'^\d{7,8}(-[0-9Kk])?$',
    },
    'observacion': {
        'type': 'string',
        'minlength': 0,
        'maxlength': 250,
    },
    'equipos_asignados': {
        'type': 'list',
        'minlength': 1,  # Al menos un equipo debe ser seleccionado
        'schema': {'type': 'integer'},  # Los valores deben ser enteros
    }
}

asignacion = Blueprint("asignacion", __name__, template_folder="app/templates")
@asignacion.route("/asignacion")
@asignacion.route("/asignacion/<int:page>")
@loguear_requerido
def Asignacion(page=1):
    perpage = getPerPage()
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(f"""
    SELECT
        a.idAsignacion,
        a.fecha_inicioAsignacion,
        a.ObservacionAsignacion,
        a.ActivoAsignacion,
        f.rutFuncionario,
        f.nombreFuncionario,
        f.cargoFuncionario,
        ea.idEquipoAsignacion,
        d.idDevolucion,
        d.fechaDevolucion,
        me.nombreModeloequipo,
        te.nombreTipo_equipo,
        mae.nombreMarcaEquipo,
        e.Cod_inventarioEquipo,
        e.Num_serieEquipo,
        e.codigoproveedor_equipo,
        e.ObservacionEquipo
    FROM asignacion a
    JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
    JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
    LEFT JOIN devolucion d ON ea.idEquipoAsignacion = d.idEquipoAsignacion
    JOIN equipo e ON e.idEquipo = ea.idEquipo
    JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
    JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
    JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
    JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
    ORDER BY a.idAsignacion DESC
    LIMIT %s OFFSET %s
    """, (perpage, offset))
    data = cur.fetchall()

    # Formatear fechas
    for row in data:
        row['fecha_inicio'] = row['fecha_inicioAsignacion'].strftime('%d-%m-%Y') if row['fecha_inicioAsignacion'] else 'N/A'
        row['fecha_devolucion'] = row['fechaDevolucion'].strftime('%d-%m-%Y') if row['fechaDevolucion'] else 'Sin devolver'

    # Total para paginación
    cur.execute("SELECT COUNT(*) AS total FROM asignacion")
    total = cur.fetchone()['total']
    lastpage = (total + perpage - 1) // perpage

    # Funcionarios
    cur.execute("""SELECT rutFuncionario, nombreFuncionario FROM funcionario ORDER BY nombreFuncionario""")
    funcionarios = cur.fetchall()

    # Equipos sin asignar
    cur.execute("""
        SELECT 
            e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo,
            e.codigoproveedor_equipo, e.ObservacionEquipo,
            me.nombreModeloequipo, te.nombreTipo_equipo,
            mae.nombreMarcaEquipo, u.nombreUnidad
        FROM equipo e
        JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
        JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
        JOIN estado_equipo ee ON e.idEstado_equipo = ee.idEstado_equipo
        JOIN unidad u ON e.idUnidad = u.idUnidad
        WHERE ee.nombreEstado_equipo = 'SIN ASIGNAR'
    """)
    equipos_sin_asignar = cur.fetchall()

    cur.close()

    return render_template(
        'GestionR.H/asignacion.html',
        funcionarios=funcionarios,
        asignacion=data,
        equipos_sin_asignar=equipos_sin_asignar,
        page=page,
        lastpage=lastpage
    )
def getPerPage():
    return 10 

@asignacion.route("/asignacion/create_asignacion", methods=["POST"])
@administrador_requerido
def create_asignacion():
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")

    if request.method != "POST":
        return redirect(url_for("asignacion.Asignacion"))

    # Obtiene los datos del formulario
    fecha_asignacion = request.form.get('fecha-asignacion') 
    rut_funcionario = request.form.get('rut_funcionario')
    observacion = request.form.get('observacion')
    id_equipos = [int(equipo) for equipo in request.form.getlist('equiposAsignados[]')]

    # Se crea un objeto para poder validar los datos recibidos
    data = {
        'fecha_asignacion': fecha_asignacion,
        'observacion': observacion,
        'equipos_asignados': id_equipos,
    }
    print(data)

    # Valida los campos y muestra solo el primer mensaje de error
    v = Validator(schema_asignacion)
    
    if not v.validate(data):
        for campo, mensaje in v.errors.items():
            flash(f"Error en '{campo}': {mensaje[0]}", 'warning')
            break
        return redirect(url_for("asignacion.Asignacion"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO asignacion (
                fecha_inicioAsignacion,
                ObservacionAsignacion,
                rutFuncionario,
                ActivoAsignacion
            )
            VALUES (%s, %s, %s, 1)
            """, (fecha_asignacion, observacion, rut_funcionario))
        id_asignacion = cur.lastrowid # Recupera el ID de la asignación recién insertada

        TuplaEquipos = ()

        # Recorre los equipos asignados
        for id_equipo in id_equipos:
            # Inserta los datos en la tabla equipo_asignacion
            cur.execute("""
                INSERT INTO equipo_asignacion (idAsignacion, idEquipo)
                VALUES (%s, %s)
                """, (id_asignacion, id_equipo))

            # Encuentra el ID del estado "EN USO"
            cur.execute("""
                        SELECT *
                        FROM estado_equipo
                        WHERE nombreEstado_equipo = %s
                        """, ("EN USO",))
            id_estado_equipo = cur.fetchone()['idEstado_equipo']
                
            # Cambia el estado del equipo a "EN USO"
            cur.execute("""
                        UPDATE equipo
                        SET idEstado_equipo = %s
                        WHERE idEquipo = %s
                        """, (id_estado_equipo, id_equipo))

            #Seleccionar el equipo de equipo_asignacion y agregarlo a una tupla para el excel
            cur.execute("""
                        SELECT e.*, 
                            me.nombreModeloequipo, 
                            te.nombreTipo_equipo, 
                            mae.nombreMarcaEquipo, 
                            ee.nombreEstado_equipo
                        FROM equipo e
                        INNER JOIN modelo_equipo me ON me.idModelo_Equipo = e.idModelo_Equipo
                        INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
                        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
                        INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
                        INNER JOIN estado_equipo ee ON ee.idEstado_equipo = e.idEstado_equipo
                        WHERE e.idEquipo = %s
                        """, (id_equipo,))
            equipoTupla = cur.fetchone()
            TuplaEquipos = TuplaEquipos + (equipoTupla,)
        mysql.connection.commit()

        # Obtiene información relevante del funcionario para añadir al PDF
        cur.execute("""
            SELECT
                f.nombreFuncionario,
                a.idAsignacion,
                a.fecha_inicioAsignacion,
                u.nombreUnidad,
                u.idUnidad
            FROM funcionario f
            JOIN asignacion a ON f.rutFuncionario = a.rutFuncionario
            JOIN unidad u ON f.idUnidad = u.idUnidad
            WHERE a.idAsignacion = %s
        """, (id_asignacion,))
        query = cur.fetchone()

        funcionario = {
            "nombre": query["nombreFuncionario"],
            "id_asignacion": str(query["idAsignacion"]),
            "fecha_asignacion": str(query["fecha_inicioAsignacion"].strftime("%d-%m-%Y")),
            "unidad": query["nombreUnidad"],
            "idUnidad": query["idUnidad"]
        }
    except IntegrityError as e:
        error_message = str(e)
        if "FOREIGN KEY (`rutFuncionario`) REFERENCES `funcionario` (`rutFuncionario`)" in error_message:
            flash("Error: No se selecciono funcionario Unidad", 'warning')
        return redirect(url_for("asignacion.Asignacion"))

    except Exception as e:
        mysql.connection.rollback()  # En caso de error, se revierten los cambios
        flash("Error al crear la asignación: " + str(e), 'danger')
        return redirect(url_for("asignacion.Asignacion"))

    flash("Asignación agregada exitosamente", 'success')
    
    return redirect(url_for('asignacion.Asignacion'))

# enviar datos a vista editar
@asignacion.route("/asignacion/edit_asignacion/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        #se obtiene la asignacion actual
        cur.execute(
            """ 
           SELECT  
                a.idAsignacion,
                a.fecha_inicioAsignacion,
                a.observacionAsignacion,
                a.rutaactaAsignacion,
                a.rutFuncionario,
                f.nombreFuncionario,
                d.fechaDevolucion
                FROM asignacion a
                INNER JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
                LEFT JOIN devolucion d ON a.idDevolucion = d.idDevolucion
            WHERE idAsignacion = %s""",
            (id,),
        )
        #esto para los select
        data = cur.fetchone()
        cur.execute("SELECT * FROM funcionario")
        f_data = cur.fetchall()
        #creo que el equipo se deberia porder borrar
        cur.execute("SELECT * FROM equipo")
        eq_data = cur.fetchall()
        #print(data)
        #print(data['observacionAsignacion'])
        return render_template(
            'GestionR.H/editAsignacion.html', 
            asignacion=data, 
            funcionario=f_data, 
            equipo=eq_data
        )
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))


# actualizar
@asignacion.route("/asignacion/update_asignacion/<id>", methods=["POST"])
@administrador_requerido
def update_asignacion(id):
    if request.method == "POST":
        #obtener informacion del formulario
        fechaasignacion = request.form["fechaasignacion"]
        observacionasignacion = request.form["observacionasignacion"]
        rutFuncionario = request.form["rutFuncionario"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE asignacion
            SET fecha_inicioAsignacion = %s,
                ObservacionAsignacion = %s,
                rutFuncionario = %s
            WHERE idAsignacion = %s
            """,
                (
                    fechaasignacion,
                    observacionasignacion,
                    rutFuncionario,
                    id,
                ),
            )
            mysql.connection.commit()
            flash("asignacion actualizado correctamente")
            return redirect(url_for("asignacion.Asignacion"))
        except Exception as e:

            flash("Error al crear")
            #flash(e.args[1])
            return redirect(url_for("asignacion.Asignacion"))


# eliminar
@asignacion.route("/delete_asignacion/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT *
                    FROM asignacion
                    WHERE idAsignacion = %s
                    """, (id,))
        asignacionAborrar = cur.fetchone()
        #encontrar todas las tablas equipo_asignacion que contengan la id de la asignacion
        cur.execute("""SELECT *
                        FROM equipo_asignacion
                        WHERE idAsignacion= %s
        """, (id,))
        asignaciones = cur.fetchall()
        #revisar cada equipo_asignacion individualmente
        for asignacion in asignaciones:
            idEquipo = asignacion['idEquipo']
            #encontrar la id del estado sin asignar
            cur.execute("""
                        SELECT *
                        FROM estado_equipo
                        WHERE nombreEstado_equipo = %s
                        """, ("SIN ASIGNAR",))
            estado_equipo_data = cur.fetchone()
            #cambiar el estado de cada equipo en la asignacion eliminada a sin asignar
            cur.execute("""
                        UPDATE equipo
                        SET idEstado_equipo = %s
                        WHERE idEquipo = %s
                        """, (estado_equipo_data['idEstado_equipo'], idEquipo))
            mysql.connection.commit()
        cur.execute("DELETE FROM equipo_asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        cur.execute("DELETE FROM asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()

        flash("Asignación eliminada exitosamente", "success")
        return redirect(url_for("asignacion.Asignacion"))
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
        return redirect(url_for("asignacion.Asignacion"))

def crear_pdf_asignacion(funcionario, equipos):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    class PDF(FPDF):
        def header(self):
            #imagen del encabezado
            self.image("static/img/logo_junji.png", 10, 8, 32)
            # font
            self.set_font("times", "B", 12)
            self.set_text_color(170, 170, 170)
            # Title
            self.cell(0, 30, "", border=False, ln=1, align="L")
            self.cell(0, 5, "JUNTA NACIONAL DE", border=False, ln=1, align="L")
            self.cell(0, 5, "JARDINES INFANTILES", border=False, ln=1, align="L")
            self.cell(0, 5, "Unidad de Inventarios", border=False, ln=1, align="L")
            # line break
            self.ln(10)

        def footer(self):
            self.set_y(-30)
            self.set_font("times", "B", 12)
            self.set_text_color(170, 170, 170)
            self.cell(0, 0, "", ln=1)
            self.cell(0, 0, "Junta Nacional de Jardines Infantiles - JUNJI", ln=1)
            self.cell(0, 12, "O'Higgins Poniente 77 Concepción. Tel: 412125579", ln=1)
            self.cell(0, 12, "www.junji.cl", ln=1)

    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    titulo = "ACTA de Asignación de Equipo Informático N°" + funcionario["id_asignacion"]

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    creado_por = "Documento creado por: " + session['user']
    pdf.cell(0, 10, creado_por, ln=True, align="L")
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la unidad: "
    presentacion22 = "En la fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombre_funcionario = funcionario["nombre"]
    unidad_funcionario = funcionario["unidad"]
    fecha_asignacion = funcionario["fecha_asignacion"]

    pdf.ln(10)
    #se hace en columnas para que quede ordenado
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(presentacion1)
        cols.ln()
        cols.write(presentacion2)
        cols.ln()
        cols.write(presentacion22)
        cols.ln()
        cols.ln()
        cols.write(presentacion3)
        cols.ln()
        cols.new_column()
        #lo que se escribe despues de new_column va en la siguiente columna
        cols.write(nombre_funcionario)
        cols.ln()
        cols.write(unidad_funcionario)
        cols.ln()
        cols.write(fecha_asignacion)

    pdf.ln(20)
    #Encabezado de la tabla
    TABLE_DATA = (
        ("N°", "Tipo equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    i = 0
    for equipo in equipos:
        tipo_equipo = equipo["nombreTipo_equipo"]
        marca = equipo["nombreMarcaEquipo"]
        modelo = equipo["nombreModeloequipo"]
        num_serie = str(equipo["Num_serieEquipo"])
        num_inventario = str(equipo["Cod_inventarioEquipo"])

        i += 1

        TABLE_DATA = TABLE_DATA + (
            (str(i), tipo_equipo, marca, modelo, num_serie, num_inventario),
        )
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)

    pdf.ln(10)
    nombreEncargado = "Nombre del encargado TI:"
    rutEncargado = "RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre del funcionario:"
    rutMinistro = "RUT:"
    firma = "Firma"
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(nombreEncargado)
        cols.ln()
        cols.ln()
        cols.write(rutEncargado)
        cols.ln()
        cols.ln()
        cols.write(firmaEncargado)
        cols.ln()
        cols.ln()
        cols.ln()
        cols.ln()

        cols.write(nombreMinistro)
        cols.ln()
        cols.ln()
        cols.write(rutMinistro)
        cols.ln()
        cols.ln()
        cols.write(firma)
        cols.ln()
        cols.ln()
        cols.new_column()
        for i in range(0, 3):
            if i == 0:
                cols.write(text= session['user'])
            else:
                cols.write(text="___________________________________")
            cols.ln()
            cols.ln()
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="___________________________________")
            cols.ln()
            cols.ln()
    #*(path cambiado y creacion de carpeta asignaciones)
    ruta_asignaciones = "pdf/asignaciones"
    # Asegurar que la carpeta "pdf/asignaciones" exista
    os.makedirs(ruta_asignaciones, exist_ok=True)
    nombrePdf = "asignacion_" + funcionario["id_asignacion"] + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, os.path.join(ruta_asignaciones, nombrePdf))
    return nombrePdf

@asignacion.route("/asignacion/descargar_pdf_asignacion/<id>")
@loguear_requerido
def descargar_pdf_asignacion(id):
    try:
        nombrePDF = "asignacion_" + str(id) + ".pdf"
        file = os.path.join("pdf/asignaciones", nombrePDF)
        return send_file(file, as_attachment=False)
    except:
        flash("Error: No se encontró el PDF", "danger")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/devolver_equipos", methods=["POST"])
@administrador_requerido
def devolver_equipos():
    # Obtener los ID de equipo_asignacion desde el formulario
    ids_equipos_asignacion = request.form.getlist("equiposSeleccionados")

    if not ids_equipos_asignacion:
        flash("No se seleccionó ningún equipo para devolver", "danger")
        return redirect(url_for("asignacion.Asignacion"))

    today = date.today()
    cur = mysql.connection.cursor()

    # Iniciar una transacción
    cur.execute("START TRANSACTION")

    # Obtener el ID del estado "SIN ASIGNAR"
    cur.execute("SELECT idEstado_equipo FROM estado_equipo WHERE nombreEstado_equipo = 'SIN ASIGNAR'")
    estado_sin_asignar = cur.fetchone()

    if not estado_sin_asignar:
        flash("No se encontró el estado 'SIN ASIGNAR'", "danger")
        cur.execute("ROLLBACK")  # Cancelar cualquier cambio
        return redirect(url_for("asignacion.Asignacion"))

    id_estado_sin_asignar = estado_sin_asignar["idEstado_equipo"]

    for id_equipo_asignacion in ids_equipos_asignacion:
        # Verificar si ya fue devuelto
        cur.execute("""
            SELECT idDevolucion 
            FROM devolucion 
            WHERE idEquipoAsignacion = %s
        """, (id_equipo_asignacion,))
        if cur.fetchone():  # Si existe, detener todo el proceso
            flash("Error: Uno o más equipos seleccionados ya fueron devueltos", "danger")
            cur.execute("ROLLBACK")  # Cancelar todo el proceso
            return redirect(url_for("asignacion.Asignacion"))


    # Si no hay errores, proceder con la devolución
    for id_equipo_asignacion in ids_equipos_asignacion:
        # Obtener la asignación y el equipo correspondiente
        cur.execute("""
            SELECT ea.idAsignacion, ea.idEquipo
            FROM equipo_asignacion ea
            WHERE ea.idEquipoAsignacion = %s
        """, (id_equipo_asignacion,))
        equipo_asignacion_info = cur.fetchone()

        if not equipo_asignacion_info:
            flash(f"No se encontró información para el equipo asignado {id_equipo_asignacion}.", "warning")
            cur.execute("ROLLBACK")  # Cancelar todo el proceso
            return redirect(url_for("asignacion.Asignacion"))

        id_asignacion = equipo_asignacion_info["idAsignacion"]
        id_equipo = equipo_asignacion_info["idEquipo"]

        # Registrar la devolución en la tabla devolucion
        cur.execute("""
            INSERT INTO devolucion (fechaDevolucion, idEquipoAsignacion)
            VALUES (%s, %s)
        """, (today, id_equipo_asignacion))
        id_devolucion = str(cur.lastrowid) # Recupera el ID de la devolución recién insertada

        # Actualizar el estado del equipo a "SIN ASIGNAR"
        cur.execute("""
            UPDATE equipo
            SET idEstado_equipo = %s
            WHERE idEquipo = %s
        """, (id_estado_sin_asignar, id_equipo))

        # Verificar si todos los equipos de la asignación ya fueron devueltos
        cur.execute("""
            SELECT COUNT(*) AS equipos_no_devueltos
            FROM equipo_asignacion ea
            LEFT JOIN devolucion d ON ea.idEquipoAsignacion = d.idEquipoAsignacion
            WHERE ea.idAsignacion = %s AND d.idDevolucion IS NULL
        """, (id_asignacion,))
        equipos_pendientes = cur.fetchone()

        # Si no hay más equipos pendientes, actualizar la asignación como cerrada
        if equipos_pendientes["equipos_no_devueltos"] == 0:
            cur.execute("""
                UPDATE asignacion
                SET ActivoAsignacion = 0
                WHERE idAsignacion = %s
            """, (id_asignacion,))

    # Obtiene información relevante del funcionario para añadir al PDF
    cur.execute("""
        SELECT 
            f.nombreFuncionario,
            a.idAsignacion,
            a.fecha_inicioAsignacion,
            u.nombreUnidad
        FROM funcionario f
        JOIN asignacion a ON f.rutFuncionario = a.rutFuncionario
        JOIN unidad u ON f.idUnidad = u.idUnidad
        WHERE a.idAsignacion = %s
    """, (id_asignacion,))
    query = cur.fetchone()

    data_funcionario_PDF = {
        "nombre": query["nombreFuncionario"],
        "id_asignacion": str(query["idAsignacion"]),
        "fecha_asignacion": str(query["fecha_inicioAsignacion"].strftime("%d-%m-%Y")),
        "unidad": query["nombreUnidad"]
    }

    # Obtiene información relevante de los equipos seleccionados para devolver para añadir al PDF
    placeholders = ', '.join(['%s'] * len(ids_equipos_asignacion))
    cur.execute(f"""
        SELECT
            te.nombreTipo_equipo,
            mae.nombreMarcaEquipo,
            me.nombreModeloequipo,
            e.Num_serieEquipo,
            e.Cod_inventarioEquipo
        FROM equipo e
        JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
        JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
        JOIN equipo_asignacion ea ON e.idEquipo = ea.idEquipo
        WHERE ea.idEquipoAsignacion IN ({placeholders})
    """, tuple(ids_equipos_asignacion))
    query = cur.fetchall()

    data_equipos_PDF = [
        {
            "tipo": equipo["nombreTipo_equipo"],
            "marca": equipo["nombreMarcaEquipo"],
            "modelo": equipo["nombreModeloequipo"],
            "num_serie": str(equipo["Num_serieEquipo"]),
            "cod_inventario": str(equipo["Cod_inventarioEquipo"])
        }
        for equipo in query
    ]

    # Si todo fue exitoso, confirmar cambios
    cur.execute("COMMIT")
    crear_pdf_devolucion(data_funcionario_PDF, data_equipos_PDF, id_devolucion)
    flash("Devolución de equipos realizada exitosamente", "success")
    return redirect(url_for("asignacion.Asignacion"))


def crear_pdf_devolucion(funcionario, equipos, id_devolucion):
    class PDF(FPDF):
        def header(self):
            #logo
            self.image("static/img/logo_junji.png", 10, 8, 32)
            #font
            self.set_font('times', 'B', 12)
            self.set_text_color(170, 170, 170)
            #Title
            self.cell(0, 30, '', border=False, ln=1, align='L')
            self.cell(0, 5, 'JUNTA NACIONAL DE', border=False, ln=1, align='L')
            self.cell(0, 5, 'JARDINES INFANTILES', border=False, ln=1, align='L')
            self.cell(0, 5, 'Unidad de Inventarios', border=False, ln=1, align='L')
            #line break
            self.ln(10)

        def footer(self):
            self.set_y(-30)
            self.set_font('times', 'B', 12)
            self.set_text_color(170, 170, 170)
            self.cell(0, 0, "", ln=1)
            self.cell(0, 0, "Junta Nacional de Jardines Infantiles - JUNJI", ln=1)
            self.cell(0, 12, "O'Higgins Poniente 77 Concepción. Tel: 412125579", ln=1)
            self.cell(0, 12, "www.junji.cl", ln=1)

    cur = mysql.connection.cursor()

    # 📌 Consultar la fecha de devolución en la base de datos
    cur.execute("""
        SELECT fechaDevolucion
        FROM devolucion
        WHERE idDevolucion = %s
    """, (id_devolucion,))

    devolucion_data = cur.fetchone()

    # Convertir a string para evitar errores con fpdf ademas se cambia el orden de la fecha 
    fecha_devolucion = (
    devolucion_data["fechaDevolucion"].strftime("%d/%m/%Y") if devolucion_data else "FECHA NO DISPONIBLE"
    )
    
    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    titulo = "ACTA de Devolución de Equipo Informático N°" + id_devolucion
    creado_por = "Documento creado por: " + session['user']

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    pdf.cell(0, 10, creado_por, ln=True, align="L")
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la unidad: "
    presentacion22 = "En la fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombre_funcionario = funcionario["nombre"]
    unidad_funcionario = funcionario["unidad"]

    pdf.ln(10)
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(presentacion1)
        cols.ln()
        cols.write(presentacion2)
        cols.ln()
        cols.write(presentacion22)
        cols.ln()
        cols.ln()
        cols.write(presentacion3)
        cols.ln()
        cols.new_column()
        cols.write(nombre_funcionario)
        cols.ln()
        cols.write(unidad_funcionario)
        cols.ln()
        cols.write(fecha_devolucion)  # ✅ Ahora ya no dará error

    pdf.ln(20)
    TABLE_DATA = (
        ("N°", "Tipo equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    i = 0
    for equipo in equipos:
        tipo = equipo["tipo"]
        marca = equipo["marca"]
        modelo = equipo["modelo"]
        num_serie = equipo["num_serie"]
        num_inventario = equipo["cod_inventario"]

        i += 1

        TABLE_DATA = TABLE_DATA + (
            (str(i), tipo, marca, modelo, num_serie, num_inventario),
        )
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)

    pdf.ln(10)
    nombreEncargado = "Nombre del encargado TI:" 
    rutEncargado = "RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre del funcionario:"
    rutMinistro = "RUT:"
    firma = "Firma"
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(nombreEncargado)
        cols.ln()
        cols.ln()
        cols.write(rutEncargado)
        cols.ln()
        cols.ln()
        cols.write(firmaEncargado)
        cols.ln()
        cols.ln()
        cols.ln()
        cols.ln()

        cols.write(nombreMinistro)
        cols.ln()
        cols.ln()
        cols.write(rutMinistro)
        cols.ln()
        cols.ln()
        cols.write(firma)
        cols.ln()
        cols.ln()
        cols.new_column()
        for i in range(0, 3):
            if i == 0:
                cols.write(text= session['user'])
            else:
                cols.write(text="___________________________________")
            cols.ln()
            cols.ln()
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="___________________________________")
            cols.ln()
            cols.ln()
    creado_por = "documento creado por: " + session['user']#! codigo basura????
    #* Definir la ruta donde se almacenarán los PDFs de devoluciones
    ruta_devoluciones = "pdf/devoluciones"
    # Asegurar que la carpeta "pdf/devoluciones" exista
    os.makedirs(ruta_devoluciones, exist_ok=True)
    nombrePdf = "devolucion_" + id_devolucion + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, os.path.join(ruta_devoluciones, nombrePdf))

@asignacion.route("/asignacion/descargar_pdf_devolucion/<id>")
@loguear_requerido
def descargar_pdf_devolucion(id):
    try:
        nombrePDF = "devolucion_" + str(id) + ".pdf"
        file = os.path.join("pdf/devoluciones", nombrePDF)
        return send_file(file, as_attachment=False)
    except:
        flash("Error: No se encontró el PDF", "danger")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/buscar/<idAsignacion>")
@loguear_requerido
def buscar(idAsignacion):
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT  
        a.idAsignacion,
        a.fecha_inicioAsignacion,
        a.observacionAsignacion,
        a.rutaactaAsignacion,
        f.nombreFuncionario,
        a.fechaDevolucion,
        a.ActivoAsignacion
    FROM asignacion a
    INNER JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
    WHERE a.idAsignacion = %s
        """, (idAsignacion,)
    )
    #solo tiene un elemento pero se extraen todas para reusar el html
    Asignaciones = cur.fetchall()

    cur.execute(
        """ SELECT 
            f.rutFuncionario,
            f.nombreFuncionario 
        FROM funcionario f
        ORDER BY f.nombreFuncionario
        """
    )
    funcionarios = cur.fetchall()

    return render_template(
        'GestionR.H/asignacion.html',  
        funcionarios=funcionarios, 
        asignacion=Asignaciones,
        page=1, 
        lastpage=True
    )

@asignacion.route("/asignacion/detalles_json/<idAsignacion>")
@loguear_requerido
def obtener_detalles_asignacion(idAsignacion):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            a.idAsignacion,
            a.fecha_inicioAsignacion,
            d.fechaDevolucion,
            a.ObservacionAsignacion,
            f.rutFuncionario,
            f.nombreFuncionario,
            f.cargoFuncionario,
            te.nombreTipo_equipo,
            mae.nombreMarcaEquipo,
            me.nombreModeloequipo,
            e.Cod_inventarioEquipo,
            e.Num_serieEquipo,
            e.codigoproveedor_equipo,
            e.ObservacionEquipo
        FROM asignacion a
        JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
        JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
        JOIN equipo e ON ea.idEquipo = e.idEquipo
        LEFT JOIN devolucion d ON ea.idEquipoAsignacion = d.idEquipoAsignacion
        JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
        JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
        WHERE a.idAsignacion = %s
        LIMIT 1
    """, (idAsignacion,))
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error": "No se encontró la asignación"}), 404

    return jsonify({
        "asignacion": row
    })


@asignacion.route("/buscar_asignaciones", methods=["GET"])
@loguear_requerido
def buscar_asignaciones():
    query = request.args.get("q", "").lower()  # Obtener el término de búsqueda
    page = request.args.get("page", default=1, type=int)  # Página actual
    per_page = 10  # Número de resultados por página
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # Consulta para buscar asignaciones
    cur.execute(f"""
        SELECT
            a.idAsignacion,
            a.fecha_inicioAsignacion,
            a.ObservacionAsignacion,
            a.ActivoAsignacion,
            f.nombreFuncionario,
            f.cargoFuncionario,
            e.Cod_inventarioEquipo,
            e.Num_serieEquipo,
            te.nombreTipo_equipo
        FROM asignacion a
        JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
        JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
        JOIN equipo e ON e.idEquipo = ea.idEquipo
        JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
        JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE LOWER(f.nombreFuncionario) LIKE %s
           OR LOWER(f.cargoFuncionario) LIKE %s
           OR LOWER(e.Cod_inventarioEquipo) LIKE %s
           OR LOWER(e.Num_serieEquipo) LIKE %s
           OR LOWER(te.nombreTipo_equipo) LIKE %s
           OR LOWER(a.ObservacionAsignacion) LIKE %s
        LIMIT %s OFFSET %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%",
          f"%{query}%", f"%{query}%", per_page, offset))
    asignaciones = cur.fetchall()

    # Total de resultados para la búsqueda
    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM asignacion a
        JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
        JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
        JOIN equipo e ON e.idEquipo = ea.idEquipo
        JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
        JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE LOWER(f.nombreFuncionario) LIKE %s
           OR LOWER(f.cargoFuncionario) LIKE %s
           OR LOWER(e.Cod_inventarioEquipo) LIKE %s
           OR LOWER(e.Num_serieEquipo) LIKE %s
           OR LOWER(te.nombreTipo_equipo) LIKE %s
           OR LOWER(a.ObservacionAsignacion) LIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%",
          f"%{query}%", f"%{query}%"))
    total = cur.fetchone()["total"]
    total_pages = (total + per_page - 1) // per_page

    return jsonify({
        "asignaciones": asignaciones,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    })

@asignacion.route("/asignacion/firmar/<id>", methods=["GET"])
@loguear_requerido
def firmar_asignacion(id):
    if "user" not in session:
        flash("You are NOT authorized")
        return redirect("/ingresar")

    # Ruta de la carpeta donde se almacenan las firmas
    dir_firmas = "pdf/firmas_asignaciones"
    nombreFirmado = None

    # Buscar el archivo firmado relacionado con el ID
    try:
        for filename in os.listdir(dir_firmas):
            if filename.startswith(f"asignacion_{id}_") and filename.endswith("_firmado.pdf"):
                nombreFirmado = filename
                break
    except FileNotFoundError:
        flash("No se encontró la carpeta de firmas", "danger")

    # Renderizar la plantilla con los datos necesarios
    return render_template(
        "GestionR.H/asignacion.modals.html",
        id=id,
        location="asignacion",
        nombreFirmado=nombreFirmado
    )

@asignacion.route("/asignacion/listar_pdf/<idAsignacion>")
@asignacion.route("/asignacion/listar_pdf/<idAsignacion>/<devolver>")
@loguear_requerido
def listar_pdf(idAsignacion, devolver="None"):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    dir = 'pdf'   
    if devolver == "None":
        nombreFirmado = "asignacion_" + str(idAsignacion) + "_" + "firmado.pdf"
        location = "asignacion"
    else:
        nombreFirmado = "devolucion_" + str(idAsignacion) + "_" + "firmado.pdf"

        location = "devolucion"
    #revisa si el archivo esta firmado
    if not os.path.exists(os.path.join("pdf/firmas_asignaciones", nombreFirmado)) and not os.path.exists(os.path.join("pdf/firmas_devoluciones", nombreFirmado)):
        nombreFirmado = "No existen firmas para este documento"

    return render_template(
        'GestionR.H/firma.html', 
        nombreFirmado=nombreFirmado, 
        id=idAsignacion, 
        location=location
        )


#**APARTADO DE FIRMAS**** 

@asignacion.route("/devolucion/mostrar_pdf/<id>/")
@loguear_requerido
def mostrar_pdf_devolucion_firmado(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        nombrePDF = "devolucion_" + str(id) + "_firmado.pdf"
        file = os.path.join("pdf/firmas_devoluciones", nombrePDF)
        return send_file(file, as_attachment=False)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/mostrar_pdf/<id>/")
@loguear_requerido
def mostrar_pdf_asignacion_firmado(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        nombrePDF = "asignacion_" + str(id) + "_firmado.pdf"
        file = os.path.join("pdf/firmas_asignaciones", nombrePDF)
        return send_file(file, as_attachment=False)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))
    


@asignacion.route("/asignacion/firmas_json/<idAsignacion>")
@loguear_requerido
def obtener_firma_json(idAsignacion):
    dir_firmas = "pdf/firmas_asignaciones"
    nombre = f"asignacion_{idAsignacion}_firmado.pdf"
    ruta = os.path.join(dir_firmas, nombre)

    if os.path.exists(ruta):
        return jsonify({"existe": True, "nombre": nombre})
    else:
        return jsonify({"existe": False})


@asignacion.route("/asignacion/adjuntar_pdf/<idAsignacion>", methods=["POST"])
@administrador_requerido
def adjuntar_pdf_asignacion(idAsignacion):
    if "user" not in session:
        flash("You are NOT authorized")
        return redirect("/ingresar")

    # Obtener el archivo
    file = request.files["archivoFirma"]

    # Definir la carpeta donde se guardará el archivo
    dir = "pdf/firmas_asignaciones" if inLinux else "app/pdf/firmas_asignaciones"

    # Crear la carpeta si no existe
    os.makedirs(dir, exist_ok=True)

    # Nombre del archivo que debe eliminarse si ya existe
    filenameToDelete = f"asignacion_{idAsignacion}_firmado.pdf"
    filenameToDelete = secure_filename(filenameToDelete)

    # Verificar si el archivo ya existe y eliminarlo
    file_path = os.path.join(dir, filenameToDelete)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Guardar el nuevo archivo con un nombre seguro
    sfilename = secure_filename(file.filename)
    temp_file_path = os.path.join(dir, sfilename)
    file.save(temp_file_path)

    # Renombrar el archivo al formato correcto
    new_file_path = os.path.join(dir, f"asignacion_{idAsignacion}_firmado.pdf")
    os.rename(temp_file_path, new_file_path)

    flash("Se subió la firma correctamente")
    return redirect(url_for("asignacion.Asignacion"))


@asignacion.route("/asignacion/firmas_devolucion_json/<idDevolucion>")
@loguear_requerido
def obtener_firma_devolucion_json(idDevolucion):
    dir_firmas = "pdf/firmas_devoluciones"
    nombre = f"devolucion_{idDevolucion}_firmado.pdf"
    ruta = os.path.join(dir_firmas, nombre)

    if os.path.exists(ruta):
        return jsonify({"existe": True, "nombre": nombre})
    else:
        return jsonify({"existe": False})


@asignacion.route("/devolucion/adjuntar_pdf/<idAsignacion>", methods=["POST"])
@administrador_requerido
def adjuntar_pdf_devolucion(idAsignacion):
    # Definir la carpeta donde se guardará el archivo
    dir = "pdf/firmas_devoluciones"

    # Crear la carpeta si no existe
    os.makedirs(dir, exist_ok=True)

    # Nombre del archivo que debe eliminarse si ya existe
    filenameToDelete = f"devolucion_{idAsignacion}_firmado.pdf"
    file_path = os.path.join(dir, filenameToDelete)

    # Verificar si el archivo ya existe y eliminarlo
    if os.path.exists(file_path):
        os.remove(file_path)

    # Obtener el archivo desde la solicitud
    file = request.files.get("archivoFirma")

    # Guardar el archivo con un nombre seguro
    sfilename = secure_filename(file.filename)
    temp_file_path = os.path.join(dir, sfilename)
    file.save(temp_file_path)

    # Renombrar el archivo al formato correcto
    new_file_path = os.path.join(dir, f"devolucion_{idAsignacion}_firmado.pdf")
    os.rename(temp_file_path, new_file_path)

    return redirect(url_for("asignacion.Asignacion"))
