from flask import request, flash, render_template, url_for, redirect, Blueprint, session, send_file
from db import mysql
from funciones import getPerPage
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill
from cuentas import loguear_requerido, administrador_requerido
from werkzeug.utils import secure_filename
from cerberus import Validator
from MySQLdb import IntegrityError

import os

equipo = Blueprint("equipo", __name__, template_folder="app/templates")


# envia datos al formulario y tabla de equipo CAMBIA FK_IDCODIGO_PROVEEDOR
@equipo.route("/equipo")
@equipo.route("/equipo/<page>")
@loguear_requerido
def Equipo(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (int(page) - 1) * perpage
    #solo funciona con connect no con connect
    #si funciona con connection. parece que era algo de la maquina virtual
    #elimine la maquina virtual y ahora funciona
    cur = mysql.connection.cursor() #ahora connect funciona pero no connection ¿?
    cur.execute("SELECT COUNT(*) FROM equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])
    cur.execute(""" 
    SELECT *
    FROM super_equipo
    LIMIT %s OFFSET %s

    """,(
            perpage, offset
        )
    )
    equipos = cur.fetchall()
    print(equipos)
    modelos_por_tipo = cur.fetchall()
    cur.execute("SELECT * FROM tipo_equipo")
    tipo_equipo = cur.fetchall()
    cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    _data = cur.fetchall()
    cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
    ubi_data = cur.fetchall()
    cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    ordenc_data = cur.fetchall()
    cur.execute("""
    SELECT *
    FROM marca_equipo
                """)
    marcas = cur.fetchall()
    #print(marcas)

    modelos_por_tipo = {

    }
    for tipo in tipo_equipo:
        cur.execute("""
        SELECT *
        FROM modelo_equipo me
        WHERE me.idTipo_Equipo = %s
            """, (tipo['idTipo_equipo'],))
        modelo_tipo = cur.fetchall()
        modelos_por_tipo[tipo['idTipo_equipo']] = modelo_tipo
    #print("modelos por tipo")
    #print(modelos_por_tipo)

    #print("tipos de equipo ############")
    #print(tipoe_data)
    cur.execute("""
        SELECT *
        FROM modelo_equipo
                """)
    modelo_equipo = cur.fetchall()
    cur.close()

    marcas_llenadas = crear_lista_modelo_tipo_marca()
    return render_template(
        "equipo.html",
        equipo=equipos,
        tipo_equipo=tipo_equipo,
        modelo_equipo_simple = modelo_equipo,
        marcas_equipo=marcas_llenadas,
        orden_compra=ordenc_data,
        Unidad=ubi_data,
        modelo_equipo=modelos_por_tipo,
        page=page,
        lastpage=page < (total / perpage) + 1,
        session=session
    )
def crear_lista_modelo_tipo_marca():
    #Va a ser de tipo 
    #[
    #   {
    #       llave_marca: dato_marca, ..., tipos_equipo: {
    #           llave_tipo_equipo: dato_tipo_equipo, ..., modelos_equipo: {
    #               llave_modelo: dato_modelo, ...
    #           }
    #       }
    #   }
    #]
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT *
    FROM marca_equipo
                """)
    marcas = cur.fetchall()
    marcas_llenadas = []
    for i in range(0, len(marcas)):
        tipos_llenados = []
        marca = marcas[i]
        cur.execute("""
            SELECT *
            FROM tipo_equipo te
            INNER JOIN marca_tipo_equipo mte ON mte.idTipo_equipo = te.idTipo_equipo
            WHERE mte.idMarca_Equipo = %s
            """, (marca['idMarca_Equipo'],))
        tipos_equipo_asociados_marca = cur.fetchall()
        for j in range(0, len(tipos_equipo_asociados_marca)):
            tipo = tipos_equipo_asociados_marca[j]
            cur.execute("""
            SELECT *
            FROM modelo_equipo me
            WHERE me.idTipo_equipo = %s
            AND me.idMarca_Equipo = %s
                        """, (tipo['idTipo_equipo'], marca['idMarca_Equipo']))
            modelos_equipo_asociados_tipo = cur.fetchall()
            tipo.update({'modelo_equipo': modelos_equipo_asociados_tipo})
            tipos_llenados.append(tipo)        
        tipos_llenados = tuple(tipos_llenados)
        marca.update({'tipo_equipo': tipos_llenados})
        marcas_llenadas.append(marca)
    marcas_llenadas = tuple(marcas_llenadas)
    #print("marcas_llenadas")
    #print(marcas_llenadas)
    return marcas_llenadas


    #añadir tipos a marca


    pass
# agrega registro para id
@equipo.route("/add_equipo", methods=["POST"])
def add_equipo():
    if request.method == "POST":
        datos = {
            'codigo_inventario' : request.form["codigo_inventario"],
            'numero_serie' : request.form["numero_serie"],
            'observacion_equipo' : request.form["observacion_equipo"],
            'codigoproveedor' : request.form["codigoproveedor"],
            'mac' : request.form["mac"],
            'imei' : request.form["imei"],
            'numero' : request.form["numero"],
            #nombre_tipo_equipo : request.form["nombre_tipo_equipo"]
            #nombre_estado_equipo : request.form["nombre_estado_equipo"]
            'codigo_Unidad' : request.form["codigo_Unidad"],
            'nombre_orden_compra' : request.form["nombre_orden_compra"],
            'idModelo_equipo' : request.form["modelo_equipo"],
        }

                # Definir el esquema de validación
        schema = { 
            'codigo_inventario': {'type': 'string', 'regex': '^[a-zA-Z0-9]+$'}, 
            'numero_serie': {'type': 'string', 'regex': '^[a-zA-Z0-9]+$'}, 
            'observacion_equipo': {'type': 'string', 'nullable': True}, 
            'codigoproveedor': {'type': 'string', 'regex': '^[a-zA-Z0-9]+$'}, 
            'mac': {'type': 'string', 'regex': '^[0-9]+$'}, 
            'imei': {'type': 'string', 'regex': '^[0-9]+$'}, 
            'numero': {'type': 'string', 'regex': '^[0-9]+$'}, 
            'codigo_Unidad': {'type': 'string', 'nullable': True}, 
            'nombre_orden_compra': {'type': 'string', 'nullable': True}, 
            'idModelo_equipo': {'type': 'string', 'nullable': True},
            }

        #validator
        v = Validator(schema)

        # Validar los datos usando Cerberus
        if not v.validate(datos):
            flash("Caracteres no permitidos")
            return redirect(url_for("equipo.Equipo"))


        #TODO: Muchos select tienen el mismo nombre y esto provoca un error
        #no recuerdo si resolvi la linea anterior
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """ INSERT INTO equipo (
                    Cod_inventarioEquipo, 
                    Num_serieEquipo, 
                    ObservacionEquipo,
                    codigoproveedor_equipo,
                    macEquipo,
                    imeiEquipo, 
                    numerotelefonicoEquipo, 
                    idEstado_Equipo, 
                    idUnidad, 
                    idOrden_compra, 
                    idModelo_equipo) 
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s)
            """,
                (
                   datos['codigo_inventario'],
                   datos ['numero_serie'],
                    datos['observacion_equipo'],
                    datos['codigoproveedor'],
                    datos['mac'],
                   datos ['imei'],
                   datos ['numero'],
                    3,
                   datos ['codigo_Unidad'],
                  datos  ['nombre_orden_compra'],
                   datos ['idModelo_equipo'],
                ),
            )
            mysql.connection.commit()
            flash("Equipo agregado correctamente")
            return redirect(url_for("equipo.Equipo"))
        except IntegrityError as e:
            mensaje_error = str(e)
            if "Duplicate entry" in mensaje_error:
                if "PRIMARY" in mensaje_error:
                    flash("El código de inventario ya existe")
                elif "UNIQUE" in mensaje_error:
                    flash("El número de serie ya existe")
                else:
                    flash("Error de duplicacion en la base de datos")
            else:
                flash("Error de integridad en la base de datos")
            return redirect(url_for('equipo.Equipo'))
        
        except Exception as e:
            flash(f"Error al crear el equipo: {str(e)}")
            return redirect(url_for('equipo.Equipo'))
        
# envia datos al formulario editar segun id
@equipo.route("/edit_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """ 
           SELECT *
        FROM equipo e
        INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
        INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
        INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
        INNER JOIN unidad u on u.idUnidad = e.idUnidad
        INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
        WHERE idEquipo = %s
        """,
            (id,),
        )
        data = cur.fetchall()
        cur.execute("SELECT * FROM tipo_equipo")
        tipoe_data = cur.fetchall()
        cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
        estadoe_data = cur.fetchall()
        cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
        ubi_data = cur.fetchall()
        cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
        ordenc_data = cur.fetchall()
        cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
        modeloe_data = cur.fetchall()
        return render_template(
            "editEquipo.html",
            equipo=data[0],
            tipo_equipo=tipoe_data,
            estado_equipo=estadoe_data,
            orden_compra=ordenc_data,
            Unidad=ubi_data,
            modelo_equipo=modeloe_data,
        )
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for("equipo.Equipo"))
# actualiza registro a traves de id correspondiente
@equipo.route("/update_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == "POST":
        datos = {
            'codigo_inventario': request.form["codigo_inventario"],
            'numero_serie': request.form["numero_serie"],
            'observacion_equipo': request.form["observacion_equipo"],
            'codigoproveedor': request.form["codigoproveedor"],
            'mac': request.form["mac"],
            'imei': request.form["imei"],
            'numero': request.form["numero"],
            'nombre_estado_equipo': request.form["nombre_estado_equipo"],
            'codigo_Unidad': request.form["codigo_Unidad"],
            'nombre_orden_compra': request.form["nombre_orden_compra"],
            'nombre_modelo_equipo': request.form["nombre_modelo_equipo"],
        }

        schema = {
            'codigo_inventario': {'type': 'string', 'regex': '^[a-zA-Z0-9]+$'},
            'numero_serie': {'type': 'string', 'regex': '^[a-zA-Z0-9]+$'},
            'observacion_equipo': {'type': 'string', 'nullable': True},
            'codigoproveedor': {'type': 'string', 'regex': '^[a-zA-Z0-9]+$'},
            'mac': {'type': 'string', 'regex': '^[0-9]+$'},
            'imei': {'type': 'string', 'regex': '^[0-9]+$'},
            'numero': {'type': 'string', 'regex': '^[0-9]+$'},
            'nombre_estado_equipo': {'type': 'string'},
            'codigo_Unidad': {'type': 'string', 'nullable': True},
            'nombre_orden_compra': {'type': 'string', 'nullable': True},
            'nombre_modelo_equipo': {'type': 'string', 'nullable': True},
        }


        v = Validator(schema)
        # Validación de caracteres no permitidos
        if not v.validate(datos):
            flash("Caracteres no permitidos")
            return redirect(url_for("equipo.Equipo"))

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
                UPDATE equipo
                SET Cod_inventarioEquipo = %s,
                    Num_serieEquipo = %s,
                    ObservacionEquipo = %s,
                    codigoproveedor_equipo = %s,
                    macEquipo = %s,
                    imeiEquipo = %s,
                    numerotelefonicoEquipo = %s,
                    idUnidad = %s,
                    idOrden_compra = %s,
                    idModelo_equipo = %s
                WHERE idEquipo = %s
                """,
                (
                    datos['codigo_inventario'],
                    datos['numero_serie'],
                    datos['observacion_equipo'],
                    datos['codigoproveedor'],
                    datos['mac'],
                    datos['imei'],
                    datos['numero'],
                    datos['nombre_estado_equipo'],
                    datos['codigo_Unidad'],
                    datos['nombre_orden_compra'],
                    datos['nombre_modelo_equipo'],
                    id,
                ),
            )
            mysql.connection.commit()
            flash("Equipo actualizado correctamente")
            return redirect(url_for("equipo.Equipo"))
        except Exception as error:
            flash(f"Error al actualizar el equipo: {str(error)}")
            return redirect(url_for("equipo.Equipo"))
        

