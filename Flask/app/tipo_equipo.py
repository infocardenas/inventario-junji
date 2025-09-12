from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator
from MySQLdb import IntegrityError

tipo_equipo = Blueprint("tipo_equipo", __name__, template_folder="app/templates")


# Definir el esquema de validación para tipo_equipo
schema_tipo_equipo = {
    'nombre_tipo_equipo': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 45,
        'regex': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    }
}

# ruta para enviar los datos y visualizar la pagina principal para tipo de equipo
# Ruta para visualizar la página principal de tipos de equipo
@tipo_equipo.route("/tipo_equipo")
@tipo_equipo.route("/tipo_equipo/<int:page>")
@loguear_requerido
def tipoEquipo(page=1):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")

    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()

    # Obtener el total de registros para la paginación
    cur.execute("SELECT COUNT(*) AS total FROM tipo_equipo")
    total = cur.fetchone()["total"]

    # Obtener tipos de equipo con marcas relacionadas
    cur.execute("""
        SELECT 
            te.*, 
            GROUP_CONCAT(me.nombreMarcaEquipo SEPARATOR ', ') AS marcas
        FROM tipo_equipo te
        LEFT JOIN marca_tipo_equipo mte ON te.idTipo_equipo = mte.idTipo_equipo
        LEFT JOIN marca_equipo me ON mte.idMarca_Equipo = me.idMarca_Equipo
        GROUP BY te.idTipo_equipo
        LIMIT %s OFFSET %s
    """, (perpage, offset))
    tipo_equipo_data = cur.fetchall()

    # Obtener todas las marcas para el modal
    cur.execute("SELECT idMarca_equipo, nombreMarcaEquipo FROM marca_equipo")
    marcas = cur.fetchall()

    # Calcular última página
    lastpage = (total + perpage - 1) // perpage  # Redondeo hacia arriba

    return render_template(
        "Equipo/tipo_equipo.html",
        tipo_equipo=tipo_equipo_data,
        marcas=marcas,
        page=page,
        lastpage=page < lastpage
    )

# agrega un tipo de equipo
@tipo_equipo.route("/crear_tipo_equipo", methods=["POST"])
@administrador_requerido
def crear_tipo_equipo():
    if request.method != "POST":
        return redirect(url_for("tipo_equipo.tipoEquipo"))

    # Procesar datos del formulario
    nombre_tipo_equipo = request.form["nombreTipo_equipo"]
    ids_marcas_seleccionadas = [int(id_marca) for id_marca in request.form.getlist("marcas[]")]

    data = {
        'nombre_tipo_equipo': nombre_tipo_equipo
    }

    v = Validator(schema_tipo_equipo)
    if not v.validate(data):
        flash("Error: Caracteres no permitidos en el nombre", 'warning')
        return redirect(url_for("tipo_equipo.tipoEquipo"))

    cur = mysql.connection.cursor()
    try:
        # Insertar el tipo de equipo
        cur.execute("""
            INSERT INTO tipo_equipo (nombreTipo_equipo) 
            VALUES (%s)
        """, (nombre_tipo_equipo,))
        id_tipo_equipo = cur.lastrowid

        # Enlazar marcas seleccionadas
        for id_marca in ids_marcas_seleccionadas:
            cur.execute("""
                INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo) 
                VALUES (%s, %s)
            """, (id_marca, id_tipo_equipo))

        mysql.connection.commit()
        flash("Tipo de equipo creado exitosamente.", 'success')

    except IntegrityError as e: # Captura errores de la BD
        error_message = str(e)
        if "tipo_equipo" in error_message:
            flash("Error: El tipo de equipo ya se encuentra registrado", 'warning')

    except Exception as e: # Captura cualquier otro tipo de error
        error_message = str(e)
        flash("Error al crear el tipo de equipo:" + error_message, 'danger')

    return redirect(url_for("tipo_equipo.tipoEquipo"))

