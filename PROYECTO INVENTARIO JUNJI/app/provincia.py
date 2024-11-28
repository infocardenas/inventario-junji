#se importa flask
from flask import Blueprint, render_template, request, url_for, redirect,flash, session
#se importa db.py para utilizar la conexion a mysql
from db import mysql
#importamos el modulo que creamos
from funciones import validarChar

provincias = Blueprint('provincias', __name__, template_folder='app/templates')

#envia los datos a la vista principalde provincia
@provincias.route('/provincia')
def Provincia():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from provincia')
    data = cur.fetchall()
    return render_template('provincia.html', provincia = data)

#agrega un registro para provincia
@provincias.route('/add_provincia', methods = ['POST'])
def add_provincia():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
        nombre_provincia = request.form['nombre_provincia']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO provincia (nombreProvincia) VALUES (%s)', (nombre_provincia,))
            mysql.connection.commit()
            flash('Provincia agregada correctamente')
            return redirect(url_for('provincias.Provincia'))  
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('provincias.Provincia'))
        
#enviar datos a vista editar segun el id
@provincias.route('/edit_provincia/<id>', methods = ['POST', 'GET'])
def edit_provincia(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM provincia WHERE idProvincia = %s', (id,))
        data = cur.fetchall()
        return render_template('editProvincia.html', provincia = data[0])
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('provincias.Provincia'))

#actualiza el registro segun id 
@provincias.route('/update_provincia/<id>', methods = ['POST'])
def update_provincia(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
        nombre_provincia = request.form['nombre_provincia']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE provincia
            SET nombreProvincia = %s
            WHERE idProvincia = %s
            """, (nombre_provincia, id))
            mysql.connection.commit()
            flash('Provincia actualizada correctamente')
            return redirect(url_for('provincias.Provincia'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('provincias.Provincia'))

#elimina un elemento segun el id correspondiente
@provincias.route('/delete_provincia/<id>', methods = ['POST', 'GET'])
def delete_provincia(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM provincia WHERE idProvincia = %s', (id,))
        mysql.connection.commit()
        flash('Provincia eliminada correctamente')
        return redirect(url_for('provincias.Provincia'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('provincias.Provincia'))