from flask import Blueprint, request, render_template, flash, url_for, redirect, session
from db import mysql
from funciones import validarRut, getPerPage, validarCorreo
from cuentas import loguear_requerido, administrador_requerido
funcionario = Blueprint('funcionario', __name__, template_folder='app/templates')

#envias los datos a la vista pricipal de funcionario
@funcionario.route('/funcionario')
@funcionario.route('/funcionario/<page>')
@loguear_requerido
def Funcionario(page = 1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset = (page -1) * perpage 
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario, 
            f.idUnidad, u.idUnidad, u.nombreUnidad, f.correoFuncionario
    FROM funcionario f
    INNER JOIN unidad u on f.idUnidad = u.idUnidad
    LIMIT %s OFFSET %s 
    """, (perpage, offset))
    data = cur.fetchall()
    cur.execute('SELECT * FROM unidad')
    ubi_data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM funcionario')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    return render_template('funcionario.html', funcionario = data, 
                           Unidad = ubi_data, page=page, lastpage= page < (total/perpage)+1)


#agregar funcionario
@funcionario.route('/add_funcionario', methods = ['POST'])
@administrador_requerido
def add_funcionario():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
        rut_funcionario = request.form['rut_funcionario']
        nombre_funcionario = request.form['nombre_funcionario']
        cargo_funcionario = request.form['cargo_funcionario']
        codigo_Unidad = request.form['codigo_Unidad']
        correo_funcionario = request.form['correo_funcionario']


        if(not validarRut(rut_funcionario)):
            flash(f'Rut no es valido')
            return redirect(url_for('funcionario.Funcionario'))
        #if(not validarCorreo(correo_funcionario)):
            #flash('El correo no es valido')
            #return redirect(url_for('funcionario.Funcionario'))
        
    
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                        INSERT INTO funcionario 
                        (rutFuncionario, nombreFuncionario, 
                        cargoFuncionario, idUnidad, correoFuncionario) 
                        VALUES (%s, %s, %s, %s, %s)
                        """, 
            (rut_funcionario, nombre_funcionario,cargo_funcionario, 
                codigo_Unidad, correo_funcionario))
            mysql.connection.commit()
            flash('Funcionario agregado correctamente')
            return redirect(url_for('funcionario.Funcionario'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('funcionario.Funcionario'))
    
#enviar datos a vista editar
@funcionario.route('/edit_funcionario/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_funcionario(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
        SELECT *
        FROM funcionario f
        INNER JOIN unidad u on f.idUnidad = u.idUnidad
        WHERE rutFuncionario = %s
        """, (id,))
        data = cur.fetchall()
        cur.execute('SELECT * from unidad')
        print(data) 
        ubi_data = cur.fetchall()
        return render_template('editFuncionario.html', funcionario = data[0], Unidad = ubi_data)
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('funcionario.Funcionario'))

#actualizar funcionario por id
@funcionario.route('/update_funcionario/<id>', methods = ['POST'])
@administrador_requerido
def update_funcionario(id):
    if request.method == 'POST':
        rut_funcionario = request.form['rut_funcionario']
        nombre_funcionario = request.form['nombre_funcionario']
        correo_funcionario = request.form['correo_funcionario']
        cargo_funcionario = request.form['cargo_funcionario']
        codigo_Unidad = request.form['codigo_Unidad']

        cur = mysql.connection.cursor()

        try:
            cur.execute("""
            UPDATE funcionario
            SET rutFuncionario = %s,
                nombreFuncionario = %s,
                cargoFuncionario = %s,
                idUnidad = %s,
                correoFuncionario = %s
            WHERE rutFuncionario = %s
            """, (rut_funcionario, nombre_funcionario, cargo_funcionario, 
                codigo_Unidad, correo_funcionario, id))
            mysql.connection.commit()
            flash('Funcionario actualizado correctamente')
        
            return redirect(url_for('funcionario.Funcionario'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('funcionario.Funcionario'))

#eliminar registro segun id
@funcionario.route('/delete_funcionario/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_funcionario(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM funcionario WHERE rutFuncionario = %s', (id,))
        mysql.connection.commit()
        flash('Funcionario eliminado correctamente')
        return redirect(url_for('funcionario.Funcionario'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('funcionario.Funcionario'))

@funcionario.route("/funcionario/buscar_funcionario/<id>")
@loguear_requerido
def buscar_funcionario(id):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT * 
    FROM funcionario f
    INNER JOIN unidad u on f.idUnidad = u.idUnidad
    WHERE f.rutFuncionario = %s
    """, (id,))
    funcionarios = cur.fetchall()

    cur.execute("""
    SELECT *
    FROM unidad u 
                """)
    unidades = cur.fetchall()
    return render_template('funcionario.html', funcionario = funcionarios, 
                           Unidad = unidades, page=1, lastpage=True)