@tipo_equipo.route("/update_tipo_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_tipo_equipo(id):
    if request.method != "POST":
        return redirect(url_for("tipo_equipo.tipoEquipo"))

    # Procesar datos del formulario
    nombre_tipo_equipo = request.form['nombreTipo_equipo']
    ids_marcas_seleccionadas = [int(id_marca) for id_marca in request.form.getlist("marcas[]")]

    data = {
        'nombre_tipo_equipo': nombre_tipo_equipo
    }

    v = Validator(schema_tipo_equipo)
    if not v.validate(data):
        flash("Caracteres no permitidos en el nombre", "warning")
        return redirect(url_for("tipo_equipo.tipoEquipo"))

    cur = mysql.connection.cursor()

    # Obtener las marcas actuales asociadas al tipo
    cur.execute("""
        SELECT idMarca_Equipo 
        FROM marca_tipo_equipo 
        WHERE idTipo_equipo = %s
    """, (id,))
    ids_marca_actuales = [row['idMarca_Equipo'] for row in cur.fetchall()] or []

    # Comparar marcas para identificar cambios
    ids_marca_eliminadas = set(ids_marca_actuales) - set(ids_marcas_seleccionadas)
    ids_marca_nuevas = set(ids_marcas_seleccionadas) - set(ids_marca_actuales)

    try:
        # PASO 1: Manejar Marcas Eliminadas
        if ids_marca_eliminadas:
            for id_marca in ids_marca_eliminadas:
                # Eliminar equipos relacionados con los modelos de la marca eliminada
                cur.execute("""
                    DELETE FROM equipo 
                    WHERE idModelo_equipo IN (
                        SELECT idModelo_Equipo 
                        FROM modelo_equipo 
                        WHERE idMarca_Tipo_Equipo = (
                            SELECT idMarcaTipo 
                            FROM marca_tipo_equipo 
                            WHERE idMarca_Equipo = %s AND idTipo_equipo = %s
                        )
                    )
                """, (id_marca, id))

                # Eliminar modelos relacionados con la marca eliminada
                cur.execute("""
                    DELETE FROM modelo_equipo 
                    WHERE idMarca_Tipo_Equipo = (
                        SELECT idMarcaTipo 
                        FROM marca_tipo_equipo 
                        WHERE idMarca_Equipo = %s AND idTipo_equipo = %s
                    )
                """, (id_marca, id))

                # Eliminar relación en marca_tipo_equipo
                cur.execute("""
                    DELETE FROM marca_tipo_equipo 
                    WHERE idMarca_Equipo = %s AND idTipo_equipo = %s
                """, (id_marca, id))

        # PASO 2: Manejar Marcas Nuevas
        if ids_marca_nuevas:
            for id_marca in ids_marca_nuevas:
                cur.execute("""
                    INSERT INTO marca_tipo_equipo (idTipo_equipo, idMarca_Equipo)
                    VALUES (%s, %s)
                """, (id, id_marca))

        # PASO 3: Actualizar Nombre del Tipo de Equipo
        cur.execute("""
            UPDATE tipo_equipo 
            SET nombreTipo_equipo = %s 
            WHERE idTipo_equipo = %s
        """, (nombre_tipo_equipo, id))

        mysql.connection.commit()
        flash("Tipo de equipo actualizado exitosamente.", "success")

    except IntegrityError as e:
        error_message = str(e)
        if "tipo_equipo" in error_message:
            flash("Error: El tipo de equipo ya se encuentra registrado", 'warning')

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al actualizar el tipo de equipo: {str(e)}", "danger")

    return redirect(url_for("tipo_equipo.tipoEquipo"))

@tipo_equipo.route("/delete_tipo_equipo/<id>", methods=["GET"])
@administrador_requerido
def delete_tipo_equipo(id):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esa ruta", "warning")
        return redirect("/ingresar")

    cur = mysql.connection.cursor()
    try:
        ids = id.split(",")  

        for tipo_id in ids:
            # 1. Obtener todos los idMarcaTipo de este tipo_equipo
            cur.execute("SELECT idMarcaTipo FROM marca_tipo_equipo WHERE idTipo_equipo = %s", (tipo_id,))
            marca_tipo_ids = [row['idMarcaTipo'] for row in cur.fetchall()]

            # 2. Obtener todos los idModelo_Equipo de estos marca_tipo
            if marca_tipo_ids:
                formato = ",".join(["%s"] * len(marca_tipo_ids))
                cur.execute(f"SELECT idModelo_Equipo FROM modelo_equipo WHERE idMarca_Tipo_Equipo IN ({formato})", tuple(marca_tipo_ids))
                modelo_ids = [row['idModelo_Equipo'] for row in cur.fetchall()]
            else:
                modelo_ids = []

            # 3. Obtener todos los idEquipo de estos modelos
            if modelo_ids:
                formato = ",".join(["%s"] * len(modelo_ids))
                cur.execute(f"SELECT idEquipo FROM equipo WHERE idModelo_equipo IN ({formato})", tuple(modelo_ids))
                equipo_ids = [row['idEquipo'] for row in cur.fetchall()]
            else:
                equipo_ids = []

            # 4. Obtener todos los idEquipoAsignacion de estos equipos
            if equipo_ids:
                formato = ",".join(["%s"] * len(equipo_ids))
                cur.execute(f"SELECT idEquipoAsignacion FROM equipo_asignacion WHERE idEquipo IN ({formato})", tuple(equipo_ids))
                equipo_asignacion_ids = [row['idEquipoAsignacion'] for row in cur.fetchall()]
            else:
                equipo_asignacion_ids = []

            # 5. Obtener todos los idTraslado de traslacion de estos equipos
            if equipo_ids:
                formato = ",".join(["%s"] * len(equipo_ids))
                cur.execute(f"SELECT idTraslado FROM traslacion WHERE idEquipo IN ({formato})", tuple(equipo_ids))
                traslado_ids = [row['idTraslado'] for row in cur.fetchall()]
            else:
                traslado_ids = []

            # 6. Eliminar detalle_traslado
            if traslado_ids:
                formato = ",".join(["%s"] * len(traslado_ids))
                cur.execute(f"DELETE FROM detalle_traslado WHERE idTraslado IN ({formato})", tuple(traslado_ids))

            # 7. Eliminar traslacion
            if equipo_ids:
                formato = ",".join(["%s"] * len(equipo_ids))
                cur.execute(f"DELETE FROM traslacion WHERE idEquipo IN ({formato})", tuple(equipo_ids))

            # 8. Eliminar incidencia
            if equipo_ids:
                formato = ",".join(["%s"] * len(equipo_ids))
                cur.execute(f"DELETE FROM incidencia WHERE idEquipo IN ({formato})", tuple(equipo_ids))

            # 9. Eliminar devolucion
            if equipo_asignacion_ids:
                formato = ",".join(["%s"] * len(equipo_asignacion_ids))
                cur.execute(f"DELETE FROM devolucion WHERE idEquipoAsignacion IN ({formato})", tuple(equipo_asignacion_ids))

            # 10. Eliminar equipo_asignacion
            if equipo_ids:
                formato = ",".join(["%s"] * len(equipo_ids))
                cur.execute(f"DELETE FROM equipo_asignacion WHERE idEquipo IN ({formato})", tuple(equipo_ids))

            # 11. Eliminar equipos
            if modelo_ids:
                formato = ",".join(["%s"] * len(modelo_ids))
                cur.execute(f"DELETE FROM equipo WHERE idModelo_equipo IN ({formato})", tuple(modelo_ids))

            # 12. Eliminar modelos
            if marca_tipo_ids:
                formato = ",".join(["%s"] * len(marca_tipo_ids))
                cur.execute(f"DELETE FROM modelo_equipo WHERE idMarca_Tipo_Equipo IN ({formato})", tuple(marca_tipo_ids))

            # 13. Eliminar marca_tipo_equipo
            cur.execute("DELETE FROM marca_tipo_equipo WHERE idTipo_equipo = %s", (tipo_id,))

            # 14. Eliminar tipo_equipo
            cur.execute("DELETE FROM tipo_equipo WHERE idTipo_equipo = %s", (tipo_id,))

        mysql.connection.commit()
        flash("Tipo(s) de equipo eliminado(s) exitosamente.", "success")
        return redirect(url_for("tipo_equipo.tipoEquipo"))

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al eliminar el tipo de equipo: {str(e)}", "danger")
        return redirect(url_for("tipo_equipo.tipoEquipo"))
