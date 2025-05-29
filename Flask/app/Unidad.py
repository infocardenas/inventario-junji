from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify
from db import mysql
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator

Unidad = Blueprint('Unidad', __name__, template_folder = 'app/templates')

#ruta para poder enviar datos a la pagina principal de Unidad
@Unidad.route('/Unidad')
@loguear_requerido
def UNIDAD():
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT u.idUnidad, u.nombreUnidad, u.contactoUnidad,
               u.direccionUnidad, u.idComuna, co.nombreComuna, 
               COUNT(e.idEquipo) as num_equipos,
               mo.nombreModalidad, u.idModalidad
        FROM unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad
        LEFT JOIN equipo e on u.idUnidad = e.idUnidad
        GROUP BY u.idUnidad, u.nombreUnidad, u.contactoUnidad, u.direccionUnidad, 
                 u.idComuna, co.nombreComuna, mo.nombreModalidad, u.idModalidad
    """)
    
    data = cur.fetchall()  # Obtiene todas las unidades
    
    cur.execute('SELECT * FROM comuna')
    c_data = cur.fetchall()
    
    cur.execute("SELECT * FROM modalidad")
    modalidades_data = cur.fetchall()
    
    cur.close()
    
    return render_template('Organizacion/Unidad.html', Unidad=data, comuna=c_data, Modalidades=modalidades_data)


#ruta y metodo para poder agregar una Unidad
@Unidad.route('/add_Unidad', methods = ['POST'])
@administrador_requerido
def add_Unidad():
    if request.method == 'POST':
                # Imprimir datos recibidos para depuración
        print("Formulario recibido:", request.form)

        # Recoger datos del formulario
        id_modalidad = request.form.get('idModalidad', '').strip()

        # Verificar si el campo está vacío antes de convertir a entero
        if not id_modalidad.isdigit():
            flash("Error: Modalidad no válida")
            return redirect(url_for('Unidad.UNIDAD'))

        # Recoger datos del formulario
        data = {
            'codigoUnidad': request.form['codigo_unidad'], #DEBE SER IGUAL AL NAME DEL HTML
            'nombreUnidad': request.form['nombreUnidad'],
            'contactoUnidad': request.form['contactoUnidad'],
            'direccionUnidad': request.form['direccionUnidad'],
            'idComuna': int(request.form['idComuna']),
            'idModalidad': int(request.form['idModalidad'])
        }
        add_Unidad_schema = { #VALIDACION CADA DATO
            'codigoUnidad': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9 ]+$'  # Permitir solo alfanuméricos y espacios
            },
            'nombreUnidad': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 255,
                'required': True,  # Permitir solo alfanuméricos y espacios
            },
            'contactoUnidad': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 255,
                'required': True,
                'regex': '^[a-zA-Z0-9 ]+$'  # Permitir solo alfanuméricos y espacios
            },
            'direccionUnidad': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 255,
                'required': True,  # Permitir alfanuméricos, espacios, comas, puntos y guiones
            },
            'idComuna': {
                'type': 'integer',
                'required': True
            },
            'idModalidad': {
                'type': 'integer',
                'required': True
            }
        }
        # Validar datos
        v = Validator(add_Unidad_schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('Unidad.UNIDAD'))


        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO unidad (idUnidad, nombreUnidad, contactoUnidad, direccionUnidad, idComuna, idModalidad) VALUES (%s, %s, %s, %s, %s, %s)',
                       (data['codigoUnidad'], data['nombreUnidad'], data['contactoUnidad'], data['direccionUnidad'], data['idComuna'], data['idModalidad']))
            mysql.connection.commit()
            flash('Unidad agregada correctamente', 'success')
            return redirect(url_for('Unidad.UNIDAD'))
        except Exception as e:
            flash("Error al crear", 'danger')
            return redirect(url_for('Unidad.UNIDAD'))

#ruta para poder enviar los datos a la vista de edicion segun el id correspondiente
@Unidad.route('/edit_Unidad/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_Unidad(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
        SELECT *
        FROM unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        INNER JOIN modalidad mo on u.idModalidad =mo.idModalidad
        WHERE idUnidad = %s
        """, (id,))
        data = cur.fetchall()
        curs = mysql.connection.cursor()
        curs.execute('SELECT idComuna, nombreComuna FROM comuna')
        c_data = curs.fetchall()

        cur.execute("SELECT * FROM modalidad")
        modalidades_data = cur.fetchall()
        curs.close()
        return render_template('Organizacion/editUnidad.html', Unidad = data[0],
                comuna = c_data, Modalidades=modalidades_data)
    except Exception as e:
        flash("Error al crear")
        return redirect(url_for('Unidad.UNIDAD'))

