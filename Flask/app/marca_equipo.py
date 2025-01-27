from flask import Blueprint, request, flash, render_template, redirect, url_for, g, session
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
        'maxlength': 100,
        'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
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
    #flash(order)
    query = 'SELECT * FROM marca_equipo '
    #if(order == "ASC"):
        ##flash("test")
        #query += "ORDER BY marca_equipo.nombreMarcaEquipo" 
    #elif(order == "DESC"):
        #query += "ORDER BY marca_equipo.nombreMarcaEquipo DESC"
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

#enviar datos a vista editar
@marca_equipo.route('/marca_equipo/edit_marca_equipo/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_marca_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM marca_equipo WHERE idMarca_Equipo = %s', (id,))
        data = cur.fetchall()
        return render_template(
            'Equipo/editMarca_equipo.html', 
            marca_equipo = data[0]
            )
    except Exception as e:
        #flash(e.args[1])
        flash("Error al editar la marca", 'danger')
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

#eliminar    
@marca_equipo.route('/marca_equipo/delete_marca_equipo/<ids>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_marca_equipo(ids):
    try:
        # Dividir los IDs separados por comas
        id_list = ids.split(',')
        
        # Crear una consulta SQL para eliminar múltiples IDs
        cur = mysql.connection.cursor()
        query = 'DELETE FROM marca_equipo WHERE idMarca_equipo IN (%s)' % ','.join(['%s'] * len(id_list))
        cur.execute(query, id_list)
        mysql.connection.commit()

        flash('Marcas eliminadas exitosamente', 'success')
        return redirect(url_for('marca_equipo.marcaEquipo'))
    except Exception as e:
    # Capturar el error completo
        error_message = f"Error al eliminar las marcas: {str(e)}"
        flash(error_message, 'danger')  # Mostrar el error completo en el flash
        print(error_message)  # Opcional: Imprimir el error en la consola del servidor para depuración
        return redirect(url_for('marca_equipo.marcaEquipo'))


