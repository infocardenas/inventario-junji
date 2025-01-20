from flask import Blueprint, request, render_template, flash, url_for, redirect, session
from db import mysql
from funciones import validarRut, getPerPage, validarCorreo
from cuentas import loguear_requerido, administrador_requerido
funcionario = Blueprint('funcionario', __name__, template_folder='app/templates')
from cerberus import Validator
from MySQLdb import IntegrityError 

# Definir el esquema de validación para funcionario
schema_funcionario = {
    'rut_funcionario': {
        'type': 'string',
        'minlength': 9,
        'maxlength': 10,
        'regex': r'^\d{7,8}-[0-9kK]$'  # Aceptar formato 1234567-K o 12345678-9
    },
    'nombre_funcionario': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$'  # Permitir letras, tildes y espacios
    },
    'cargo_funcionario': {
        'type': 'string',
        'allowed': ['ADMINISTRATIVO', 'AUXILIAR', 'PROFESIONAL', 'TECNICO'],  # Valores permitidos
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
        'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Permitir formato de correo electrónico
    }
}

#envias los datos a la vista pricipal de funcionario
@funcionario.route('/funcionario')
@funcionario.route('/funcionario/<page>')
@loguear_requerido
def Funcionario(page = 1):
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
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
    return render_template(
        'GestionR.H/funcionario.html', 
        funcionario = data, 
        Unidad = ubi_data, 
        page=page, lastpage= page < (total/perpage)+1
        )


#agregar funcionario
@funcionario.route('/add_funcionario', methods=['POST'])
@administrador_requerido
def add_funcionario():
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    
    if request.method == 'POST':
        data = {
            'rut_funcionario': request.form.get('rut_funcionario', '').strip(),
            'nombre_funcionario': request.form.get('nombre_funcionario', '').strip(),
            'cargo_funcionario': request.form.get('cargo_funcionario', '').strip(),
            'codigo_Unidad': request.form.get('codigo_Unidad', '').strip(),
            'correo_funcionario': request.form.get('correo_funcionario', '').strip()
        }

        # Validar los datos usando Cerberus
        v = Validator(schema_funcionario)
        if not v.validate(data):
            errores = v.errors  # Diccionario con los errores específicos por campo
            for campo, mensaje in errores.items():
                print(campo)
                print(mensaje)
                if "min length is 9" in mensaje:
                    flash("Error: El RUT ingresado debe contener 7 u 8 dígitos", 'warning')
                else:
                    flash(f"Error en '{campo}': {mensaje[0]}", 'warning')
            return redirect(url_for('funcionario.Funcionario'))
        
        try:
            # Insertar datos en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("""
                        INSERT INTO funcionario 
                        (rutFuncionario, nombreFuncionario, 
                        cargoFuncionario, idUnidad, correoFuncionario) 
                        VALUES (%s, %s, %s, %s, %s)
                        """, 
                        (data['rut_funcionario'], data['nombre_funcionario'], 
                         data['cargo_funcionario'], data['codigo_Unidad'], 
                         data['correo_funcionario']))
            mysql.connection.commit()
            flash('Funcionario agregado correctamente', "success")
            return redirect(url_for('funcionario.Funcionario'))
        
        except IntegrityError as e:
            error_message = str(e)
            if "Duplicate entry" in error_message:
                if "PRIMARY" in error_message:
                    flash("Error: El RUT ya está registrado", 'warning')
                elif "correoFuncionario" in error_message:
                    flash("Error: El correo electrónico ya está registrado", 'warning')
                else:
                    flash("Error de duplicación en la base de datos", 'warning')
            else:
                flash("Error de integridad en la base de datos", 'danger')
            return redirect(url_for('funcionario.Funcionario'))
        
        except Exception as e:
            flash(f"Error al crear el funcionario: {str(e)}", 'danger')
            return redirect(url_for('funcionario.Funcionario'))

@funcionario.route('/edit_funcionario', methods=['POST'])
@administrador_requerido
def edit_funcionario():
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    
    try:
        # Obtener datos del formulario
        rut_actual = request.form.get('rut_actual').strip()  # RUT actual almacenado
        nuevo_rut = request.form.get('rut_completo').strip()  # Nuevo RUT enviado por el formulario
        nombre_funcionario = request.form.get('nombre_funcionario').strip()
        correo_funcionario = request.form.get('correo_funcionario').strip()
        cargo_funcionario = request.form.get('cargo_funcionario').strip()
        codigo_unidad = request.form.get('codigo_Unidad').strip()

        # Validar datos básicos
        if not rut_actual or not nuevo_rut or not nombre_funcionario or not correo_funcionario or not cargo_funcionario or not codigo_unidad:
            flash("Todos los campos son obligatorios", 'warning')
            return redirect(url_for('funcionario.Funcionario'))
        
        # Actualizar el funcionario en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE funcionario
            SET rutFuncionario = %s, nombreFuncionario = %s, correoFuncionario = %s, 
                cargoFuncionario = %s, idUnidad = %s
            WHERE rutFuncionario = %s
        """, (nuevo_rut, nombre_funcionario, correo_funcionario, cargo_funcionario, codigo_unidad, rut_actual))
        mysql.connection.commit()
        cur.close()

        flash("Funcionario editado exitosamente", 'success')
        return redirect(url_for('funcionario.Funcionario'))

    except Exception as e:
        flash(f"Error al editar el funcionario: {str(e)}", 'danger')
        return redirect(url_for('funcionario.Funcionario'))

#eliminar registro segun id
@funcionario.route('/delete_funcionario/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_funcionario(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM funcionario WHERE rutFuncionario = %s', (id,))
        mysql.connection.commit()
        flash('Funcionario eliminado correctamente', 'success')
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
    FROM (
        SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario, 
            f.idUnidad, u.idUnidad, u.nombreUnidad, f.correoFuncionario
        FROM funcionario f
        INNER JOIN unidad u on f.idUnidad = u.idUnidad
        WHERE f.rutFuncionario = %s
        UNION ALL
        SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario, 
            f.idUnidad, u.idUnidad, u.nombreUnidad, f.correoFuncionario
        FROM funcionario f
        INNER JOIN unidad u on f.idUnidad = u.idUnidad
        WHERE f.correoFuncionario = %s)
    """, (id, id))
    funcionarios = cur.fetchall()

    cur.execute("""
    SELECT *
    FROM unidad u 
                """)
    unidades = cur.fetchall()
    return render_template(
        'GestionR.H/funcionario.html', 
        funcionario = funcionarios, 
        Unidad = unidades, 
        page=1, lastpage=True
        )