# Actualiza los datos de Unidad según el id correspondiente
@Unidad.route('/update_Unidad/<id>', methods=['POST'])
@administrador_requerido
def update_Unidad(id):
    if request.method == 'POST':
        # Recoger datos del formulario
        data = {
            'codigo_Unidad': request.form['codigo_Unidad'],
            'nombreUnidad': request.form['nombreUnidad'],
            'contactoUnidad': request.form['contactoUnidad'],
            'direccionUnidad': request.form['direccionUnidad'],
            'idComuna': int(request.form['nombreComuna']),
            'idModalidad': int(request.form['idModalidad'])
        }

        update_Unidad_schema = {
            'codigo_Unidad': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9 ]+$'  # Permitir solo alfanuméricos y espacios
            },
            'nombreUnidad': {
                'type': 'string',  # Permitir solo alfanuméricos y espacios
            },
            'contactoUnidad': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9 ]+$', # Permitir solo alfanuméricos y espacios
            },
            'direccionUnidad': {
                'type': 'string',  # Permitir solo alfanuméricos y espacios
            },
            'idComuna': {
                'type': 'integer',
                'required': True
            },
            'idModalidad': {
                'type': 'integer',
                'required': True
            }
        }

        # Validar datos
        v = Validator(update_Unidad_schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('Unidad.UNIDAD'))

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE unidad
            SET idUnidad =%s,
                nombreUnidad = %s,
                contactoUnidad = %s,
                direccionUnidad = %s,
                idComuna = %s,
                idModalidad = %s
            WHERE idUnidad = %s
            """, (data['codigo_Unidad'], data['nombreUnidad'], data['contactoUnidad'],
                  data['direccionUnidad'], data['idComuna'], data['idModalidad'], id))
            mysql.connection.commit()
            flash('Unidad actualizada correctamente')
            return redirect(url_for('Unidad.UNIDAD'))
        except Exception as e:
            flash("Error al actualizar: " + str(e))  # Muestra el error para depuración
            return redirect(url_for('Unidad.UNIDAD'))

#Elimina un registro segun el id
@Unidad.route('/delete_Unidad/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_Unidad(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM unidad WHERE idUnidad = %s', (id,))
        mysql.connection.commit()
        flash('Unidad eliminada correctamente')
        return redirect(url_for('Unidad.UNIDAD'))
    except Exception as e:
        flash("NO se pudo eliminar la unidad, tiene equipos o funcionarios asociados")
        return redirect(url_for('Unidad.UNIDAD'))
    
@Unidad.route("/unidad/buscar_unidad/<id>")
@loguear_requerido
def buscar_unidad(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.idUnidad, u.nombreUnidad, u.contactoUnidad,
               u.direccionUnidad, u.idComuna, co.nombreComuna,
               co.idComuna, COUNT(e.idEquipo) as num_equipos,
               mo.nombreModalidad
        FROM unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad
        LEFT JOIN equipo e on u.idUnidad = e.idUnidad
        WHERE u.idUnidad = %s
        GROUP BY u.idUnidad, u.nombreUnidad, u.contactoUnidad, u.direccionUnidad, u.idComuna, co.nombreComuna, co.idComuna
                """, (id,))
    data = cur.fetchall()
    cur.execute("""
    SELECT *
    FROM comuna c
                """)
    c_data = cur.fetchall()
    cur.execute("""
    SELECT *
    FROM modalidad mo
                """)
    modalidades_data = cur.fetchall()

    return render_template('Organizacion/Unidad.html', Unidad = data, comuna = c_data,
        page=1, lastpage= True, Modalidades=modalidades_data)

