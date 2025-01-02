from functools import wraps
from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file, jsonify, session
from db import mysql, bcrypt
from funciones import getPerPage
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
            flash("Nesesita estar logueado para usar esta ruta")
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
            flash("Nesesita estar logueado para usar esta ruta")
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
        flash("contraseña o usuario incorectos")
        return redirect("/ingresar")
    usuario = usuario[0]
    if bcrypt.check_password_hash(usuario['contrasennaUsuario'], contrasenna):
        session["user"] = nombreUsuario
        session["privilegio"] = usuario['privilegiosAdministrador']
        return redirect("/")
    else:
        flash("contraseña o usuario incorectos")
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
    return render_template("register.html", usuarios=usuarios)

@cuentas.route("/crear_cuenta", methods=["GET", "POST"])
@administrador_requerido
def crear_cuenta():
    data={
    'nombreUsuario' : request.form['nombreUsuario'],
    'contrasenna' : request.form['contrasenna'],
    'contrasenna2 ': request.form['repetir']
    }
    isAdmin = request.form.get("isAdmin")

    schema = {
        'nombreUsuario' : {
            'required' : True,
            'type' : 'string',
            'regex' : '^[a-zA-Z0-9@.]+$'},
        'contrasenna' : {
            'required' : True,
            'type' : 'string',
            'regex' : '^[a-zA-Z0-9!@#$%^&*]+$'},
        'contrasenna2' : {
            'required' : True,
            'type' : 'string',
            'regex' : '^[a-zA-Z0-9!@#$%^&*]+$'}, 
    }
    v = Validator(schema)
    if not v.validate(data):
        flash("caracteres no permitidos")
        return redirect(url_for('cuentas.registrar'))
    
    if isAdmin == "on":
        isAdmin = 1
    else:
        isAdmin = 0

    if 'contrasenna' != 'contrasenna2':
        flash("Las contraseñas son diferentes")
        return redirect("/registrar")


    #revisar si existe un usuario con ese nombre
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT * 
    FROM usuario u
    WHERE u.nombreUsuario = %s
        """, ('nombreUsuario',))
    #se usa fetchall para que este en forma de tupla
    usuarios = cur.fetchall()
    if len(usuarios) == 1:
        flash("El usuario ya existe, ingrese un nombre distinto")
        return redirect("/registrar")

    
    #Encriptar contraseña
    contraseñaHasheda = bcrypt.generate_password_hash('contrasenna').decode('utf-8')
    print(contraseñaHasheda)

    #subir datos a la base de datos
    cur.execute("""
    INSERT INTO usuario(
        nombreUsuario,
        contrasennaUsuario,
        privilegiosAdministrador
    ) VALUES (%s, %s, %s)
    """, ('nombreUsuario', contraseñaHasheda, str(isAdmin)))
    mysql.connection.commit()
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
    nombreUsuarioNuevo = request.form['nombreUsuario']
    isAdmin = request.form.get('isAdmin')
    print("isAdmin")
    print(isAdmin)
    if isAdmin == "on":
        isAdmin = "1"
    else:
        isAdmin = "0"

    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE usuario
    SET nombreUsuario = %s,
        privilegiosAdministrador = %s
    WHERE nombreUsuario = %s
                """, (nombreUsuarioNuevo, isAdmin, nombreUsuario))
    mysql.connection.commit()
    flash("usuario actualizado")
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
    flash("usuario ha sido eliminado")
    return redirect("/registrar")