# elimina registro a traves de id correspondiente
@equipo.route("/delete_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM equipo WHERE idEquipo = %s", (id,))
        mysql.connection.commit()
        flash("Equipo eliminado correctamente")
        return redirect(url_for("equipo.Equipo"))
    except Exception as e:
        flash("Error al Eliminar, equipo puede tener dependencias")
        #flash(e.args[1])
        return redirect(url_for("equipo.Equipo"))


@equipo.route("/mostrar_asociados_traslado/<idTraslado>")
@loguear_requerido
def mostrar_asociados_traslado(idTraslado):
    page = 1
    perpage = 200
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])
    cur.execute(
        """ 
    SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, e.ObservacionEquipo, 
    e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, e.numerotelefonicoEquipo,
    e.idEstado_Equipo, e.idUnidad, e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, 
    te.nombreTipo_Equipo, ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
    moe.idModelo_equipo, moe.nombreModeloequipo
    FROM equipo e
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    INNER JOIN traslacion tras on tras.idEquipo = e.idEquipo
    WHERE tras.idTraslado = %s
    LIMIT %s OFFSET %s
    """,
        (idTraslado, perpage, offset),
    )
    data = cur.fetchall()
    cur.execute("SELECT * FROM tipo_equipo")
    tipoe_data = cur.fetchall()
    cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    estadoe_data = cur.fetchall()
    cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
    ubi_data = cur.fetchall()
    cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    ordenc_data = cur.fetchall()
    cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
    modeloe_data = cur.fetchall()

    return render_template(
        "equipo.html",
        equipo=data,
        tipo_equipo=tipoe_data,
        estado_equipo=estadoe_data,
        orden_compra=ordenc_data,
        Unidad=ubi_data,
        modelo_equipo=modeloe_data,
        page=page,
        lastpage=False,
    )


