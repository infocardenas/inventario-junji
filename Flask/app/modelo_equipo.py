from flask import Blueprint, flash, redirect, render_template, url_for, request, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator
from flask import jsonify

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



@modelo_equipo.route("/modelo_equipo")
@modelo_equipo.route("/modelo_equipo/<page>")
@loguear_requerido
def modeloEquipo(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()
    cur.execute(""" 
                SELECT me.*, te.nombreTipo_equipo, mae.nombreMarcaEquipo
                FROM modelo_equipo me
                INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
                INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
                INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo;

                """)
    data = cur.fetchall()
    cur.execute("SELECT * FROM marca_equipo")
    marca_data = cur.fetchall()
    marca_con_tipo = []
    for i in range(0, len(marca_data)):
        marca = marca_data[i]
        cur.execute("""
        SELECT *
        FROM marca_tipo_equipo mte
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        WHERE mte.idMarca_Equipo = %s
                    """, (marca['idMarca_Equipo'],))
        tipos_asociados = cur.fetchall()

        nueva_marca = ingresar_elemento_a_tupla(marca, tipos_asociados, 'tipo_equipo')
        marca_con_tipo.append(nueva_marca)

    marca_con_tipo = tuple(marca_con_tipo)


        
    cur.execute("SELECT * FROM tipo_equipo")
    tipo_data = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM modelo_equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])


    return render_template(
        "Equipo/modelo_equipo.html",
        marca_equipo=marca_con_tipo,
        modelo_equipo=data,
        tipo_equipo=tipo_data,
        page=page,
        lastpage=page < (total / perpage) + 1,
    )


def ingresar_elemento_a_tupla(tupla_mayor, tupla_a_agregar, nombre_tupla_agregar):
    tupla_mayor.update({nombre_tupla_agregar: tupla_a_agregar})
    return tupla_mayor


# agregar un regisro para modelo de equipo
@modelo_equipo.route("/add_modelo_equipo", methods=["POST"])
#@administrador_requerido
def add_modelo_equipo():
    if request.method == "POST":
        data = {
            'nombre_modelo_equipo': request.form['nombre_modelo_equipo'],
            'id_tipo_equipo': int(request.form['nombre_tipo_equipo']),
            'id_marca_equipo': int(request.form['nombre_marca_equipo'])
        }
        print("Datos recibidos del formulario:", data)

        v = Validator(schema)
        if not v.validate(data):
            errores = v.errors
            mensaje_error = "Errores de validación:"
            for campo, detalle in errores.items():
                mensaje_error += f" {campo}: {detalle};"
            print("Errores de validación:", v.errors)
            print("Validación fallida, redirigiendo...")
            return redirect(url_for("modelo_equipo.modeloEquipo"))

        cur = None  # Inicializar el cursor
        try:
            cur = mysql.connection.cursor()

            # Verificar o insertar en marca_tipo_equipo
            print("Validando relación marca-tipo...")
            cur.execute(
                """
                SELECT idMarcaTipo 
                FROM marca_tipo_equipo 
                WHERE idMarca_Equipo = %s AND idTipo_equipo = %s
                """,
                (data['id_marca_equipo'], data['id_tipo_equipo'])
            )
            marca_tipo = cur.fetchone()

            if not marca_tipo:  # Si no existe la relación, crearla
                print("Relación no existe, creando en marca_tipo_equipo...")
                cur.execute(
                    """
                    INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo) 
                    VALUES (%s, %s)
                    """,
                    (data['id_marca_equipo'], data['id_tipo_equipo'])
                )
                mysql.connection.commit()  # Confirmar para obtener el ID
                cur.execute("SELECT LAST_INSERT_ID() AS idMarcaTipo")
                marca_tipo = cur.fetchone()

            id_marca_tipo = marca_tipo['idMarcaTipo']
            print(f"ID de marca-tipo obtenido: {id_marca_tipo}")

            # Insertar el modelo en modelo_equipo
            print(f"Insertando modelo: {data['nombre_modelo_equipo']}, Marca-Tipo ID: {id_marca_tipo}")
            cur.execute(
                """
                INSERT INTO modelo_equipo (nombreModeloequipo, idMarca_Tipo_Equipo) 
                VALUES (%s, %s)
                """,
                (data['nombre_modelo_equipo'], id_marca_tipo)
            )

            # Confirmar las transacciones
            mysql.connection.commit()
            print("Transacciones confirmadas")

        except Exception as e:
            print(f"Error durante la ejecución: {str(e)}")
            flash(f"Error al crear el modelo: {str(e)}")
            return redirect(url_for("modelo_equipo.modeloEquipo"))

        finally:
            if cur:
                cur.close()  # Asegurarse de cerrar el cursor
                print("Cursor cerrado")

        flash("Modelo agregado exitosamente", 'success')
        return redirect(url_for("modelo_equipo.modeloEquipo"))


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



