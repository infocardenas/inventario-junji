from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from db import mysql
from cuentas import loguear_requerido, administrador_requerido

devolucion = Blueprint('devolucion', __name__, template_folder='app/templates')


@devolucion.route('/add_devolucion', methods = ['POST'])
@loguear_requerido
def add_estado_equipo():
    if request.method == 'POST':
        fechaDevolucion = request.form['fechaDevolucion']
        observacionDevolucion= request.form['observacionDevolucion']
        rutaactaDevolucion= request.form['rutaactaDevolucion']
        ActivoDevolucion= request.form['ActivoDevolucion']
        rutFuncionario= request.form['rutFuncionario']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO devolucion (fechaDevolucion,observacionDevolucion,rutaactaDevolucion,ActivoDevolucion,rutFuncionario) VALUES (%s, %s,%s,%s,%s)', 
                        ( fechaDevolucion,observacionDevolucion,rutaactaDevolucion,ActivoDevolucion,rutFuncionario))
            mysql.connection.commit()
            flash('Estado de equipo agregado correctamente')
            return redirect(url_for('devolucion.Devolucion'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('devolucion.Devolucion'))
    
#enviar datos a vista editar
@devolucion.route('/edit_devolucion/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_devolucion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
    SELECT d.idDevolucion, d.fechaDevolucion, d.observacionDevolucion, d.rutaactaDevolucion, d.ActivoDevolucion, d.rutFuncionario, f.rutFuncionario
    FROM devolucion d
    INNER JOIN funcionario f on d.rutFuncionario = f.rutFuncionario
    WHERE idDevolucion = %s""", (id,))
        data = cur.fetchall()
        cur.execute('SELECT rutFuncionario FROM funcionario')
        f_data = cur.fetchall()
        return render_template('editdevolucion.html', devolucion = data[0], funcionario= f_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('devolucion.Devolucion'))

#actualizar
@devolucion.route('/update_devolucion/<id>', methods = ['POST'])
@administrador_requerido
def update_devolucion(id):
    if request.method == 'POST':
        fechaDevolucion = request.form['fechaDevolucion']
        observacionDevolucion= request.form['observacionDevolucion']
        rutaactaDevolucion= request.form['rutaactaDevolucion']
        try:
            ActivoDevolucion= request.form['ActivoDevolucion']
        except:
            ActivoDevolucion = 0
        finally:
            rutFuncionario= request.form['rutFuncionario']
            try:
                cur = mysql.connection.cursor()
                cur.execute("""
                UPDATE devolucion
                SET fechaDevolucion = %s,
                    observacionDevolucion = %s,
                    rutaactaDevolucion = %s,
                    ActivoDevolucion = %s,
                    rutFuncionario = %s
                WHERE iddevolucion = %s
                """, (fechaDevolucion, observacionDevolucion,rutaactaDevolucion,ActivoDevolucion,rutFuncionario,id))
                mysql.connection.commit()
                flash('devolucion actualizado correctamente')
                return redirect(url_for('devolucion.Devolucion'))
            except Exception as e:
                flash(e.args[1])
                return redirect(url_for('devolucion.Devolucion'))

#eliminar    
@devolucion.route('/delete_devolucion/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_devolucion(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM devolucion WHERE iddevolucion = %s', (id,))
        mysql.connection.commit()
        flash('devolucion eliminado correctamente')
        return redirect(url_for('devolucion.Devolucion'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('devolucion.Devolucion'))

@devolucion.route("/test1")
@administrador_requerido
def crear_pdf():
    return redirect(url_for("asignacion.Asignacion"))