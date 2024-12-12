from flask import Blueprint, request, render_template, flash, url_for, redirect, session
from db import mysql
from funciones import validarRut, getPerPage, validarCorreo
from cuentas import loguear_requerido, administrador_requerido
funcionario = Blueprint('funcionario', __name__, template_folder='app/templates')
from cerberus import Validator

# Definir el esquema de validación para funcionario
schema_funcionario = {
    'rut_funcionario': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 12,  # Longitud máxima considerando el RUT con guion
        'regex': '^[0-9]+[-]?[0-9kK]$'  # Permitir números y el carácter '-'
    },
    'nombre_funcionario': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': '^[a-zA-Z]*$'  # Permitir solo letras y espacios
    },
    'cargo_funcionario': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': '^[a-zA-Z]*$'  # Permitir solo letras y espacios
    },
    'codigo_Unidad': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 10  
    },
    'correo_funcionario': {
        'type': 'string',
        'minlength': 5,
        'maxlength': 100,
        'regex': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[a-zA-Z]{2,}$'  # Permitir formato de correo electrónico
    }
}

#envias los datos a la vista pricipal de funcionario
@funcionario.route('/funcionario')
@funcionario.route('/funcionario/<page>')
@loguear_requerido
def Funcionario(page = 1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset = (page -1) * perpage 
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario, 
            f.idUnidad, u.idUnidad, u.nombreUnidad, f.correoFuncionario
    FROM funcionario f
    INNER JOIN unidad u on f.idUnidad = u.idUnidad
    LIMIT %s OFFSET %s 
    """, (perpage, offset))
    data = cur.fetchall()
    cur.execute('SELECT * FROM unidad')
    ubi_data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM funcionario')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    return render_template('funcionario.html', funcionario = data, 
                           Unidad = ubi_data, page=page, lastpage= page < (total/perpage)+1)


#agregar funcionario
@funcionario.route('/add_funcionario', methods = ['POST'])
@administrador_requerido
def add_funcionario():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
        data = {
            'rut_funcionario': request.form['rut_funcionario'],
            'nombre_funcionario': request.form['nombre_funcionario'],
            'cargo_funcionario': request.form['cargo_funcionario'],
            'codigo_Unidad': request.form['codigo_Unidad'],
            'correo_funcionario': request.form['correo_funcionario']
        }
        # Validar los datos usando Cerberus
        v = Validator(schema_funcionario)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('funcionario.Funcionario'))
        
    
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                        INSERT INTO funcionario 
                        (rutFuncionario, nombreFuncionario, 
                        cargoFuncionario, idUnidad, correoFuncionario) 
                        VALUES (%s, %s, %s, %s, %s)
                        """, 
            (data['rut_funcionario'], data['nombre_funcionario'], data['cargo_funcionario'], 
                data['codigo_Unidad'], data['correo_funcionario']))
            mysql.connection.commit()
            flash('Funcionario agregado correctamente')
            return redirect(url_for('funcionario.Funcionario'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('funcionario.Funcionario'))
    
#enviar datos a vista editar
@funcionario.route('/edit_funcionario/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_funcionario(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
        SELECT *
        FROM funcionario f
        INNER JOIN unidad u on f.idUnidad = u.idUnidad
        WHERE rutFuncionario = %s
        """, (id,))
        data = cur.fetchall()
        cur.execute('SELECT * from unidad')
        print(data) 
        ubi_data = cur.fetchall()
        return render_template('editFuncionario.html', funcionario = data[0], Unidad = ubi_data)
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('funcionario.Funcionario'))

#actualizar funcionario por id
@funcionario.route('/update_funcionario/<id>', methods = ['POST'])
@administrador_requerido
def update_funcionario(id):
    if request.method == 'POST':
        # Obtener los datos del formulario
        data = {
            'rut_funcionario': request.form['rut_funcionario'],
            'nombre_funcionario': request.form['nombre_funcionario'],
            'correo_funcionario': request.form['correo_funcionario'],
            'cargo_funcionario': request.form['cargo_funcionario'],
            'codigo_Unidad': request.form['codigo_Unidad']
        }

        # Validar los datos usando Cerberus
        v = Validator(schema_funcionario)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('funcionario.Funcionario'))


        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE funcionario
            SET rutFuncionario = %s,
                nombreFuncionario = %s,
                cargoFuncionario = %s,
                idUnidad = %s,
                correoFuncionario = %s
            WHERE rutFuncionario = %s
            """, (data["rut_funcionario"], data["nombre_funcionario"], data["cargo_funcionario"], 
                data["codigo_Unidad"], data["correo_funcionario"], id))
            mysql.connection.commit()
            flash('Funcionario actualizado correctamente')
        
            return redirect(url_for('funcionario.Funcionario'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('funcionario.Funcionario'))

#eliminar registro segun id
@funcionario.route('/delete_funcionario/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_funcionario(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM funcionario WHERE rutFuncionario = %s', (id,))
        mysql.connection.commit()
        flash('Funcionario eliminado correctamente')
        return redirect(url_for('funcionario.Funcionario'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('funcionario.Funcionario'))

@funcionario.route("/funcionario/buscar_funcionario/<id>")
@loguear_requerido
def buscar_funcionario(id):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT * 
    FROM funcionario f
    INNER JOIN unidad u on f.idUnidad = u.idUnidad
    WHERE f.rutFuncionario = %s
    """, (id,))
    funcionarios = cur.fetchall()

    cur.execute("""
    SELECT *
    FROM unidad u 
                """)
    unidades = cur.fetchall()
    return render_template('funcionario.html', funcionario = funcionarios, 
                           Unidad = unidades, page=1, lastpage=True)