@equipo.route("/mostrar_asociados_unidad/<idUnidad>")
@equipo.route("/mostrar_asociados_unidad/<idUnidad>/<page>")
@loguear_requerido
def mostrar_asociados_unidad(idUnidad, page=1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    page = int(page)
    page = 1
    perpage = 200  # getPerPage()
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])
    cur.execute(
        """ 
    SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, e.ObservacionEquipo, 
    e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, e.numerotelefonicoEquipo,
    e.idEstado_Equipo, e.idUnidad, e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, 
    te.nombreTipo_Equipo, ee.idEstado_equipo, ee.nombreEstado_equipo, 
    u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
    moe.idModelo_equipo, moe.nombreModeloequipo
    FROM equipo e
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    WHERE e.idUnidad = %s
    LIMIT %s OFFSET %s
    """,
        (
            idUnidad,
            perpage,
            offset,
        ),
    )
    data = cur.fetchall()
    cur.execute("SELECT * FROM tipo_equipo")
    tipoe_data = cur.fetchall()
    cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    estadoe_data = cur.fetchall()
    cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
    ubi_data = cur.fetchall()
    cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    ordenc_data = cur.fetchall()
    cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
    modeloe_data = cur.fetchall()

    return render_template(
        "equipo.html",
        equipo=data,
        tipo_equipo=tipoe_data,
        estado_equipo=estadoe_data,
        orden_compra=ordenc_data,
        Unidad=ubi_data,
        modelo_equipo=modeloe_data,
        page=page,
        lastpage=False,
    )

