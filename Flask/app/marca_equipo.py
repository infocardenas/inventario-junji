from flask import Blueprint, request, flash, render_template, redirect, url_for, g, session
from . import mysql
from .funciones import getPerPage
from .cuentas import loguear_requerido, administrador_requerido
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

        # Dividir los IDs por comas (para eliminaciones múltiples)
        id_list = ids.split(',')

        # PASO 1: Eliminar dependencias en detalle_traslado
        cur.execute("""
            DELETE FROM detalle_traslado 
            WHERE idTraslado IN (
                SELECT idTraslado FROM traslado
                WHERE idTraslado IN (
                    SELECT idTraslado FROM traslacion
                    WHERE idEquipo IN (
                        SELECT idEquipo FROM equipo 
                        WHERE idModelo_equipo IN (
                            SELECT idModelo_Equipo FROM modelo_equipo 
                            WHERE idMarca_Tipo_Equipo IN (
                                SELECT idMarcaTipo FROM marca_tipo_equipo 
                                WHERE idMarca_Equipo IN (%s)
                            )
                        )
                    )
                )
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 2: Eliminar dependencias en incidencia
        cur.execute("""
            DELETE FROM incidencia 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo 
                WHERE idModelo_equipo IN (
                    SELECT idModelo_Equipo FROM modelo_equipo 
                    WHERE idMarca_Tipo_Equipo IN (
                        SELECT idMarcaTipo FROM marca_tipo_equipo 
                        WHERE idMarca_Equipo IN (%s)
                    )
                )
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 3: Eliminar dependencias en devolucion
        cur.execute("""
            DELETE FROM devolucion 
            WHERE idEquipoAsignacion IN (
                SELECT idEquipoAsignacion
                FROM equipo_asignacion
                WHERE idEquipo IN (
                    SELECT idEquipo
                    FROM equipo
                    WHERE idModelo_equipo IN (
                        SELECT idModelo_Equipo 
                        FROM modelo_equipo
                        WHERE idMarca_Tipo_Equipo IN (
                            SELECT idMarcaTipo
                            FROM marca_tipo_equipo
                            WHERE idMarca_Equipo IN (%s)
                        )
                    )
                )
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 4: Eliminar dependencias en equipo_asignacion
        cur.execute("""
            DELETE FROM equipo_asignacion 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo 
                WHERE idModelo_equipo IN (
                    SELECT idModelo_Equipo FROM modelo_equipo 
                    WHERE idMarca_Tipo_Equipo IN (
                        SELECT idMarcaTipo FROM marca_tipo_equipo 
                        WHERE idMarca_Equipo IN (%s)
                    )
                )
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 5: Eliminar dependencias en traslacion
        cur.execute("""
            DELETE FROM traslacion 
            WHERE idEquipo IN (
                SELECT idEquipo FROM equipo 
                WHERE idModelo_equipo IN (
                    SELECT idModelo_Equipo FROM modelo_equipo 
                    WHERE idMarca_Tipo_Equipo IN (
                        SELECT idMarcaTipo FROM marca_tipo_equipo 
                        WHERE idMarca_Equipo IN (%s)
                    )
                )
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)


        # PASO 6: Eliminar equipos relacionados a la marca
        cur.execute("""
            DELETE FROM equipo 
            WHERE idModelo_equipo IN (
                SELECT idModelo_Equipo FROM modelo_equipo 
                WHERE idMarca_Tipo_Equipo IN (
                    SELECT idMarcaTipo FROM marca_tipo_equipo 
                    WHERE idMarca_Equipo IN (%s)
                )
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 7: Eliminar modelos de equipos relacionados a la marca
        cur.execute("""
            DELETE FROM modelo_equipo 
            WHERE idMarca_Tipo_Equipo IN (
                SELECT idMarcaTipo FROM marca_tipo_equipo 
                WHERE idMarca_Equipo IN (%s)
            )
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 8: Eliminar relaciones en marca_tipo_equipo
        cur.execute("""
            DELETE FROM marca_tipo_equipo 
            WHERE idMarca_Equipo IN (%s)
        """ % ','.join(['%s'] * len(id_list)), id_list)

        # PASO 9: Finalmente, eliminar la marca en marca_equipo
        cur.execute("""
            DELETE FROM marca_equipo WHERE idMarca_Equipo IN (%s)
        """ % ','.join(['%s'] * len(id_list)), id_list)

        mysql.connection.commit()

        # Mensaje genérico
        flash(f"Se eliminaron {len(id_list)} marca(s) y sus relaciones asociadas exitosamente.", 'success')
        return redirect(url_for('marca_equipo.marcaEquipo'))
    except Exception as e:
        flash(f"Error al eliminar la(s) marca(s): {str(e)}", 'danger')
        return redirect(url_for('marca_equipo.marcaEquipo'))



