#se importa flask
from flask import Blueprint, render_template, request, url_for, redirect,flash, session, jsonify
#se importa db.py para utilizar la conexion a mysql
from db import mysql
#importamos el modulo que creamos
from funciones import validarChar, getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator


orden_compra = Blueprint('orden_compra', __name__, template_folder='app/templates')

#vista principal orden_compra
@orden_compra.route('/orden_compra')
@orden_compra.route('/orden_compra/<page>')
@loguear_requerido
def ordenCompra(page = 1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset = (page-1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(''' SELECT oc.idOrden_compra, oc.nombreOrden_compra, oc.fechacompraOrden_compra,oc.fechafin_ORDEN_COMPRA,oc.rutadocumentoOrden_compra,
                p.nombreProveedor, p.idProveedor, ta.idTipo_adquisicion, ta.nombre_tipo_adquisicion, oc.idProveedor, oc.idTipo_adquisicion
                from orden_compra oc
                inner join proveedor p on p.idProveedor = oc.idProveedor
                inner join tipo_adquisicion ta on ta.idTipo_adquisicion = oc.idTipo_adquisicion
                LIMIT %s OFFSET %s
    ''',(perpage, offset))
    data = cur.fetchall() 

    cur.execute('SELECT COUNT(*) FROM orden_compra')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    #Se generan mas consultas para rellenar los campos select en la vista.html 
    cur.execute('SELECT * FROM proveedor')
    #la variable puede llamarse de cualquier forma pero la llamamos data por lo general, si tenemos mas de una consulta generar otra variable con un nombre distinto
    datas = cur.fetchall()
    cur.execute('SELECT * FROM tipo_adquisicion')
    ta_data = cur.fetchall()
    cur.close()
    return render_template(
        'GestionP/orden_compra.html', 
        orden_compra = data, 
        proveedor = datas,
        tipo_adquisicion = ta_data,
        page=page, lastpage= page < (total/perpage)+1
        )

#agrega un registro para orden de compra
@orden_compra.route('/add_ordenc', methods = ['POST'])
@administrador_requerido
def add_ordenc():
    if request.method == 'POST':
        fecha_compra = request.form["fecha_compra_ordenc"],
        fecha_fin = request.form["fecha_fin_ordenc"] or None,

        data  = {
        'id_ordenc' : request.form["id_ordenc"],
        'nombre_ordenc' : request.form["nombre_ordenc"],
        'nombre_tipoa' : request.form["nombre_tipo_adquisicion_ordenc"],  
        'nombre_proveedor' : request.form["nombre_proveedor_ordenc"],
        }

        orden_compra_schema = {
            'id_ordenc': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9\\-\\s]*$'  # Permitir solo letras, números y espacios
            },
            'nombre_ordenc': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9 ]*$'  # Permitir solo letras, números y espacios
            },
            'nombre_tipoa': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
            },
            'nombre_proveedor': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
            }
        }
        v = Validator(orden_compra_schema)
        if not v.validate(data):
            errores = v.errors  # Obtiene los errores de validación
            mensajes_error = []

            for campo, mensaje in errores.items():
                # Personalizar el mensaje de error
                mensajes_error.append(f"Error en el campo '{campo}': {mensaje[0]}")

            # Combinar todos los errores en un solo mensaje
            mensaje_final = " | ".join(mensajes_error)
            flash(mensaje_final, "warning")
            return redirect(url_for('orden_compra.ordenCompra'))# Si el formulario no es válido


        
        try:      
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO orden_compra 
                        (idOrden_compra, nombreOrden_compra, fechacompraOrden_compra,fechafin_ORDEN_COMPRA,
                            idTipo_adquisicion,idProveedor) 
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ''', (data['id_ordenc'], data['nombre_ordenc'], fecha_compra, fecha_fin, data['nombre_tipoa'], data['nombre_proveedor']))
            
            cur.connection.commit()
            flash("Orden de compra agregada correctamente","success")
            return redirect(url_for('orden_compra.ordenCompra'))
        except Exception as e:
            error_message = str(e)
            if "1062" in error_message and "PRIMARY" in error_message:
                flash("Error: Ya existe una orden de compra con ese ID", "warning")
            else:
                flash(f"Error inesperado: {error_message}", "danger")
            return redirect(url_for('orden_compra.ordenCompra'))

#Envias datos a formulario editar
@orden_compra.route('/edit_ordenc/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_ordenc(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT oc.idOrden_compra, oc.nombreOrden_compra, oc.fechacompraOrden_compra, oc.fechafin_ORDEN_COMPRA, oc.rutadocumentoOrden_compra, p.nombreProveedor, p.idProveedor, ta.idTipo_adquisicion, ta.nombre_tipo_adquisicion
                    , oc.idProveedor, oc.idTipo_adquisicion
                    from orden_compra oc
                    inner join proveedor p on p.idProveedor = oc.idProveedor
                    inner join tipo_adquisicion ta on ta.idTipo_adquisicion = oc.idTipo_adquisicion
                    WHERE idOrden_compra = %s
        ''', (id,))
        data = cur.fetchall()
        cur.execute('SELECT * FROM proveedor')
        datas = cur.fetchall()
        cur.execute('SELECT * FROM tipo_adquisicion')
        dataso = cur.fetchall()
        cur.close()
        return render_template(
            'GestionP/editOrden_compra.html', 
            orden_compra = data[0], 
            tipo_adquisicion = dataso, 
            proveedor = datas
            )
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('orden_compra.ordenCompra'))
    
