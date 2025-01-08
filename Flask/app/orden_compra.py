#se importa flask
from flask import Blueprint, render_template, request, url_for, redirect,flash, session
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
                p.nombreProveedor, p.idProveedor, ta.idTipo_adquisicion, ta.nombreTipo_adquisicion, oc.idProveedor, oc.idTipo_adquisicion
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
    return render_template('orden_compra.html', orden_compra = data, proveedor = datas,
                            tipo_adquisicion = ta_data,
                            page=page, lastpage= page < (total/perpage)+1)

#agrega un registro para orden de compra
@orden_compra.route('/add_ordenc', methods = ['POST'])
@administrador_requerido
def add_ordenc():
    if request.method == 'POST':
        fecha_compra = request.form["fecha_compra_ordenc"],
        fecha_fin = request.form["fecha_fin_ordenc"],

        data  = {
        'id_ordenc' : request.form["id_ordenc"],
        'nombre_ordenc' : request.form["nombre_ordenc"],
        'nombre_tipoa' : request.form["nombre_tipo_adquisicion_ordenc"],  
        'nombre_proveedor' : request.form["nombre_proveedor_ordenc"],
        }

        orden_compra_schema = {
            'id_ordenc': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9 -]*$'  # Permitir solo letras, números y espacios
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
            flash("caracteres no permitidos")
            return redirect(url_for('orden_compra.ordenCompra'))

        
        try:      
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO orden_compra 
                        (idOrden_compra, nombreOrden_compra, fechacompraOrden_compra,fechafin_ORDEN_COMPRA,
                            idTipo_adquisicion,idProveedor) 
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ''', (data['id_ordenc'], data['nombre_ordenc'], fecha_compra, fecha_fin, data['nombre_tipoa'], data['nombre_proveedor']))
            
            cur.connection.commit()
            flash("Orden de compra agregada correctamente")
            return redirect(url_for('orden_compra.ordenCompra'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('orden_compra.ordenCompra'))
#Envias datos a formulario editar
@orden_compra.route('/edit_ordenc/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_ordenc(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(''' SELECT oc.idOrden_compra, oc.nombreOrden_compra, oc.fechacompraOrden_compra, oc.fechafin_ORDEN_COMPRA, oc.rutadocumentoOrden_compra, p.nombreProveedor, p.idProveedor, ta.idTipo_adquisicion, ta.nombreTipo_adquisicion
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
        return render_template('editOrden_compra.html', orden_compra = data[0], tipo_adquisicion = dataso, proveedor = datas)
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('orden_compra.ordenCompra'))
    
#actualizar
@orden_compra.route('/update_ordenc/<id>', methods = ['POST'])
@administrador_requerido
def update_ordenc(id):
    if request.method == 'POST':
        fecha_compra_ordenc = request.form['fecha_compra_ordenc'],
        fecha_fin_ordenc = request.form['fecha_fin_ordenc'],
        data ={
        'id_orden_compra' : request.form['id_orden_compra'],
        'nombre_ordenc' : request.form['nombre_ordenc'],
        'nombre_tipo_adquisicion_ordenc' : request.form['nombre_tipo_adquisicion_ordenc'],
        'nombre_proveedor_ordenc' : request.form['nombre_proveedor_ordenc'],
        }

        orden_compra_schema = {
            'id_orden_compra': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9 -]*$'  # Permitir solo letras, números y espacios
            },
            'nombre_ordenc': {
                'type': 'string',
                'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
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

        v = Validator(orden_compra_schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for('orden_compra.ordenCompra'))


        try:
            cur = mysql.connection.cursor()
            cur.execute('''
            UPDATE orden_compra 
            SET idOrden_compra = %s,
                nombreOrden_compra = %s,
                fechacompraOrden_compra = %s,
                fechafin_ORDEN_COMPRA= %s,
                idProveedor = %s,
                idTipo_adquisicion = %s
            WHERE idOrden_compra = %s
            ''', (data['nombre_ordenc'],data['nombre_tipo_adquisicion_ordenc'], data['nombre_proveedor_ordenc'],fecha_compra_ordenc, fecha_fin_ordenc, id))
            mysql.connection.commit()
            flash('Orden de compra actualizada correctamente')
            return redirect(url_for('orden_compra.ordenCompra'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('orden_compra.ordenCompra'))
        
#eliminar    
@orden_compra.route('/delete_ordenc/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_ordenc(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM orden_compra WHERE idOrden_compra = %s', (id,))
        mysql.connection.commit()
        flash('Orden de compra eliminado correctamente')
        return redirect(url_for('orden_compra.ordenCompra'))
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for('orden_compra.ordenCompra'))