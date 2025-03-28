from flask import Blueprint, request, render_template, flash, url_for, redirect, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator
from MySQLdb import IntegrityError

funcionario = Blueprint('funcionario', __name__, template_folder='app/templates')

# Esquemas de validación
schema_agregar_funcionario = {
    'rut_funcionario': {
        'type': 'string',
        'minlength': 9,
        'maxlength': 10,
        'regex': r'^\d{7,8}(-[0-9kK]{1})?$'  # Aceptar formato 1234567-K o 12345678-9
    },
    'nombre_funcionario': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'  # Permitir letras, tildes y espacios
    },
    'cargo_funcionario': {
        'type': 'string',
        'allowed': ['ADMINISTRATIVO', 'AUXILIAR', 'PROFESIONAL', 'TÉCNICO', 'DIRECTOR REGIONAL','JARDIN'],  # Valores permitidos
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
        'regex': r'^[a-zA-Z0-9._%+-]+@(junji\.cl|junjired\.cl)$'  # Permitir formato de correo electrónico
    }
}

schema_editar_funcionario = schema_agregar_funcionario.copy()
schema_editar_funcionario['rut_actual'] = {
    'type': 'string',
    'minlength': 9,
    'maxlength': 10,
    'regex': r'^\d{7,8}-[0-9kK]$'
}

# Vista principal de funcionario
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

    # Consulta que obtiene funcionarios y cuenta las asignaciones activas
    cur.execute("""
    SELECT 
        f.rutFuncionario,
        f.nombreFuncionario,
        f.cargoFuncionario, 
        f.idUnidad,
        u.idUnidad,
        u.nombreUnidad,
        f.correoFuncionario,
        COALESCE((SELECT COUNT(*)
                    FROM asignacion a
                    JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
                    WHERE a.rutFuncionario = f.rutFuncionario
                    AND a.ActivoAsignacion = 1), 0) AS equipos_asignados
    FROM funcionario f
    JOIN unidad u ON f.idUnidad = u.idUnidad
    LIMIT %s OFFSET %s
    """, (perpage, offset))
    data = cur.fetchall()

    # Consulta para ver que equipos asignados tiene cada funcionario
    for funcionario in data:
        cur.execute("""
            SELECT 
                te.nombreTipo_equipo,
                mae.nombreMarcaEquipo,
                me.nombreModeloequipo,
                e.Cod_inventarioEquipo,
                e.Num_serieEquipo
            FROM asignacion a
            JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
            JOIN equipo e ON ea.idEquipo = e.idEquipo
            JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
            JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
            JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
            JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
            WHERE a.rutFuncionario = %s AND a.ActivoAsignacion = 1
        """, (funcionario["rutFuncionario"],))
        
        equipos_asignados = cur.fetchall()
        funcionario["equipos_detalle"] = equipos_asignados

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

@funcionario.route('/add_funcionario', methods=['POST'])
@administrador_requerido
def add_funcionario():
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        rut_funcionario = request.form.get('rut_funcionario', '').strip()
        nombre_funcionario = request.form.get('nombre_funcionario', '').strip()
        cargo_funcionario = request.form.get('cargo_funcionario', '').strip()
        codigo_Unidad = request.form.get('codigo_Unidad', '').strip()
        correo_funcionario = request.form.get('correo_funcionario', '').strip()

        # Eliminar puntos y guiones del RUT
        rut_funcionario = rut_funcionario.replace('.', '').replace('-', '')

        # Validación de longitud del RUT
        if len(rut_funcionario) < 7 or len(rut_funcionario) > 8:
            flash("Error: El RUT debe contener entre 7 y 8 dígitos", 'warning')
            return redirect(url_for('funcionario.Funcionario'))

        # Si el cargo es "JARDIN", no requerimos el guion ni el DV
        if cargo_funcionario == "JARDIN":
            rut_funcionario = rut_funcionario.split('-')[0]  # Eliminar el DV si es jardín

        # Validar los datos con el esquema
        data = {
            'rut_funcionario': rut_funcionario,
            'nombre_funcionario': nombre_funcionario,
            'cargo_funcionario': cargo_funcionario,
            'codigo_Unidad': codigo_Unidad,
            'correo_funcionario': correo_funcionario
        }

        v = Validator(schema_agregar_funcionario)
        if not v.validate(data):
            errores = v.errors
            for campo, mensaje in errores.items():
                flash(f"Error en '{campo}': {mensaje[0]}", 'warning')
            return redirect(url_for('funcionario.Funcionario'))
        
        try:
            # Insertar los datos en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("""
                        INSERT INTO funcionario 
                        (rutFuncionario, nombreFuncionario, 
                        cargoFuncionario, idUnidad, correoFuncionario) 
                        VALUES (%s, %s, %s, %s, %s)
                        """, 
                        (rut_funcionario, nombre_funcionario, 
                         cargo_funcionario, codigo_Unidad, 
                         correo_funcionario))
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
        
# Editar funcionario
@funcionario.route('/edit_funcionario', methods=['POST'])
@administrador_requerido
def edit_funcionario():
    if "user" not in session:
        flash("No estás autorizado para ingresar a esta ruta", 'warning')
        return redirect("/ingresar")
    
    try:
        data = {
            'rut_actual': request.form.get('edit_rut_actual', '').strip(),
            'rut_funcionario': request.form.get('rut_completo', '').strip(),
            'nombre_funcionario': request.form.get('nombre_funcionario', '').strip(),
            'correo_funcionario': request.form.get('correo_funcionario', '').strip(),
            'cargo_funcionario': request.form.get('cargo_funcionario', '').strip(),
            'codigo_Unidad': request.form.get('codigo_Unidad', '').strip()
        }

        # Valida que los campos no estén vacíos
        if not all(data.values()):
            flash("Todos los campos son obligatorios", 'warning')
            return redirect(url_for('funcionario.Funcionario'))

        validator = Validator(schema_editar_funcionario)
        if not validator.validate(data):
            # Obtiene el primer campo con error y su mensaje
            campo, mensajes = next(iter(validator.errors.items()))
            flash(f"Error en {campo}: {mensajes[0]}", 'warning')  # Muestra solo el primer error
            return redirect(url_for('funcionario.Funcionario'))


        # Actualizar el funcionario en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE funcionario
            SET rutFuncionario = %s, nombreFuncionario = %s, correoFuncionario = %s, 
                cargoFuncionario = %s, idUnidad = %s
            WHERE rutFuncionario = %s
        """, (data['rut_funcionario'], data['nombre_funcionario'], data['correo_funcionario'], data['cargo_funcionario'], data['codigo_Unidad'], data['rut_actual']))
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
        flash(e.args[1], 'warning')
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

