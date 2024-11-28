#se importa flask
from flask import Blueprint, render_template, request, url_for, redirect,flash
#se importa db.py para utilizar la conexion a mysql
from db import mysql
#importamos el modulo que creamos
from funciones import validarChar

comuna = Blueprint('comuna', __name__, template_folder='app/templates')

#vista principal comuna y envia datos correspondientes
@comuna.route('/comuna')
def Comuna():
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT pro.idProvincia, pro.nombreProvincia, co.idComuna, co.nombreComuna, co.idProvincia
    FROM comuna co
    INNER JOIN provincia pro on pro.idProvincia = co.idProvincia
    """)
    data = cur.fetchall()    
    cur.execute('SELECT * FROM provincia')
    p_data = cur.fetchall()
    cur.close()
    return render_template('comuna.html', comuna = data, provincia = p_data)

#agrega registro para comuna
@comuna.route('/add_comuna', methods = ['POST'])
def add_comuna():
    if request.method == 'POST':
        nombre_comuna = request.form['nombre_comuna']
        nombre_provincia = request.form['nombre_provincia']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO comuna (nombreComuna, idProvincia) VALUES (%s, %s)', (nombre_comuna, nombre_provincia))
            mysql.connection.commit()
            flash('Comuna ingresada correctamente')
            return redirect(url_for('comuna.Comuna'))
        except Exception as e:
            flash("Error al crear")
            #flash(e.args[1])
            return redirect(url_for('comuna.Comuna'))
        
#enviar datos a vista editar
@comuna.route('/edit_comuna/<id>')
def edit_comuna(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
        SELECT pro.idProvincia, pro.nombreProvincia, co.idComuna, co.nombreComuna, co.idProvincia
        FROM comuna co
        INNER JOIN provincia pro on pro.idProvincia = co.idProvincia
        WHERE idComuna = %s
        """, (id,))
        data = cur.fetchall()        
        cur.execute('SELECT * FROM provincia')
        p_data = cur.fetchall()
        cur.close()
        return render_template('editComuna.html', comuna = data[0], provincia = p_data)
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for('comuna.Comuna'))
    
#actualiza registro segun el id
@comuna.route('/update_comuna/<id>', methods = ['POST'])
def update_comuna(id):
    if request.method == 'POST':
        nombre_comuna = request.form['nombre_comuna']
        nombre_provincia = request.form['nombre_provincia']
        try:
            cur = mysql.connection.cursor()
            cur.execute(""" 
            UPDATE comuna 
            SET nombreComuna = %s,
                idProvincia = %s
                WHERE idComuna = %s
            """, (nombre_comuna, nombre_provincia, id))
            mysql.connection.commit()
            flash('Comuna actualizada correctamente')
            return redirect(url_for('comuna.Comuna'))
        except Exception as e:
            flash("Error al crear")
            #flash(e.args[1])
            return redirect(url_for('comuna.Comuna'))
        
#elimina registro segun el id
@comuna.route('/delete_comuna/<id>')
def delete_comuna(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM comuna WHERE idComuna = %s', (id,))
        mysql.connection.commit()
        flash('Comuna eliminada correctamente')
        return redirect(url_for('comuna.Comuna'))
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for('comuna.Comuna'))