@equipo.route("/mostrar_asociados_funcionario/<rutFuncionario>")
@equipo.route("/mostrar_asociados_funcionario/<rutFuncionario>/<page>")
@loguear_requerido
def mostrar_asociados_funcionario(rutFuncionario, page=1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tipo_equipo")
    tipoe_data = cur.fetchall()
    cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    estadoe_data = cur.fetchall()
    cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
    ubi_data = cur.fetchall()
    cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    ordenc_data = cur.fetchall()
    cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
    modeloe_data = cur.fetchall()

    page = int(page)
    page = 1
    perpage = 200 #porque ningun funcionario tendra tantos 
                    #equipos que la paginacion sea nesesaria
    offset = (page - 1) * perpage
    cur.execute("SELECT COUNT(*) FROM equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])
    #encontar la fecha de la ultima asignacion
    cur.execute("""
                SELECT *
                FROM asignacion a
                WHERE a.rutFuncionario = %s
                AND a.ActivoAsignacion = 1
                ORDER BY a.fecha_inicioAsignacion DESC
                """, (rutFuncionario,))
    asignaciones = cur.fetchall()
    print("########################")
    print(asignaciones)
    if(len(asignaciones) == 0):
        
        return render_template(
            "equipo.html",
            equipo=(),
            tipo_equipo=tipoe_data,
            estado_equipo=estadoe_data,
            orden_compra=ordenc_data,
            Unidad=ubi_data,
            modelo_equipo=modeloe_data,
            page=page,
            lastpage=False,
        )
    ultimaAsignacion = asignaciones[0]
    primeraAsignacion = asignaciones[-1] #-1 deberia dar el ultimo elemento

    cur.execute(""" 
    SELECT *
    FROM equipo e
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    INNER JOIN equipo_asignacion ea on ea.idEquipo = e.idEquipo
    INNER JOIN asignacion a on a.idAsignacion = ea.idAsignacion
    INNER JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
    INNER JOIN unidad u on u.idUnidad = e.idUnidad
    WHERE a.idAsignacion = %s AND f.rutFuncionario = %s
    LIMIT %s OFFSET %s
    """,
        (
            ultimaAsignacion['idAsignacion'],
            rutFuncionario,
            perpage,
            offset,
        ),
    )
    data = cur.fetchall()
    return render_template(
        "equipo.html",
        equipo=data,
        tipo_equipo=tipoe_data,
        estado_equipo=estadoe_data,
        orden_compra=ordenc_data,
        Unidad=ubi_data,
        modelo_equipo=modeloe_data,
        page=page,
        lastpage=False,
    )


@equipo.route("/equipo_detalles/<idEquipo>")
@loguear_requerido
def equipo_detalles(idEquipo):
    cur = mysql.connection.cursor()
    #Como funcionaria con la asignacion cambiada ¿?
    #Cuando se añadan las asignaciones y devoluciones agregar funcionario como nombre
    #TODO: Revisar que hacer con las observaciones de Traslado, 
    #Revisar que hacer con observacion de Devolucion
    cur.execute("""
                SELECT i.fechaIncidencia as fecha, i.idIncidencia as id,
                    "Incidencia" as evento, i.observacionIncidencia as observacion,
                    i.nombreIncidencia as nombre
                FROM incidencia i
                WHERE i.idEquipo = %s
                UNION ALL
                SELECT traslado.fechaTraslado, traslado.idTraslado, "Traslado",
                    "Nombre", "observacion"
                FROM traslado, traslacion
                WHERE traslacion.idTraslado = traslado.idTraslado AND traslacion.idEquipo = %s
                UNION ALL
                SELECT a.fecha_inicioAsignacion, a.idAsignacion, "Asignacion",
                    a.ObservacionAsignacion, f.nombreFuncionario 
                FROM asignacion a
                INNER JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
                INNER JOIN equipo_asignacion ea on a.idAsignacion = ea.idAsignacion
                WHERE ea.idEquipo = %s
                UNION ALL
                SELECT a.fechaDevolucion, a.idAsignacion, "Devolucion",
                    a.ObservacionAsignacion, f.nombreFuncionario
                FROM asignacion a
                INNER JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
                INNER JOIN equipo_asignacion ea on a.idAsignacion = ea.idAsignacion
                WHERE ea.idEquipo = %s
                ORDER BY fecha DESC
                """, (idEquipo, idEquipo, idEquipo, idEquipo))
    data_eventos = cur.fetchall()
    #cur.execute(
        #"""
                #SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, 
                #e.ObservacionEquipo, e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, 
                #e.numerotelefonicoEquipo,e.idEstado_Equipo, e.idUnidad, 
                #e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, te.nombreTipo_Equipo, 
                #ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad, u.nombreUnidad, 
                #oc.idOrden_compra, oc.nombreOrden_compra,
    #moe.idModelo_equipo, moe.nombreModeloequipo
    #FROM equipo e
    #INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    #INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
    #INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    #INNER JOIN unidad u on u.idUnidad = e.idUnidad
    #INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    #WHERE e.idEquipo = %s
                #""",(idEquipo))
    cur.execute("""
    SELECT *
    FROM super_equipo se
    WHERE se.idEquipo = %s
    """, (idEquipo,)
    )
    data_equipo = cur.fetchone()
    #revisar si este equipo esta asignado a un funcionario
    if data_equipo['nombreFuncionario'] != '':
        cur.execute("""
        SELECT *
        FROM funcionario f
        INNER JOIN unidad u ON u.idUnidad = f.idUnidad
        WHERE f.rutFuncionario = %s
        """, (data_equipo['rutFuncionario'],))
        funcionario = cur.fetchone()
    else:
        funcionario = None

    return render_template("equipo_detalles.html", equipo=data_equipo, eventos=data_eventos, funcionario=funcionario)

#
    #cur.execute("""
            #SELECT *
            #FROM (
                #SELECT *
                #FROM asignacion
                #WHERE asignacion.idEquipo = %s 
            #)
            #LEFT OUTER JOIN (
                #SELECT *
                #FROM devolucion
                #WHERE devolucion.idEquipo = %s
            #)
            #LEFT OUTER JOIN (
                #SELECT *
                #FROM incidencia
                #WHERE incidencia.idEquipo = %s
            #)
            #LEFT OUTER JOIN (

            #)
                #""")
@equipo.route("/test_excel_form", methods=["POST"])
@loguear_requerido
def test_excel_form():
    #para el uso de la pagina de otros
    tipos = ("aio", "notebook", "impresoras", "bam", "proyectores", "telefonos", "disco_duro",
             "tablets")
    todo_check = request.form.get('todo_check')
    #si se imprime todo en una hoja usar la funcion ya creada
    if(todo_check == "on"):
        print("test")
        return crear_excel()
    #de lo contrario imprimir cada hoja individualmente
    computadora_check = request.form.get('AIO_check')
    notebooks_check = request.form.get('Notebooks')
    impresoras_check = request.form.get('impresoras_check')
    bam_check = request.form.get('bam_check')
    proyectores_check = request.form.get('proyectores_check')
    telefonos_check = request.form.get('telefonos_check')
    HDD_check = request.form.get('HDD_check')
    tablets_check = request.form.get('tablets_check')
    otros_check = request.form.get('otros_check')
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
    #al ser otro requiere una consulta distinta ya que tendria que ser distinto a
    #todas las categorias anteriores
    if otros_check == "on":
        print("otros")
        ws.title = "Otros"
        añadir_hoja_de_otros(tipos, ws)
        ws = wb.create_sheet("sheet")
    
        wb.save("test_exportados.xlsx")
        return send_file('test_exportados.xlsx', as_attachment=True)
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
        """.format(tipos[i]) 
        if(i != len(tipos) - 1):
            query += " AND "
    cur.execute(query)
    equipo_data = cur.fetchall()

    encabezado = (["Provincia", "Comuna", "Modalidad", "Codigo Proveedor", "Nombre", "Tipo de Bien", "Marca", "Modelo", 
               "N° Serie", "Codigo Inventario", "Nombre Proveedor"])
    print("encabezado len: " +  str(len(encabezado)))
    print(encabezado[10])
    for i in range(0, len(encabezado)):
        print(i)
        char = chr(65 + i)
        ws[char + str(1)].fill = PatternFill(start_color="000ff000", fill_type = "solid")
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
        #65 = A en ASCII
        #consegir lista de valores y extraer la lista de valires en cada for interior
        fillCell(equipo_data[fila]['nombreProvincia'], fila + 2)
        fillCell(equipo_data[fila]['nombreComuna'], fila + 2)
        fillCell(equipo_data[fila]['nombreModalidad'], fila + 2)
        fillCell(equipo_data[fila]['codigoproveedor_equipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreUnidad'], fila + 2)
        fillCell(equipo_data[fila]['tipo_equipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreMarcaEquipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreModeloequipo'], fila + 2)
        fillCell(equipo_data[fila]['Num_serieEquipo'], fila + 2)
        fillCell(equipo_data[fila]['Cod_inventarioEquipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreProveedor'], fila + 2)



    pass


def añadir_hoja_de_tipo(tipo, ws):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute(""" 
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
                """, (tipo,))
    equipo_data = cur.fetchall()

    encabezado = (["Provincia", "Comuna", "Modalidad", "Codigo Proveedor", "Nombre", 
                   "CodigoUnidad","Tipo de Bien", "Marca", "Modelo", 
               "N° Serie", "Codigo Inventario", "Nombre Proveedor"])
    for i in range(0, len(encabezado)):
        char = chr(65 + i)
        ws[char + str(1)].fill = PatternFill(start_color="000ff000", fill_type = "solid")
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
        #65 = A en ASCII
        #consegir lista de valores y extraer la lista de valires en cada for interior
        fillCell(equipo_data[fila]['nombreProvincia'], fila + 2)
        fillCell(equipo_data[fila]['nombreComuna'], fila + 2)
        fillCell(equipo_data[fila]['nombreModalidad'], fila + 2)
        fillCell(equipo_data[fila]['codigoproveedor_equipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreUnidad'], fila + 2)
        fillCell(equipo_data[fila]['idUnidad'], fila + 2)
        fillCell(equipo_data[fila]['tipo_equipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreMarcaEquipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreModeloequipo'], fila + 2)
        fillCell(equipo_data[fila]['Num_serieEquipo'], fila + 2)
        fillCell(equipo_data[fila]['Cod_inventarioEquipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreProveedor'], fila + 2)



    #ingresar datos
    return
#exportar a pdf
@equipo.route("/equipo/crear_excel")
@loguear_requerido
def crear_excel():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    #buscar columnas
    wb = Workbook()
    ws = wb.active

    #consulta datos
    cur = mysql.connection.cursor()
    cur.execute(""" 
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
    """)
    equipo_data = cur.fetchall()

    #generar encabezado
    #encabezado

    encabezado = (["Provincia", "Comuna", "Modalidad", "Codigo Proveedor", "Nombre", "Tipo de Bien", "Marca", "Modelo", 
               "N° Serie", "Codigo Inventario", "Nombre Proveedor"])
    for i in range(0, len(encabezado)):
        char = chr(65 + i)
        ws[char + str(1)].fill = PatternFill(start_color="000ff000", fill_type = "solid")
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
        #65 = A en ASCII
        #consegir lista de valores y extraer la lista de valires en cada for interior
        fillCell(equipo_data[fila]['nombreProvincia'], fila + 2)
        fillCell(equipo_data[fila]['nombreComuna'], fila + 2)
        fillCell(equipo_data[fila]['nombreModalidad'], fila + 2)
        fillCell(equipo_data[fila]['codigoproveedor_equipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreUnidad'], fila + 2)
        fillCell(equipo_data[fila]['nombreTipo_equipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreMarcaEquipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreModeloequipo'], fila + 2)
        fillCell(equipo_data[fila]['Num_serieEquipo'], fila + 2)
        fillCell(equipo_data[fila]['Cod_inventarioEquipo'], fila + 2)
        fillCell(equipo_data[fila]['nombreProveedor'], fila + 2)




    #ingresar datos
    wb.save("datos_exportados.xlsx")
    return send_file('datos_exportados.xlsx', as_attachment=True)

def crear_pagina_todojunto(wb):
    return wb

@equipo.route("/equipo/importar_excel", methods=["POST"])
@administrador_requerido
def importar_excel():
    #Nesesito el excel para ver el formato
    file = request.files["file"]
    path = ""
    safename = secure_filename(file.filename)
    file.save(os.path.join(path, safename))
    wb = load_workbook(os.path.join(path, safename))
    ws = wb['Equipo']
    importar_equipo(col_codigo_inventario='A', 
                    col_n_serie='B', 
                    col_codigo_proveedor='C', 
                    col_mac='D', 
                    col_imei='E', 
                    col_telefono='F', 
                    col_idUnidad='G', 
                    col_modelo='H', 
                    col_tipo_equipo='I',
                    col_marca='J', 
                    col_id_orden_compra='P',
                    col_nombre_orden_compra='K', 
                    col_fecha_inicio_compra='O',
                    col_fecha_fin_compra='L',
                    col_tipo_adquisicion='M',
                    col_proveedor='N',
                    
                    worksheet=ws)
    return redirect("/equipo")

@equipo.route("/equipo/importar_excel/unidad", methods=["POST"])
@administrador_requerido
def importar_excel_unidad():
    #Nesesito el excel para ver el formato
    file = request.files["file"]
    path = ""
    safename = secure_filename(file.filename)
    file.save(os.path.join(path, safename))
    wb = load_workbook(os.path.join(path, safename))
    ws = wb['Unidad']
    importar_unidad(col_comuna='E',
                    col_modalidad='F', 
                    col_codigo='A', 
                    col_contacto='C', 
                    col_nombre='B', 
                    col_direccion='D', 
                    worksheet=ws)
    #TODO: delete file
    return redirect("/equipo")
    


def importar_equipo(col_codigo_inventario, col_n_serie, col_codigo_proveedor, 
                    col_mac, col_imei, col_telefono, col_idUnidad, col_modelo,
                    col_tipo_equipo, col_marca, col_id_orden_compra,
                    col_nombre_orden_compra, col_fecha_inicio_compra,
                    col_fecha_fin_compra, col_tipo_adquisicion,
                    col_proveedor, worksheet):
    print("importar equipos")
    

    for row in range(2, worksheet.max_row+1):
        codigo_inventario = worksheet[col_codigo_inventario + str(row)].value
        n_serie = worksheet[col_n_serie + str(row)].value
        codigo_proveedor = worksheet[col_codigo_proveedor + str(row)].value
        mac = worksheet[col_mac + str(row)].value
        imei = worksheet[col_imei + str(row)].value
        telefono = worksheet[col_telefono + str(row)].value
        idUnidad = worksheet[col_idUnidad + str(row)].value
        modelo = worksheet[col_modelo + str(row)].value
        nombre_tipo = worksheet[col_tipo_equipo + str(row)].value
        nombre_marca = worksheet[col_marca + str(row)].value
        id_orden_compra = worksheet[col_id_orden_compra + str(row)].value
        nombre_orden_compra = worksheet[col_nombre_orden_compra + str(row)].value
        fecha_inicio_compra = worksheet[col_fecha_inicio_compra + str(row)].value
        fecha_fin_compra = worksheet[col_fecha_fin_compra + str(row)].value
        nombre_tipo_adquisicion = worksheet[col_tipo_adquisicion + str(row)].value
        nombre_proveedor = worksheet[col_proveedor + str(row)].value

        cur = mysql.connection.cursor()

        #nombre orden de compra
        if(nombre_orden_compra != None):
            cur.execute("""
            SELECT *
            FROM orden_compra oo
            WHERE LOWER(oo.idOrden_compra) LIKE LOWER(%s)
            """, (id_orden_compra,))
            tupla_orden_compra = cur.fetchall()
            print('tupla_orden_compra')
            print(tupla_orden_compra)
            print(len(tupla_orden_compra))
            if(len(tupla_orden_compra) == 0):
                #revisar proveedor
                cur.execute("""
                SELECT *
                FROM tipo_adquisicion ta
                WHERE LOWER(ta.nombreTipo_adquisicion) LIKE LOWER(%s)
                """, (nombre_tipo_adquisicion,))
                tupla_adquisicion = cur.fetchall()
                idTipo_adquisicion = ""
                if(len(tupla_adquisicion) == 0):
                    cur.execute("""
                    INSERT INTO tipo_adquisicion(nombreTipo_adquisicion)
                    VALUES (%s)
                    """, (nombre_tipo_adquisicion,))
                    mysql.connection.commit()
                    idTipo_adquisicion = cur.lastrowid
                else:
                    idTipo_adquisicion = tupla_adquisicion[0]['idTipo_adquisicion']

                #revisar tipo adquisicion

                cur.execute("""
                SELECT *
                FROM proveedor p
                WHERE LOWER(p.nombreProveedor) = LOWER(%s)
                """, (nombre_proveedor,))
                tupla_proveedor = cur.fetchall()
                idProveedor = ""
                if(len(tupla_proveedor) == 0):
                    cur.execute("""
                    INSERT INTO proveedor
                    (nombreProveedor)
                    VALUES (%s)
                    """, (nombre_proveedor,))
                    mysql.connection.commit()
                    idProveedor = cur.lastrowid
                else:
                    idProveedor = tupla_proveedor[0]['idProveedor']


                print("id_orden_compra")
                print(id_orden_compra)
                #crear orden de compra
                cur.execute("""
                INSERT INTO orden_compra
                (idOrden_compra ,nombreOrden_compra, fechacompraOrden_compra,
                fechafin_ORDEN_COMPRA, idTipo_adquisicion,
                            idProveedor)
                VALUES(%s, %s, %s,
                        %s, %s,
                            %s)
                            """,(id_orden_compra, nombre_orden_compra, fecha_inicio_compra,
                                fecha_fin_compra, idTipo_adquisicion, idProveedor))
                mysql.connection.commit()
            else:
                id_orden_compra = tupla_orden_compra[0]['idOrden_compra']
        else:
            id_orden_compra = None
        #buscar modelo con un nombre igual

        print("id_orden_equipo")
        print(id_orden_compra)

        cur.execute("""
        SELECT me.idModelo_Equipo
        FROM modelo_equipo me
        WHERE LOWER(me.nombreModeloequipo) = LOWER(%s)
                    """, (modelo,))
        
        id_modelo_equipo = ""
        tupla_modelo = cur.fetchall()
        if(len(tupla_modelo) == 0):
            #insertar el modelo

            Ids = encontrar_o_crear_tipo_equipo(nombre_tipo, cur, nombre_marca)
            id_tipo_equipo = Ids[0]
            id_marca_equipo = Ids[1]

            print("insert modelo")
            cur.execute("""
            INSERT INTO modelo_equipo
                (nombreModeloequipo,
                idTipo_Equipo,
                idMarca_Equipo)
            VALUES (%s, %s, %s)
                """, (modelo, id_tipo_equipo, id_marca_equipo))
                #commit
            mysql.connection.commit()
            id_modelo_equipo = cur.lastrowid
        else:
            id_modelo_equipo = tupla_modelo[0]['idModelo_Equipo']

        #buscar id de SIN ASIGNAR
        cur.execute("""
        SELECT idEstado_equipo
        FROM estado_equipo
        WHERE LOWER(nombreEstado_equipo) LIKE LOWER(%s)
        """, ("SIN ASIGNAR",))
        idEstado_equipo = cur.fetchone()['idEstado_equipo']

        print("insertar equipo")
        cur.execute("""
        INSERT INTO equipo 
                (Cod_inventarioEquipo,
                Num_serieEquipo,
                ObservacionEquipo,
                codigoproveedor_equipo,
                macEquipo,
                imeiEquipo,
                numerotelefonicoEquipo,
                idEstado_equipo,
                idUnidad,
                idOrden_compra,
                idModelo_Equipo)

            VALUES (%s, 
                    %s, 
                    %s, 
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s)
                """, (codigo_inventario,
                      n_serie,
                      None,
                    codigo_proveedor,
                    mac,
                    imei,
                    telefono,
                    idEstado_equipo,
                    idUnidad,
                    id_orden_compra,
                    id_modelo_equipo
                      ))
        mysql.connection.commit()
        flash("equipos importados")

        
         

    #TODO orden de compra no es nulable. deberia ser nulable

        pass
    pass 

def encontrar_o_crear_tipo_equipo(nombreTipoEquipo, cur, nombre_marca):
    cur.execute("""
    SELECT idTipo_equipo
    FROM tipo_equipo te
    WHERE te.nombreTipo_equipo = %s
                """, (nombreTipoEquipo,))
    tupla_tipo_equipos = cur.fetchall()
    print("tupla_tipo_equipo")
    print(tupla_tipo_equipos)
    id_tipo_equipo = ""
    #revisar si se encontro un tipo de equipo.
    #asignar valor a id_tipo_equipo consecuentemente
    if(len(tupla_tipo_equipos) == 0):
        cur.execute("""
        INSERT INTO tipo_equipo
            (nombreTipo_Equipo)
        VALUES (%s)
        """, (nombreTipoEquipo,))
        mysql.connection.commit()
        id_tipo_equipo = cur.lastrowid
    else:
        id_tipo_equipo = tupla_tipo_equipos['idTipo_equipo']
    
    #revisar si existe una marca con el nombre enviado como argumento
    cur.execute("""
    SELECT idMarca_Equipo
    FROM marca_equipo me
    WHERE LOWER(me.nombreMarcaEquipo) LIKE LOWER(%s)
    """, (nombre_marca,))
    Marca = cur.fetchall()
    id_marca_equipo = ""
    if(len(Marca) == 0):
        #crear marca con el nombre
        cur.execute("""
        INSERT INTO marca_equipo
        (nombreMarcaEquipo)
        VALUES (%s)
                """, (nombre_marca,))
        mysql.connection.commit()
        id_marca_equipo = cur.lastrowid
    else:
        id_marca_equipo = Marca[0]['idMarca_Equipo']
    #verificar que el tipo y la marca esten asociados de lo contrario crear asociacion
    cur.execute("""
    SELECT *
    FROM marca_tipo_equipo mte
    WHERE mte.idMarca_Equipo = %s AND mte.idTipo_equipo = %s
                """, (id_marca_equipo, id_tipo_equipo))
    Marca_tipo_equipo = cur.fetchall()

    if(len(Marca_tipo_equipo) == 0):
        #agregar la relacion
        cur.execute("""
        INSERT INTO marca_tipo_equipo 
        (idMarca_Equipo, idTipo_equipo)
        VALUES (%s, %s)
        """, (id_marca_equipo, id_tipo_equipo,))
        mysql.connection.commit()
    
    return (id_tipo_equipo, id_marca_equipo)


def importar_unidad(col_comuna, col_modalidad, col_codigo, 
                    col_contacto, col_nombre, col_direccion, worksheet):
    print("importar unidad" + str(worksheet.max_row))
    for row in range(2, worksheet.max_row+1):
        nombreComuna = worksheet[col_comuna + str(row)].value
        nombreModalidad = worksheet[col_modalidad + str(row)].value
        codigoUnidad = worksheet[col_codigo + str(row)].value
        contactoUnidad = worksheet[col_contacto + str(row)].value
        nombreUnidad = worksheet[col_nombre + str(row)].value
        direccionUnidad = worksheet[col_direccion + str(row)].value

        cur = mysql.connection.cursor()
        print("importar_unidad")

        #id comuna

        cur.execute("""
            SELECT idComuna
            FROM comuna c
            WHERE LOWER(c.nombreComuna) LIKE LOWER(%s)
                    """, (nombreComuna,))
        Comuna = cur.fetchone()
        print(Comuna)
        #id modalidad
        cur.execute("""
            SELECT idModalidad
            FROM modalidad m
            WHERE LOWER(m.nombreModalidad) LIKE LOWER(%s)
                    """, (nombreModalidad,))
        Modalidad = cur.fetchone()

        try:
            cur.execute("""
            INSERT INTO unidad
                        (idUnidad, nombreUnidad, contactoUnidad, direccionUnidad, idComuna, idModalidad)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """, (codigoUnidad, nombreUnidad, contactoUnidad, direccionUnidad, 
                        Comuna['idComuna'], Modalidad['idModalidad']))
            mysql.connection.commit()
        except Exception as e:
            print("unidad ya ingresada ¿?")
            flash("Error al crear")
            #flash(e.args[1])

    flash("unidades importadas")
    print("unidades importadas")

#buscar un equipo singular por id
@equipo.route("/equipo/buscar_equipo/<id>")
@loguear_requerido
def buscar_equipo(id):
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT *
                FROM
                (
                SELECT e.idEquipo, e.Cod_inventarioEquipo, 
                    e.Num_serieEquipo, e.ObservacionEquipo,
                    e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, 
                    e.numerotelefonicoEquipo,
                    te.idTipo_equipo, 
                    te.nombreTipo_Equipo, ee.idEstado_equipo, ee.nombreEstado_equipo, 
                    u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
                moe.idModelo_equipo, moe.nombreModeloequipo, "" as nombreFuncionario
                FROM equipo e
                INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
                INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
                INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
                INNER JOIN unidad u on u.idUnidad = e.idUnidad
                INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra

                WHERE ee.nombreEstado_equipo NOT LIKE "EN USO"
                UNION 
                SELECT  e.idEquipo, e.Cod_inventarioEquipo, 
                        e.Num_serieEquipo, e.ObservacionEquipo, 
                        e.codigoproveedor_equipo, e.macEquipo, 
                        e.imeiEquipo, e.numerotelefonicoEquipo,
                        te.idTipo_equipo, te.nombreTipo_Equipo,
                        ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad,
                        u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
                        moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario
                FROM equipo e
                INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
                INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
                INNER JOIN unidad u on u.idUnidad = e.idUnidad
                INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra

                INNER JOIN equipo_asignacion ea on ea.idEquipo = e.idEquipo
                INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
                INNER JOIN asignacion a on a.idAsignacion = ea.idAsignacion
                INNER JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
                WHERE ee.nombreEstado_equipo LIKE "EN USO" 
                ) as subquery
                WHERE idEquipo = %s

    """, (id,))
    Equipos = cur.fetchall()
    cur.execute("SELECT * FROM tipo_equipo")
    tipoe_data = cur.fetchall()
    cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    estadoe_data = cur.fetchall()
    cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
    ubi_data = cur.fetchall()
    cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    ordenc_data = cur.fetchall()
    cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
    modeloe_data = cur.fetchall()

    return render_template(
        "equipo.html",
        equipo=Equipos,
        tipo_equipo=tipoe_data,
        estado_equipo=estadoe_data,
        orden_compra=ordenc_data,
        Unidad=ubi_data,
        modelo_equipo=modeloe_data,
        page=1,
        lastpage=True,
    )


#buscar todos los equipos en base a una palabra de busqueda
#@equipo.route("/consulta_equipo", methods =["POST"])
#@equipo.route("/consulta_equipo/<page>", methods =["POST"])
#@loguear_requerido
#def consulta_equipo(page = 1):
    #palabra = request.form["palabra"]
    #if palabra == "":
        #print("error_redirect")
    #page = int(page)
    #perpage = getPerPage()
    #offset = (int(page) - 1) * perpage
    #cur = mysql.connection.cursor()
    #cur.execute("SELECT COUNT(*) FROM equipo")
    #total = cur.fetchone()
    #total = int(str(total).split(":")[1].split("}")[0])
    #cur = mysql.connection.cursor()
    #query = f"""
    #set palabra = CONVERT('%{palabra}%' USING utf8)
    #SELECT *
    #FROM superequipo se
    #WHERE se.Cod_inventarioEquipo LIKE palabra OR
    #se.Num_serieEquipo LIKE '%{palabra}%' OR
    #se.codigoproveedor_equipo LIKE '%{palabra}%' OR
    #se.nombreidTipoequipo LIKE '%{palabra}%' OR
    #se.nombreEstado_equipo LIKE '%{palabra}%' OR
    #se.idUnidad LIKE '%{palabra}%' OR
    #se.nombreUnidad LIKE '%{palabra}%' OR
    #se.nombreOrden_compra LIKE '%{palabra}%' OR
    #se.nombreModeloequipo LIKE '%{palabra}%' OR
    #se.nombreFuncionario LIKE '%{palabra}%'
    #LIMIT {perpage} OFFSET {offset}
    #"""
    #print(query)
    #cur.execute(query)
    #equipos = cur.fetchall()

    #cur.execute("SELECT * FROM tipo_equipo")
    #tipoe_data = cur.fetchall()
    #cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    #estadoe_data = cur.fetchall()
    #cur.execute("SELECT idUnidad, nombreUnidad FROM Unidad")
    #ubi_data = cur.fetchall()
    #cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    #ordenc_data = cur.fetchall()
    #cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
    #modeloe_data = cur.fetchall()

    #return render_template(
        #"equipo.html",
        #equipo=equipos,
        #tipo_equipo=tipoe_data,
        #estado_equipo=estadoe_data,
        #orden_compra=ordenc_data,
        #Unidad=ubi_data,
        #modelo_equipo=modeloe_data,
        #page=page,
        #lastpage=page < (total / perpage) + 1,
    #)

def obtener_equipos():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM equipo")
        return cur.fetchall()
    

@equipo.route('/equipos', methods=['GET'])
def listar_equipos():
    page = request.args.get('page', 1, type=int)  # Obtener el número de página de la solicitud
    per_page = 15  # Número máximo de equipos por página
    equipos = obtener_equipos()  # Función que obtiene todos los equipos
    total_equipos = len(equipos)  # Contar la cantidad total de equipos

    # Calcular el inicio y el final de los equipos para la página actual
    start = (page - 1) * per_page
    end = start + per_page
    equipos_pagina = equipos[start:end]  # Obtener solo los equipos para la página actual

    return render_template('equipo.html', items=equipos_pagina, total_equipos=total_equipos, page=page)