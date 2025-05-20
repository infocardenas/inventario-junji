from functools import wraps
from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file, jsonify, session
from . import mysql, bcrypt
from .funciones import getPerPage
import datetime
from cerberus import Validator

cuentas = Blueprint("cuentas", __name__, template_folder="app/templates")

#definir decorador para ingresar
#no se lo que significa el * antes del atributo, (puntero ¿?)
def loguear_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kargs):
        #print("DECORATOR 1")
        if "user" not in session:
            flash("Necesita estar logueado para acceder a esta ruta")
            return redirect("/ingresar")
        return f(*args, **kargs)
    return decorated_function

#definir decorador para ingresar
#no se lo que significa el * antes del atributo, (puntero ¿?)
def administrador_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kargs):
        #print("DECORATOR 2")
        #print(session)
        #print(session['privilegio'])
        if "user" not in session:
            flash("Necesita estar logueado para acceder a esta ruta")
            return redirect("/ingresar")
        
        if session['privilegio'] == 1:
            #print("test")
            return f(*args, **kargs)
        
        flash("Se nesesita ser administrador para usar esta funcion")
        return redirect("/ingresar")
    return decorated_function

@cuentas.route("/ingresar")
def Ingresar():
    return render_template("login.html")

@cuentas.route("/loguear", methods=["POST"])
def loguear():
    nombreUsuario = request.form['nombreUsuario']
    contrasenna = request.form['contrasenna']
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT *
    FROM usuario u
    WHERE u.nombreUsuario = %s
                """, (nombreUsuario,))
    #se usa fetchall para que el resultado este en forma de tupla.
    #para revisar el tamaño de esta
    usuario = cur.fetchall()
    if len(usuario) != 1:
        flash("Nombre de usuario o contraseña incorrecta", 'warning')
        return redirect("/ingresar")
    usuario = usuario[0]
    if bcrypt.check_password_hash(usuario['contrasennaUsuario'], contrasenna):
        session["user"] = nombreUsuario
        session["privilegio"] = usuario['privilegiosAdministrador']
        return redirect("/")
    else:
        flash("Nombre de usuario o contraseña incorrecta", 'warning')
        return redirect("/ingresar")

@cuentas.route("/registrar", methods=["GET", "POST"])
def registrar():
    if session['privilegio'] != 1:
        flash("no tiene los privilegios")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT *
    FROM usuario
                """)
    usuarios = cur.fetchall()
    print(usuarios)
    return render_template(
        "register.html", 
        usuarios=usuarios)

@cuentas.route("/crear_cuenta", methods=["GET", "POST"])
@administrador_requerido
def crear_cuenta():
    # Captura de datos correctamente
    data = {
        'nombreUsuario': request.form['nombreUsuario'],
        'contrasenna': request.form['contrasenna'],
        'contrasenna2': request.form['repetir'],
    }

    # Obtener el valor directamente del <select>
    privilegios_admin = request.form.get("privilegiosAdministrador", type=int)

    # Validación de datos
    schema = {
        'nombreUsuario': {
            'required': True,
            'type': 'string',
            'regex': '^[a-zA-Z0-9@.\s]+$'
        },
        'contrasenna': {
            'required': True,
            'type': 'string',
            'regex': '^[a-zA-Z0-9!@#$%^&*]+$'
        },
        'contrasenna2': {
            'required': True,
            'type': 'string',
            'regex': '^[a-zA-Z0-9!@#$%^&*]+$'
        }
    }

    v = Validator(schema)
    if not v.validate(data):
        flash("Caracteres no permitidos","warning")
        return redirect(url_for('cuentas.registrar'))

    # Validación de contraseñas iguales
    if data['contrasenna'] != data['contrasenna2']:
        flash("Las contraseñas son diferentes","warning")
        return redirect("/registrar")

    # Verificar si el usuario ya existe
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * 
        FROM usuario u
        WHERE u.nombreUsuario = %s
    """, (data['nombreUsuario'],))  # Corregido: ahora se pasa el valor correcto
    usuarios = cur.fetchall()

    if len(usuarios) == 1:
        flash("El usuario ya existe, ingrese un nombre distinto","warning")
        return redirect("/registrar")

    # Encriptar contraseña correctamente
    contraseña_hashed = bcrypt.generate_password_hash(data['contrasenna']).decode('utf-8')

    # Insertar usuario en la base de datos
    cur.execute("""
        INSERT INTO usuario(
            nombreUsuario,
            contrasennaUsuario,
            privilegiosAdministrador
        ) VALUES (%s, %s, %s)
    """, (data['nombreUsuario'], contraseña_hashed, privilegios_admin))
    
    mysql.connection.commit()
    flash("Usuario creado con exito", "success")
    return redirect("/registrar")


@cuentas.route("/protected")
@loguear_requerido
@administrador_requerido
def protected():
    print("logueado")
    return "good"
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    else:
        flash("you are authorized")
        return redirect("/")

@cuentas.route("/desloguear")
@loguear_requerido
def desloguear():
    session.pop("user", None)
    return redirect("/ingresar")

@cuentas.route("/edit_usuario/<nombreUsuario>")
@administrador_requerido
def edit_usuario(nombreUsuario):
    #redirect to edit page

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT *
    FROM usuario u
    WHERE u.nombreUsuario = %s
                """, (nombreUsuario,))
    usuario = cur.fetchone()
    return render_template('edit_cuenta.html', usuario=usuario)

@cuentas.route("/update_usuario_contrasenna/<nombre_usuario>", methods=["POST"])
@administrador_requerido
def edit_contrasenna(nombre_usuario):
    #comprobar que la contraseña antigua es correcta
    contrasenna_vieja = request.form['contranna_vieja']
    contrasenna_nueva = request.form['contrasenna_nueva']

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT *
    FROM usuario u
    WHERE u.nombreUsuario = %s
    """, (nombre_usuario,))
    Usuario = cur.fetchone()
    if bcrypt.check_password_hash(Usuario['contrasennaUsuario'], contrasenna_vieja):
        #cambiar la contraseña
        contrasennaHasheada = bcrypt.generate_password_hash(contrasenna_nueva).decode('utf-8')
        cur.execute("""
        UPDATE usuario SET
        contrasennaUsuario = %s 
        WHERE usuario.nombreUsuario = %s
        """, (contrasennaHasheada, nombre_usuario))
        mysql.connection.commit()
        flash("se cambio la contraseña")
        return redirect("/registrar")
    flash("la contraseña ingresada es incorrecta")
    return redirect("/registrar")
    




    pass

@cuentas.route("/update_usuario/<nombreUsuario>", methods=["POST"])
@administrador_requerido
def update_usuario(nombreUsuario):
    # Capturar datos del formulario
    nombreUsuarioNuevo = request.form['nombreUsuario']
    privilegios_admin = request.form.get('privilegiosAdministrador', type=int)

    # Actualizar el usuario en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE usuario
        SET nombreUsuario = %s,
            privilegiosAdministrador = %s
        WHERE nombreUsuario = %s
    """, (nombreUsuarioNuevo, privilegios_admin, nombreUsuario))

    mysql.connection.commit()
    flash("Usuario actualizado correctamente")
    return redirect("/registrar")



@cuentas.route("/delete_usuario/<nombreUsuario>", methods=["GET", "POST"])
@administrador_requerido
def delete_usuario(nombreUsuario):
    cur = mysql.connection.cursor()
    cur.execute("""
    DELETE FROM usuario
    WHERE nombreUsuario = %s
                """, (nombreUsuario,))
    mysql.connection.commit()
    flash("usuario ha sido eliminado","success")
    return redirect("/registrar")