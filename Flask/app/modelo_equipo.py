from flask import Blueprint, flash, redirect, render_template, url_for, request, session, jsonify
from . import mysql
from .funciones import getPerPage
from .cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator
from flask import jsonify
from MySQLdb import IntegrityError

modelo_equipo = Blueprint("modelo_equipo", __name__, template_folder="app/templates")

# Definir el esquema de validación
schema = {
    'nombre_modelo_equipo': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 45,
        'regex': '^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]*$' # Permite solo letras, números y espacios
    },
    'id_tipo_equipo': {
        'type':'integer',
        'required': True
    },
    'id_marca_equipo': {
        'type':'integer',
        'required': True
    }
}


@modelo_equipo.route("/buscar_modelo_equipo", methods=["GET"])
@loguear_requerido
def buscar_modelo_equipo():
    query = request.args.get("q", "").lower()  # Obtener el término de búsqueda
    page = request.args.get("page", default=1, type=int)  # Página actual
    per_page = 10  # Número de resultados por página
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # Consulta para buscar modelos de equipo
    cur.execute("""
        SELECT me.idModelo_Equipo, me.nombreModeloequipo, 
               te.nombreTipo_equipo, mae.nombreMarcaEquipo
        FROM modelo_equipo me
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
        WHERE LOWER(me.nombreModeloequipo) LIKE %s
           OR LOWER(te.nombreTipo_equipo) LIKE %s
           OR LOWER(mae.nombreMarcaEquipo) LIKE %s
        LIMIT %s OFFSET %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%", per_page, offset))
    modelos = cur.fetchall()

    # Total de resultados para la búsqueda
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM modelo_equipo me
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
        WHERE LOWER(me.nombreModeloequipo) LIKE %s
           OR LOWER(te.nombreTipo_equipo) LIKE %s
           OR LOWER(mae.nombreMarcaEquipo) LIKE %s
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    total = cur.fetchone()["total"]
    total_pages = (total + per_page - 1) // per_page

    return jsonify({
        "modelos": modelos,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    })

@modelo_equipo.route("/modelo_equipo")
@modelo_equipo.route("/modelo_equipo/<int:page>")
@loguear_requerido
def modeloEquipo(page=1):
    perpage = getPerPage()  # cantidad de registros por página
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()

    # Traer solo los registros de la página actual
    cur.execute("""
        SELECT me.*, te.nombreTipo_equipo, mae.nombreMarcaEquipo
        FROM modelo_equipo me
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
        LIMIT %s OFFSET %s
    """, (perpage, offset))
    data = cur.fetchall()

    # Contar total de registros
    cur.execute("SELECT COUNT(*) AS total FROM modelo_equipo")
    total = cur.fetchone()['total']
    lastpage = (total + perpage - 1) // perpage  # redondeo entero hacia arriba

    # Marcas y tipos
    cur.execute("SELECT * FROM marca_equipo")
    marca_data = cur.fetchall()
    marca_con_tipo = []
    for marca in marca_data:
        cur.execute("""
            SELECT * FROM marca_tipo_equipo mte
            INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
            WHERE mte.idMarca_Equipo = %s
        """, (marca['idMarca_Equipo'],))
        tipos_asociados = cur.fetchall()
        marca.update({'tipo_equipo': tipos_asociados})
        marca_con_tipo.append(marca)

    cur.execute("SELECT * FROM tipo_equipo")
    tipo_data = cur.fetchall()

    cur.close()

    return render_template(
        "Equipo/modelo_equipo.html",
        modelo_equipo=data,
        marca_equipo=marca_con_tipo,
        tipo_equipo=tipo_data,
        page=page,
        lastpage=lastpage,
    )

def getPerPage():
    return 10  # o cualquier número que desees por página

@modelo_equipo.route("/add_modelo_equipo", methods=["POST"])
def add_modelo_equipo():
    if request.method == "POST":
        data = {
            'nombre_modelo_equipo': request.form['nombre_modelo_equipo'].strip(),
            'id_tipo_equipo': int(request.form['nombre_tipo_equipo']),
            'id_marca_equipo': int(request.form['nombre_marca_equipo'])
        }
        print("Datos recibidos del formulario:", data)

        v = Validator(schema)
        if not v.validate(data):
            return jsonify({
                "status": "error",
                "message": "Error de validación en los datos ingresados.",
                "tipo_alerta": "warning"
            }), 400

        cur = None
        try:
            cur = mysql.connection.cursor()

            # **Verificar o insertar en marca_tipo_equipo**
            cur.execute("""
                SELECT idMarcaTipo 
                FROM marca_tipo_equipo 
                WHERE idMarca_Equipo = %s AND idTipo_equipo = %s
            """, (data['id_marca_equipo'], data['id_tipo_equipo']))
            marca_tipo = cur.fetchone()

            if not marca_tipo:
                cur.execute("""
                    INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo) 
                    VALUES (%s, %s)
                """, (data['id_marca_equipo'], data['id_tipo_equipo']))
                mysql.connection.commit()
                cur.execute("SELECT LAST_INSERT_ID() AS idMarcaTipo")
                marca_tipo = cur.fetchone()

            id_marca_tipo = marca_tipo['idMarcaTipo']

            # **Intentar insertar el modelo en la base de datos**
            cur.execute("""
                INSERT INTO modelo_equipo (nombreModeloequipo, idMarca_Tipo_Equipo) 
                VALUES (%s, %s)
            """, (data['nombre_modelo_equipo'], id_marca_tipo))

            mysql.connection.commit()

            return jsonify({
                "status": "success",
                "message": "Modelo agregado exitosamente.",
                "tipo_alerta": "success"
            }), 200

        except IntegrityError as e:
            error_message = str(e)
            mensaje = "Error de duplicación en la base de datos."
            if "Duplicate entry" in error_message:
                if "nombreModeloequipo" in error_message:
                    mensaje = "Error: Este modelo ya existe. Por favor, elija otro nombre."
            
            return jsonify({
                "status": "error",
                "message": mensaje,
                "tipo_alerta": "warning"
            }), 400

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al crear el modelo: {str(e)}",
                "tipo_alerta": "danger"
            }), 500

        finally:
            if cur:
                cur.close()


# Envias datos a formulario editar
@modelo_equipo.route("/edit_modelo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_modelo_equipo(id):
    cur = mysql.connection.cursor()
    # Consulta principal para obtener el modelo de equipo
    cur.execute(
        """ 
        SELECT *
        FROM modelo_equipo moe
        LEFT OUTER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = moe.idMarca_Tipo_Equipo
        LEFT OUTER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        LEFT OUTER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
        WHERE moe.idModelo_Equipo = %s;
        """,
        (id,)
    )
    data = cur.fetchone()

    # Obtener todas las marcas
    cur.execute("SELECT * FROM marca_equipo")
    mae_data = cur.fetchall()

    # Obtener tipos de equipo relacionados con cada marca
    marcas_con_tipo_equipo = []
    for marca in mae_data:
        cur.execute("""
            SELECT te.idTipo_equipo, te.nombreTipo_equipo, te.observacionTipoEquipo
            FROM marca_tipo_equipo mte
            INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
            WHERE mte.idMarca_Equipo = %s;
        """, (marca['idMarca_Equipo'],))
        tipo_equipo_data = cur.fetchall()
        marca['tipo_equipo'] = tipo_equipo_data
        marcas_con_tipo_equipo.append(marca)

    cur.close()

    # Obtener todas las marcas y tipos de equipo para el formulario
    curs = mysql.connection.cursor()
    curs.execute("SELECT * FROM tipo_equipo")
    tipo_data = curs.fetchall()
    curs.execute("SELECT * FROM marca_equipo")
    marcas = curs.fetchall()
    curs.close()

    # Renderizar la plantilla
    return render_template(
        "Equipo/editModelo_equipo.html",
        modelo_equipo=data,
        id=id,
        marca_equipo=marcas_con_tipo_equipo,
        tipo_equipo=tipo_data,
        marcas=marcas
    )


@modelo_equipo.route("/update_modelo_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_modelo_equipo(id):
    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "No estás autorizado para realizar esta acción."
        }), 403

    if request.method == "POST":
        try:
            # **Obtener datos del formulario**
            data = {
                'nombre_modelo_equipo': request.form['nombre_modelo_equipo'].strip(),
                'id_tipo_equipo': request.form['nombre_tipo_equipo'].strip(),
                'id_marca_equipo': request.form['nombre_marca_equipo'].strip()
            }

            # **Convertir a NULL si están vacíos**
            data['id_tipo_equipo'] = int(data['id_tipo_equipo']) if data['id_tipo_equipo'] else None
            data['id_marca_equipo'] = int(data['id_marca_equipo']) if data['id_marca_equipo'] else None

            # **Validar datos con Cerberus**
            v = Validator(schema)
            if not v.validate(data):
                return jsonify({
                    "status": "error",
                    "message": "Entrada inválida: Solo caracteres permitidos.",
                    "errors": v.errors,
                    "tipo_alerta": "warning"
                }), 400  # ⛔ Retornar error 400 para manejo en el frontend

            cur = mysql.connection.cursor()

            # **Verificar o insertar en marca_tipo_equipo**
            cur.execute("""
                SELECT idMarcaTipo 
                FROM marca_tipo_equipo 
                WHERE idMarca_Equipo = %s AND idTipo_equipo = %s
            """, (data['id_marca_equipo'], data['id_tipo_equipo']))
            marca_tipo = cur.fetchone()

            if not marca_tipo:
                cur.execute("""
                    INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo) 
                    VALUES (%s, %s)
                """, (data['id_marca_equipo'], data['id_tipo_equipo']))
                mysql.connection.commit()
                cur.execute("SELECT LAST_INSERT_ID() AS idMarcaTipo")
                marca_tipo = cur.fetchone()

            id_marca_tipo = marca_tipo['idMarcaTipo']

            # **Actualizar modelo_equipo**
            cur.execute("""
                UPDATE modelo_equipo 
                SET nombreModeloequipo = %s,
                    idMarca_Tipo_Equipo = %s
                WHERE idModelo_Equipo = %s
            """, (data['nombre_modelo_equipo'], id_marca_tipo, id))
            
            mysql.connection.commit()
            return jsonify({
                "status": "success",
                "message": "Modelo actualizado correctamente."
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al actualizar el modelo: {str(e)}"
            }), 500



@modelo_equipo.route('/delete_modelo_equipo', methods=['POST'])
@administrador_requerido
def delete_modelo_equipo():
    try:
        data = request.get_json()
        if not data or "ids" not in data:
            return jsonify({
                "status": "error",
                "message": "No se recibieron modelos para eliminar.",
                "tipo_alerta": "warning"
            }), 400

        id_list = data["ids"]

        if not id_list:
            return jsonify({
                "status": "error",
                "message": "Debe seleccionar al menos un modelo.",
                "tipo_alerta": "warning"
            }), 400

        cur = mysql.connection.cursor()

        # Eliminar dependencias en equipo_asignacion
        cur.execute("""
            DELETE FROM equipo_asignacion 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo WHERE idModelo_equipo IN %s
            )
        """, (tuple(id_list),))

        # Eliminar dependencias en traslacion
        cur.execute("""
            DELETE FROM traslacion 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo WHERE idModelo_equipo IN %s
            )
        """, (tuple(id_list),))

        # Eliminar dependencias en incidencia
        cur.execute("""
            DELETE FROM incidencia 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo WHERE idModelo_equipo IN %s
            )
        """, (tuple(id_list),))

        # Eliminar dependencias en devolucion
        cur.execute("""
            DELETE FROM devolucion 
            WHERE idEquipoAsignacion IN (
                SELECT idEquipoAsignacion
                FROM equipo_asignacion
                WHERE idEquipo IN (
                    SELECT idEquipo
                    FROM equipo 
                    WHERE idModelo_equipo IN (%s)
                )
            )
        """, (tuple(id_list),))

        # Eliminar equipos relacionados al modelo
        cur.execute("""
            DELETE FROM equipo WHERE idModelo_equipo IN %s
        """, (tuple(id_list),))

        # Eliminar los modelos seleccionados
        cur.execute("""
            DELETE FROM modelo_equipo WHERE idModelo_Equipo IN %s
        """, (tuple(id_list),))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": f"Se eliminaron {len(id_list)} modelo(s) correctamente.",
            "tipo_alerta": "success"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al eliminar modelos: {str(e)}",
            "tipo_alerta": "danger"
        }), 500



@modelo_equipo.route("/get_marcas", methods=["GET"])
@loguear_requerido
def obtener_marcas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM marca_equipo")
    marcas = cur.fetchall()
    cur.close()
    return jsonify(marcas)

@modelo_equipo.route("/get_tipos/<marca_id>", methods=["GET"])
@loguear_requerido
def obtener_tipos(marca_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT te.idTipo_equipo, te.nombreTipo_equipo 
        FROM marca_tipo_equipo mte
        INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE mte.idMarca_Equipo = %s
    """, (marca_id,))
    tipos = cur.fetchall()
    cur.close()
    return jsonify(tipos)


@modelo_equipo.route("/get_modelo/<id>", methods=["GET"])
@loguear_requerido
def obtener_modelo(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT me.idModelo_Equipo, me.nombreModeloequipo, 
               mae.idMarca_Equipo, mae.nombreMarcaEquipo, 
               te.idTipo_equipo, te.nombreTipo_equipo
        FROM modelo_equipo me
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
        WHERE me.idModelo_Equipo = %s
    """, (id,))
    modelo = cur.fetchone()
    cur.close()

    if modelo:
        return jsonify(modelo)
    else:
        return jsonify({"error": "Modelo no encontrado"}), 404

@modelo_equipo.route("/get_modelos/<marca_id>/<tipo_id>", methods=["GET"])
@loguear_requerido
def obtener_modelos(marca_id, tipo_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT me.idModelo_Equipo, me.nombreModeloequipo
        FROM modelo_equipo me
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
        WHERE mte.idMarca_Equipo = %s AND mte.idTipo_equipo = %s
    """, (marca_id, tipo_id))
    
    modelos = cur.fetchall()  # Obtiene los resultados
    cur.close()


    return jsonify(modelos)