@Unidad.route('/mostrar_funcionarios_unidad/<int:idUnidad>')
@loguear_requerido
def mostrar_funcionarios_unidad(idUnidad):
    try:
        cur = mysql.connection.cursor()
        
        # Obtener funcionarios de la unidad
        cur.execute("""
            SELECT rutFuncionario, nombreFuncionario, cargoFuncionario, correoFuncionario
            FROM funcionario
            WHERE idUnidad = %s
        """, (idUnidad,))
        funcionarios = cur.fetchall()
        
        # Obtener nombre de la unidad
        cur.execute("SELECT nombreUnidad FROM unidad WHERE idUnidad = %s", (idUnidad,))
        unidad = cur.fetchone()
        
        cur.close()
        
        return render_template('Organizacion/funcionarios_unidad.html', funcionarios=funcionarios, unidad=unidad)
    
    except Exception as e:
        flash(f"Error al obtener funcionarios: {str(e)}", 'danger')
        return redirect(url_for('Unidad.UNIDAD'))

@Unidad.route('/mostrar_equipos_unidad/<int:idUnidad>')
@loguear_requerido  # Asegúrate de tener esta función de autenticación
def mostrar_equipos_unidad(idUnidad):
    try:
        # Abre el cursor de la conexión a la base de datos
        cur = mysql.connection.cursor()

        # Realiza la consulta SQL para obtener los equipos de una unidad
        cur.execute("""
            SELECT 
                e.Cod_inventarioEquipo,
                e.Num_serieEquipo,
                est.nombreEstado_equipo AS estadoEquipo,
                f.nombreFuncionario,
                e.codigoproveedor_equipo,
                u.nombreUnidad,
                te.nombreTipo_equipo AS tipoEquipo,  
                mo.nombreModeloequipo AS modeloEquipo  -- Usamos el nombre correcto de la columna
            FROM equipo e
            LEFT JOIN estado_equipo est ON e.idEstado_equipo = est.idEstado_equipo
            LEFT JOIN funcionario f ON f.idUnidad = e.idUnidad
            LEFT JOIN unidad u ON e.idUnidad = u.idUnidad
            LEFT JOIN modelo_equipo mo ON e.idModelo_equipo = mo.idModelo_Equipo
            LEFT JOIN marca_tipo_equipo mte ON mo.idMarca_Tipo_Equipo = mte.idMarcaTipo  -- Correcto JOIN entre modelo_equipo y marca_tipo_equipo
            LEFT JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo  -- JOIN entre marca_tipo_equipo y tipo_equipo
            WHERE e.idUnidad = %s
        """, (idUnidad,))

        # Obtiene todos los resultados de la consulta
        equipos = cur.fetchall()

        # Cierra el cursor después de obtener los datos
        cur.close()

        # Renderiza la plantilla HTML con los datos obtenidos
        return render_template('Organizacion/equipos_unidad.html', equipos=equipos)

    except Exception as e:
        # En caso de error, muestra un mensaje de flash y redirige a la página de unidades
        flash(f"Error al obtener equipos: {str(e)}", 'danger')
        return redirect(url_for('Unidad.UNIDAD'))

