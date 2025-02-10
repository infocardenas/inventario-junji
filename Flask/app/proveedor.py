#se importa flask
from flask import Blueprint, render_template, request, url_for, redirect,flash, session, jsonify
#se importa dependencias para conexion con mysql
from db import mysql
#importamos el modulo que creamos
from funciones import validarChar, getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator
from MySQLdb import IntegrityError
proveedor = Blueprint('proveedor', __name__, template_folder='app/templates')

# Definir el esquema de validación para el proveedor
schema_proveedor = {
    'nombre_proveedor': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': '^[a-zA-Z0-9 ]*$'  # Permitimos letras, números y espacios
    }
}

#se especifica la ruta principal para la vista de proveedor 
@proveedor.route('/proveedor', methods=['GET'])
@proveedor.route('/proveedor/<int:page>', methods=['GET'])
@loguear_requerido
def Proveedor(page=1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()
    # Obtener la lista de proveedores con paginación
    cur.execute('SELECT * FROM proveedor LIMIT %s OFFSET %s', (perpage, offset))
    data = cur.fetchall()

    # Contar el total de proveedores
    cur.execute('SELECT COUNT(*) FROM proveedor')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])

    return render_template(
        'GestionP/proveedor.html',
        proveedor=data,
        page=page,
        lastpage=page < (total / perpage) + 1
    )


#se especifica la ruta para agregar proveedores, como tambien el metodo por el cual extrae los datos desde el formulario
@proveedor.route('/add_proveedor', methods=['POST'])  
@administrador_requerido
def add_proveedor():       
    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "No estás autorizado para esta acción.",
            "tipo_alerta": "warning"
        }), 403

    if request.method == 'POST':
        data = {
            'nombre_proveedor': request.form['nombre_proveedor'].strip()
        }

        # Validar los datos usando Cerberus
        v = Validator(schema_proveedor)
        if not v.validate(data):
            return jsonify({
                "status": "error",
                "message": "Nombre inválido: Caracteres no permitidos.",
                "tipo_alerta": "warning"
            }), 400

        try:
            cur = mysql.connection.cursor()

            # **Comprobar si el proveedor ya existe antes de insertarlo**
            cur.execute("SELECT idProveedor FROM proveedor WHERE nombreProveedor = %s", (data["nombre_proveedor"],))
            resultado = cur.fetchone()

            if resultado:
                return jsonify({
                    "status": "error",
                    "message": "Error: El proveedor ya existe. Elige otro nombre.",
                    "tipo_alerta": "warning"
                }), 400

            # **Si no existe, lo insertamos**
            cur.execute("INSERT INTO proveedor (nombreProveedor) VALUES (%s)", (data["nombre_proveedor"],))
            mysql.connection.commit()

            return jsonify({
                "status": "success",
                "message": "Proveedor agregado exitosamente.",
                "tipo_alerta": "success"
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al crear el proveedor: {str(e)}",
                "tipo_alerta": "danger"
            }), 500

#ruta para enviar datos a la vista de editarProveedor con el id correspondiente
@proveedor.route('/edit_proveedor/<id>', methods=['GET', 'POST'])
@administrador_requerido
def edit_proveedor(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM proveedor WHERE idProveedor = %s', (id,))
        data = cur.fetchall()

        # Renderizar la plantilla principal con los datos del proveedor
        return render_template(
            'GestionP/proveedor.html',
            editar_proveedor=data  # Pasar datos del proveedor a editar
        )
    except Exception as e:
        print(f"Error al obtener proveedor: {e}")
        flash("Error al cargar los datos del proveedor")
        return redirect(url_for('proveedor.Proveedor'))



#ruta para poder actualizar los datos de proveedor dependiendo del id
@proveedor.route('/update_proveedor/<id>', methods=['POST'])
@administrador_requerido
def actualizar_proveedor(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")

    try:
        # Imprimir ID recibido
        print(f"ID del proveedor recibido: {id}")

        # Obtener el dato del formulario
        nombre_proveedor = request.form.get('nombre_proveedor', '').strip()

        # Imprimir datos recibidos del formulario
        print(f"Nombre del proveedor recibido: {nombre_proveedor}")

        # Validar el dato
        data = {'nombre_proveedor': nombre_proveedor}
        v = Validator(schema_proveedor)
        if not v.validate(data):
            print(f"Errores de validación: {v.errors}")
            flash("Caracteres no permitidos")
            return redirect(url_for('proveedor.Proveedor'))

        # Ejecutar la actualización en la base de datos
        cur = mysql.connection.cursor()
        query = """
            UPDATE proveedor 
            SET nombreProveedor = %s
            WHERE idProveedor = %s
        """
        print(f"Consulta SQL: {query}")
        print(f"Parámetros: (nombreProveedor={nombre_proveedor}, idProveedor={id})")
        
        cur.execute(query, (nombre_proveedor, id))
        mysql.connection.commit()

        # Confirmar que la actualización se realizó
        cur.execute('SELECT * FROM proveedor WHERE idProveedor = %s', (id,))
        proveedor_actualizado = cur.fetchone()
        print(f"Proveedor después de la actualización: {proveedor_actualizado}")

        flash('Proveedor actualizado correctamente')
        return redirect(url_for('proveedor.Proveedor'))

    except Exception as e:
        print(f"Error al actualizar proveedor: {e}")
        flash("Error al actualizar el proveedor")
        return redirect(url_for('proveedor.Proveedor'))


    
@proveedor.route('/delete_proveedor', methods=['POST'])
@administrador_requerido
def delete_proveedor():
    if "user" not in session:
        return jsonify({
            "status": "error",
            "message": "No estás autorizado para esta acción.",
            "tipo_alerta": "warning"
        }), 403

    try:
        data = request.get_json()
        id_list = data.get("ids", [])

        if not id_list:
            return jsonify({
                "status": "error",
                "message": "Debe seleccionar al menos un proveedor para eliminar.",
                "tipo_alerta": "warning"
            }), 400

        cur = mysql.connection.cursor()

        # **PASO 1: Eliminar órdenes de compra relacionadas**
        cur.execute("DELETE FROM orden_compra WHERE idProveedor IN (%s)" % ','.join(['%s'] * len(id_list)), tuple(id_list))

        # **PASO 2: Eliminar los proveedores**
        cur.execute("DELETE FROM proveedor WHERE idProveedor IN (%s)" % ','.join(['%s'] * len(id_list)), tuple(id_list))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": f"Se eliminaron {len(id_list)} proveedor(es) correctamente.",
            "tipo_alerta": "success"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al eliminar el proveedor: {str(e)}",
            "tipo_alerta": "danger"
        }), 500