# actualizar
@modelo_equipo.route("/update_modelo_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_modelo_equipo(id):
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    if request.method == "POST":
        # Obtener los datos del formulario
        data = {
                'nombre_modelo_equipo': request.form['nombre_modelo_equipo'],
                'id_marca_equipo': request.form['nombre_marca_equipo'],
                'id_tipo_equipo': request.form['nombre_tipo_equipo']
        }
# Validar los datos usando Cerberus
        v = Validator(schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for("modelo_equipo.modeloEquipo"))
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE modelo_equipo 
            SET nombreModeloequipo = %s,
                idTipo_Equipo = %s,
                idMarca_Equipo = %s
            WHERE idModelo_Equipo = %s
            """,
                (data['nombre_modelo_equipo'], data['id_tipo_equipo'], data['id_marca_equipo'], id),
            )
            mysql.connection.commit()
            flash("Modelo actualizado correctamente")
            return redirect(url_for("modelo_equipo.modeloEquipo"))
        except Exception as e:
            flash("Error al crear")
            return redirect(url_for("modelo_equipo.modeloEquipo"))


# eliminar
@modelo_equipo.route("/delete_modelo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_modelo_equipo(id):
    print(f"🔍 Recibida solicitud para eliminar modelo ID: {id}")

    if "user" not in session:
        flash("No estás autorizado.", "danger")
        return redirect("/ingresar")

    try:
        cur = mysql.connection.cursor()

        # Verificar si hay equipos asociados al modelo
        cur.execute("SELECT COUNT(*) as total FROM equipo WHERE idModelo_equipo = %s", (id,))
        result = cur.fetchone()

        # ✅ Acceder correctamente al valor sin importar si `fetchone()` devuelve una tupla o diccionario
        if result is None:
            count = 0
        elif isinstance(result, dict):
            count = result["total"]  # 🔥 Si devuelve un diccionario
        else:
            count = result[0]  # 🔥 Si devuelve una tupla

        print(f"🔍 Equipos asociados a modelo {id}: {count}")

        if count > 0:
            confirm_url = url_for("modelo_equipo.delete_modelo_equipo_confirm", id=id)
            flash("confirm_delete_modelo", confirm_url)  # Enviar mensaje especial a JS
            return redirect(url_for("modelo_equipo.modeloEquipo"))


        # 🔹 Redirigir a la confirmación si no hay equipos asociados
        return redirect(url_for("modelo_equipo.delete_modelo_equipo_confirm", id=id))

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(f"❌ Error al verificar modelo {id}: {error_message}")
        flash(f"Error al verificar el modelo: {error_message}", "danger")
        return redirect(url_for("modelo_equipo.modeloEquipo"))


@modelo_equipo.route("/delete_modelo_equipo_confirm/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_modelo_equipo_confirm(id):
    print(f"🔍 Confirmada eliminación del modelo ID: {id}")

    if "user" not in session:
        flash("No estás autorizado.", "danger")
        return redirect("/ingresar")

    try:
        cur = mysql.connection.cursor()

        # 🔹 Eliminar dependencias antes de borrar el modelo

        cur.execute("""
            DELETE FROM equipo_asignacion 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo WHERE idModelo_equipo = %s
            )
        """, (id,))

        cur.execute("""
            DELETE FROM traslacion 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo WHERE idModelo_equipo = %s
            )
        """, (id,))

        cur.execute("""
            DELETE FROM incidencia 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo WHERE idModelo_equipo = %s
            )
        """, (id,))

        cur.execute("""
            DELETE FROM devolucion 
            WHERE rutFuncionario IN (
                SELECT f.rutFuncionario 
                FROM funcionario f
                WHERE f.rutFuncionario IN (
                    SELECT a.rutFuncionario 
                    FROM asignacion a
                    WHERE a.idAsignacion IN (
                        SELECT ea.idAsignacion 
                        FROM equipo_asignacion ea
                        WHERE ea.idEquipo IN (
                            SELECT idEquipo FROM equipo WHERE idModelo_equipo = %s
                        )
                    )
                )
            )
        """, (id,))

        # 🔹 Eliminar equipos relacionados con el modelo
        cur.execute("""
            DELETE FROM equipo WHERE idModelo_equipo = %s
        """, (id,))

        # 🔹 Finalmente, eliminar el modelo de equipo
        cur.execute("""
            DELETE FROM modelo_equipo WHERE idModelo_Equipo = %s
        """, (id,))

        mysql.connection.commit()

        flash("Modelo eliminado correctamente junto con sus relaciones asociadas.", "success")
        return redirect(url_for("modelo_equipo.modeloEquipo"))

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        print(f"❌ Error al eliminar modelo {id}: {error_message}")
        flash(f"Error al eliminar el modelo: {error_message}", "danger")
        return redirect(url_for("modelo_equipo.modeloEquipo"))




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


@modelo_equipo.route("/get_modelos/<marca_id>/<tipo_id>", methods=["GET"])
@loguear_requerido
def obtener_modelos(marca_id, tipo_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT me.idModelo_Equipo, me.nombreModeloequipo 
        FROM modelo_equipo me
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = me.idMarca_Tipo_Equipo
        WHERE mte.idTipo_equipo = %s AND mte.idMarca_Equipo = %s
    """, (tipo_id, marca_id))
    modelos = cur.fetchall()
    cur.close()
    return jsonify(modelos)


