from flask import Blueprint, request, flash, render_template, redirect, url_for, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator

marca_equipo = Blueprint('marca_equipo', __name__, template_folder= 'app/templates')

# Definir el esquema de validación para marca equipo
marca_equipo_schema = {
    'nombre_marca_equipo': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 45,
        'regex': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    }
}

@marca_equipo.route('/marca_equipo')
#@marca_equipo.route('/marca_equipo/<order>')
@marca_equipo.route('/marca_equipo/<page>/')
@loguear_requerido
def marcaEquipo(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (page-1) * perpage
    query = 'SELECT * FROM marca_equipo '
    query += "LIMIT {} OFFSET {}".format(perpage, offset)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM marca_equipo')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])

    
    return render_template(
        'Equipo/marca_equipo.html', 
        marca_equipo = data, 
        page=page,
        lastpage = page < (total/perpage) + 1
        )


#agregar
@marca_equipo.route('/add_marca_equipo', methods = ['POST'])
@administrador_requerido
def add_marca_equipo():
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    if request.method == 'POST':
# Obtener los datos del formulario
        datos = {
            'nombre_marca_equipo': request.form["nombre_marca_equipo"]
        }

        # Validar los datos usando Cerberus
        v = Validator(marca_equipo_schema)
        if not v.validate(datos):
            # Capturar los errores de validación
            errors = v.errors
            # Formatear el mensaje de advertencia
            warning_messages = []
            flash("Formato de entrada no válido", 'warning')
            return redirect(url_for("marca_equipo.marcaEquipo"))  # Redirigir a la misma página

        try:
            cur = mysql.connection.cursor()
            cur.execute("""INSERT INTO marca_equipo (nombreMarcaEquipo) VALUES (%s)""", (datos['nombre_marca_equipo'],))
            mysql.connection.commit()
            flash('Marca agregada exitosamente', 'success')
            return redirect(url_for('marca_equipo.marcaEquipo'))  
        except Exception as e:
            print("excepcion al agregar marca equipo: ", e)
            if(e.args[0] == 1062):
                flash("La marca ya se encuentra registrada", 'warning')
            else:
                flash("Error al registrar la marca", 'danger')
            return redirect(url_for('marca_equipo.marcaEquipo'))


#actualizar
@marca_equipo.route('/update_marca_equipo/<id>', methods = ['POST'])
@administrador_requerido
def update_marca_equipo(id):
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    if request.method == 'POST':
        # Obtener los datos del formulario
        datos = {
            'nombre_marca_equipo': request.form["nombre_marca_equipo"]   
        }

        # Validar los datos usando Cerberus
        v = Validator(marca_equipo_schema)
        if not v.validate(datos):
            flash("Formato de entrada no válido", "warning")
            return redirect(url_for("marca_equipo.marcaEquipo"))


        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE marca_equipo
            SET nombreMarcaEquipo = %s
            WHERE idMarca_Equipo = %s
            """, (datos['nombre_marca_equipo'], id))
            mysql.connection.commit()
            flash('Marca actualizada exitosamente', 'success')
            return redirect(url_for('marca_equipo.marcaEquipo'))
        except Exception as e:
            if (e.args[0] == 1062): # Error de llave duplicada en la BD (marca ya registrada)
                flash("La marca ya se encuentra registrada", 'warning')
            else:
                flash("Error al actualizar la marca del equipo", 'danger')

            return redirect(url_for('marca_equipo.marcaEquipo'))

# Funcion eliminar, para mantener la integridad de los datos, se muestra un mensaje al usuario para que confirme si desea eliminar la marca, si lo hace entonces borramos todas las dependencias de la marca
@marca_equipo.route('/delete_marca_equipo/<ids>', methods=['GET'])
@administrador_requerido
def delete_marca_equipo(ids):
    try:
        cur = mysql.connection.cursor()
        id_list = ids.split(',')

        for marca_id in id_list:
            # 1. Obtener todos los idMarcaTipo de esta marca
            cur.execute("SELECT idMarcaTipo FROM marca_tipo_equipo WHERE idMarca_Equipo = %s", (marca_id,))
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
            cur.execute("DELETE FROM marca_tipo_equipo WHERE idMarca_Equipo = %s", (marca_id,))

            # 14. Eliminar marca_equipo
            cur.execute("DELETE FROM marca_equipo WHERE idMarca_Equipo = %s", (marca_id,))

        mysql.connection.commit()
        flash(f"Se eliminaron {len(id_list)} marca(s) y sus relaciones asociadas exitosamente.", 'success')
        return redirect(url_for('marca_equipo.marcaEquipo'))
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al eliminar la(s) marca(s): {str(e)}", 'danger')
        return redirect(url_for('marca_equipo.marcaEquipo'))