@Unidad.route('/buscar_unidades', methods=['GET'])
@loguear_requerido
def buscar_unidades():
    query = request.args.get("q", "").lower()
    page = request.args.get("page", default=1, type=int)
    per_page = 8  # igual que DataTables, puedes ajustar

    offset = (page - 1) * per_page
    cur = mysql.connection.cursor()

    # Búsqueda por nombre, código, contacto, dirección o comuna
    cur.execute("""
        SELECT u.idUnidad, u.nombreUnidad, u.contactoUnidad,
               u.direccionUnidad, u.idComuna, co.nombreComuna, 
               COUNT(e.idEquipo) as num_equipos,
               mo.nombreModalidad, u.idModalidad
        FROM unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad
        LEFT JOIN equipo e on u.idUnidad = e.idUnidad
        WHERE LOWER(u.nombreUnidad) LIKE %s
           OR LOWER(u.idUnidad) LIKE %s
           OR LOWER(u.contactoUnidad) LIKE %s
           OR LOWER(u.direccionUnidad) LIKE %s
           OR LOWER(co.nombreComuna) LIKE %s
        GROUP BY u.idUnidad, u.nombreUnidad, u.contactoUnidad, u.direccionUnidad, 
                 u.idComuna, co.nombreComuna, mo.nombreModalidad, u.idModalidad
        LIMIT %s OFFSET %s
    """, (f"%{query}%",)*5 + (per_page, offset))
    unidades = cur.fetchall()

    # Total de resultados
    cur.execute("""
        SELECT COUNT(*) as total
        FROM unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        WHERE LOWER(u.nombreUnidad) LIKE %s
           OR LOWER(u.idUnidad) LIKE %s
           OR LOWER(u.contactoUnidad) LIKE %s
           OR LOWER(u.direccionUnidad) LIKE %s
           OR LOWER(co.nombreComuna) LIKE %s
    """, (f"%{query}%",)*5)
    total = cur.fetchone()["total"]
    total_pages = (total + per_page - 1) // per_page

    # Páginas visibles (como en equipo)
    visible_pages = []
    if total_pages <= 7:
        visible_pages = list(range(1, total_pages + 1))
    else:
        if page > 4:
            visible_pages.append(1)
            if page > 5:
                visible_pages.append("...")
        visible_pages.extend(range(max(1, page - 2), min(total_pages + 1, page + 3)))
        if page < total_pages - 3:
            if page < total_pages - 4:
                visible_pages.append("...")
            visible_pages.append(total_pages)

    return jsonify({
        "unidades": unidades,
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "visible_pages": visible_pages
    })