#actualizar
@orden_compra.route('/update_ordenc/<id>', methods=['POST'])
@administrador_requerido
def update_ordenc(id):
    if request.method == 'POST':
        # Obtener los datos del formulario
        try:
            fecha_compra_ordenc = request.form['fecha_compra_ordenc']
            fecha_fin_ordenc = request.form['fecha_fin_ordenc']
            data = {
                'id_orden_compra': request.form['id_orden_compra'],
                'nombre_ordenc': request.form['nombre_ordenc'],
                'nombre_tipo_adquisicion_ordenc': request.form['nombre_tipo_adquisicion_ordenc'],
                'nombre_proveedor_ordenc': request.form['nombre_proveedor_ordenc'],
            }

            # Esquema para validar los datos
            orden_compra_schema = {
                'id_orden_compra': {
                    'type': 'string',
                    'regex': '^[a-zA-Z0-9 -]*$'  # Permitir solo letras, números y espacios
                },
                'nombre_ordenc': {
                    'type': 'string',
                    'regex': '^[a-zA-Z0-9 ]*$'  # Permitir solo letras, números y espacios
                },
                'nombre_tipo_adquisicion_ordenc': {
                    'type': 'string',
                    'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
                },
                'nombre_proveedor_ordenc': {
                    'type': 'string',
                    'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
                }
            }

            # Validar los datos usando el esquema
            v = Validator(orden_compra_schema)
            if not v.validate(data):
                # Depuración de errores de validación
                flash(f"Errores en los datos proporcionados: {v.errors}")
                return redirect(url_for('orden_compra.ordenCompra'))

            # Depuración de datos validados
            print(f"Datos validados para la actualización: {data}")
            print(f"Fecha de compra: {fecha_compra_ordenc}, Fecha final: {fecha_fin_ordenc}")

            # Ejecutar la actualización en la base de datos
            cur = mysql.connection.cursor()
            cur.execute('''
            UPDATE orden_compra 
            SET idOrden_compra = %s,
                nombreOrden_compra = %s,
                fechacompraOrden_compra = %s,
                fechafin_ORDEN_COMPRA = %s,
                idProveedor = %s,
                idTipo_adquisicion = %s
            WHERE idOrden_compra = %s
            ''', (
                data['id_orden_compra'], 
                data['nombre_ordenc'], 
                fecha_compra_ordenc, 
                fecha_fin_ordenc, 
                data['nombre_proveedor_ordenc'], 
                data['nombre_tipo_adquisicion_ordenc'], 
                id
            ))
            mysql.connection.commit()

            # Confirmar éxito
            flash('Orden de compra actualizada correctamente')
            return redirect(url_for('orden_compra.ordenCompra'))

        except KeyError as key_error:
            # Depuración de error por falta de clave
            print(f"Faltan datos en el formulario: {key_error}")
            flash(f"Faltan datos obligatorios: {key_error}")
            return redirect(url_for('orden_compra.ordenCompra'))

        except Exception as e:
            # Depuración de errores generales
            print(f"Error durante la actualización: {e}")
            flash(f"Error al actualizar la orden de compra: {str(e)}")
            return redirect(url_for('orden_compra.ordenCompra'))

        
@orden_compra.route('/delete_ordenc', methods=['POST'])
@administrador_requerido
def delete_ordenc():
    try:
        data = request.get_json()
        id_list = data.get("ids", [])

        if not id_list:
            return jsonify({
                "status": "error",
                "message": "Debe seleccionar al menos una orden de compra para eliminar.",
                "tipo_alerta": "warning"
            }), 400

        cur = mysql.connection.cursor()

        # **PASO 1: Verificar si hay equipos en equipo_asignacion**
        cur.execute(f"""
            SELECT COUNT(*) AS total FROM equipo_asignacion 
            WHERE idEquipo IN (SELECT idEquipo FROM equipo WHERE idOrden_compra IN ({','.join(['%s'] * len(id_list))}))
        """, tuple(id_list))
        equipos_asignados = cur.fetchone()

        if equipos_asignados and equipos_asignados["total"] > 0:
            return jsonify({
                "status": "error",
                "message": "No se pueden eliminar órdenes de compra con equipos asignados. Debe reasignar o eliminar estos equipos primero.",
                "tipo_alerta": "warning"
            }), 400

        # **PASO 2: Eliminar equipos asociados a la orden de compra**
        cur.execute(f"""
            DELETE FROM equipo 
            WHERE idOrden_compra IN ({','.join(['%s'] * len(id_list))})
        """, tuple(id_list))

        # **PASO 3: Eliminar la orden de compra**
        cur.execute(f"""
            DELETE FROM orden_compra
            WHERE idOrden_compra IN ({','.join(['%s'] * len(id_list))})
        """, tuple(id_list))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": f"✅ Se eliminaron {len(id_list)} orden(es) de compra correctamente.",
            "tipo_alerta": "success"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"❌ Error al eliminar la orden de compra: {str(e)}",
            "tipo_alerta": "danger"
        }), 500