@Unidad.route('/buscar_equipos_unidad/<int:idUnidad>', methods=['GET'])
def buscar_equipos_unidad(idUnidad):
    query = request.args.get("q", "").lower()
    page = request.args.get("page", default=1, type=int)
    per_page = 8

    offset = (page - 1) * per_page
    cur = mysql.connection.cursor()

    # Búsqueda por inventario, serie, estado, funcionario, proveedor, tipo, modelo
    cur.execute("""
        SELECT 
            e.Cod_inventarioEquipo,
            e.Num_serieEquipo,
            est.nombreEstado_equipo AS estadoEquipo,
            f.nombreFuncionario,
            e.codigoproveedor_equipo,
            u.nombreUnidad,
            te.nombreTipo_equipo AS tipoEquipo,
            mo.nombreModeloequipo AS modeloEquipo
        FROM equipo e
        LEFT JOIN estado_equipo est ON e.idEstado_equipo = est.idEstado_equipo
        LEFT JOIN funcionario f ON f.idUnidad = e.idUnidad
        LEFT JOIN unidad u ON e.idUnidad = u.idUnidad
        LEFT JOIN modelo_equipo mo ON e.idModelo_equipo = mo.idModelo_Equipo
        LEFT JOIN marca_tipo_equipo mte ON mo.idMarca_Tipo_Equipo = mte.idMarcaTipo
        LEFT JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE e.idUnidad = %s AND (
            LOWER(e.Cod_inventarioEquipo) LIKE %s OR
            LOWER(e.Num_serieEquipo) LIKE %s OR
            LOWER(est.nombreEstado_equipo) LIKE %s OR
            LOWER(f.nombreFuncionario) LIKE %s OR
            LOWER(e.codigoproveedor_equipo) LIKE %s OR
            LOWER(te.nombreTipo_equipo) LIKE %s OR
            LOWER(mo.nombreModeloequipo) LIKE %s
        )
        LIMIT %s OFFSET %s
    """, (idUnidad,) + (f"%{query}%",)*7 + (per_page, offset))
    equipos = cur.fetchall()

    # Total de resultados
    cur.execute("""
        SELECT COUNT(*) as total
        FROM equipo e
        LEFT JOIN estado_equipo est ON e.idEstado_equipo = est.idEstado_equipo
        LEFT JOIN funcionario f ON f.idUnidad = e.idUnidad
        LEFT JOIN unidad u ON e.idUnidad = u.idUnidad
        LEFT JOIN modelo_equipo mo ON e.idModelo_equipo = mo.idModelo_Equipo
        LEFT JOIN marca_tipo_equipo mte ON mo.idMarca_Tipo_Equipo = mte.idMarcaTipo
        LEFT JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE e.idUnidad = %s AND (
            LOWER(e.Cod_inventarioEquipo) LIKE %s OR
            LOWER(e.Num_serieEquipo) LIKE %s OR
            LOWER(est.nombreEstado_equipo) LIKE %s OR
            LOWER(f.nombreFuncionario) LIKE %s OR
            LOWER(e.codigoproveedor_equipo) LIKE %s OR
            LOWER(te.nombreTipo_equipo) LIKE %s OR
            LOWER(mo.nombreModeloequipo) LIKE %s
        )
    """, (idUnidad,) + (f"%{query}%",)*7)
    total = cur.fetchone()["total"]
    total_pages = (total + per_page - 1) // per_page

    # Páginas visibles
    visible_pages = []
    if total_pages <= 7:
        visible_pages = list(range(1, total_pages + 1))
    else:
        if page > 4:
            visible_pages.append(1)
            if page > 5:
                visible_pages.append("...")
        visible_pages.extend(range(max(1, page - 2), min(total_pages + 1, page + 3)))
        if page < total_pages - 3:
            if page < total_pages - 4:
                visible_pages.append("...")
            visible_pages.append(total_pages)

    return jsonify({
        "equipos": equipos,
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "visible_pages": visible_pages
    })

@Unidad.route('/buscar_funcionarios_unidad/<int:idUnidad>', methods=['GET'])
def buscar_funcionarios_unidad(idUnidad):
    query = request.args.get("q", "").lower()
    page = request.args.get("page", default=1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT rutFuncionario, nombreFuncionario, cargoFuncionario, correoFuncionario
        FROM funcionario
        WHERE idUnidad = %s AND (
            LOWER(rutFuncionario) LIKE %s OR
            LOWER(nombreFuncionario) LIKE %s OR
            LOWER(cargoFuncionario) LIKE %s OR
            LOWER(correoFuncionario) LIKE %s
        )
        LIMIT %s OFFSET %s
    """, (idUnidad,) + (f"%{query}%",)*4 + (per_page, offset))
    funcionarios = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) as total
        FROM funcionario
        WHERE idUnidad = %s AND (
            LOWER(rutFuncionario) LIKE %s OR
            LOWER(nombreFuncionario) LIKE %s OR
            LOWER(cargoFuncionario) LIKE %s OR
            LOWER(correoFuncionario) LIKE %s
        )
    """, (idUnidad,) + (f"%{query}%",)*4)
    total = cur.fetchone()["total"]
    total_pages = (total + per_page - 1) // per_page

    visible_pages = []
    if total_pages <= 7:
        visible_pages = list(range(1, total_pages + 1))
    else:
        if page > 4:
            visible_pages.append(1)
            if page > 5:
                visible_pages.append("...")
        visible_pages.extend(range(max(1, page - 2), min(total_pages + 1, page + 3)))
        if page < total_pages - 3:
            if page < total_pages - 4:
                visible_pages.append("...")
            visible_pages.append(total_pages)

    return jsonify({
        "funcionarios": funcionarios,
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "visible_pages": visible_pages
    })
