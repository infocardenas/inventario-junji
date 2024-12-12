from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator

estado_equipo = Blueprint('estado_equipo', __name__, template_folder='app/templates')

@estado_equipo.route('/estado_equipo')
@estado_equipo.route('/estado_equipo/<page>')
@loguear_requerido
def estadoEquipo(page = 1):
    page = int(page)
    perpage = getPerPage()
    offset = (page-1) * perpage
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM estado_equipo LIMIT %s OFFSET %s",(perpage, offset))
    data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM estado_equipo')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    cur.close()
    return render_template('estado_equipo.html', estado_equipo = data,
                           page=page, lastpage= page < (total/perpage)+1)

@estado_equipo.route('/add_estado_equipo', methods = ['POST'])
@administrador_requerido
def add_estado_equipo():
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
        data ={
            'nombre_estado_equipo': request.form['nombre_estado_equipo'],
            }
        schema = {
            'nombre_estado_equipo': {'required': True, 'type': 'string', 'regex': '^[a-zA-Z0-9]+$'},
        }
        fecha_modificacion = request.form['fecha_modificacion']
        v = Validator(schema)
        if not v.validate(data):
            flash("caracteres no premitidos")
            return redirect(url_for('estado_equipo.estadoEquipo'))
    
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO estado_equipo (nombreEstado_equipo, FechaEstado_equipo) VALUES (%s, %s)', (data ['nombre_estado_equipo'], fecha_modificacion))
            mysql.connection.commit()
            flash('Estado de equipo agregado correctamente')
            return redirect(url_for('estado_equipo.estadoEquipo'))
        except Exception as e:
            flash("Error al crear")
            #flash(e.args[1])
            return redirect(url_for('estado_equipo.estadoEquipo'))
    
#enviar datos a vista editar
@estado_equipo.route('/edit_estado_equipo/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def edit_estado_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM estado_equipo WHERE idEstado_equipo = %s', (id,))
        data = cur.fetchall()
        return render_template('editEstado_equipo.html', estado_equipo = data[0])
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('estado_equipo.estadoEquipo'))

#actualizar
@estado_equipo.route('/update_estado_equipo/<id>', methods = ['POST'])
@administrador_requerido
def update_estado_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == 'POST':
        data ={
            'nombre_estado_equipo': request.form['nombre_estado_equipo'],
        }
        fecha_modificacion = request.form['fecha_modificacion']

        schema = {
            'nombre_estado_equipo': {'required': True, 'type': 'string', 'regex': '^[a-zA-Z0-9]+$'},
        }

        v = Validator(schema)
        if not v.validate(data):
            flash("caracteres no permitidos")
            return redirect(url_for('estado_equipo.estadoEquipo'))

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE estado_equipo
            SET nombreEstado_equipo = %s,
                FechaEstado_equipo = %s
            WHERE idEstado_equipo = %s
            """, (data['nombre_estado_equipo'], fecha_modificacion, id))
            mysql.connection.commit()
            flash('Estado de equipo actualizado correctamente')
            return redirect(url_for('estado_equipo.estadoEquipo'))
        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for('estado_equipo.estadoEquipo'))

#eliminar    
@estado_equipo.route('/delete_estado_equipo/<id>', methods = ['POST', 'GET'])
@administrador_requerido
def delete_estado_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM estado_equipo WHERE idEstado_equipo = %s', (id,))
        mysql.connection.commit()
        flash('Estado de equipo eliminado correctamente')
        return redirect(url_for('estado_equipo.estadoEquipo'))
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for('estado_equipo.estadoEquipo'))

@estado_equipo.route("/mostrar_equipos_segun_tipo/<tipo>")
@administrador_requerido
def mostrar_equipos_segun_tipo(tipo):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute("""

            SELECT *
                FROM
                (
                SELECT e.idEquipo, e.Cod_inventarioEquipo, 
                    e.Num_serieEquipo, e.ObservacionEquipo,
                    e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, 
                    e.numerotelefonicoEquipo,
                    te.idTipo_equipo, 
                    te.nombreTipo_Equipo, ee.idEstado_equipo, ee.nombreEstado_equipo, 
                    u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
                moe.idModelo_equipo, moe.nombreModeloequipo, "" as nombreFuncionario
                FROM equipo e
                INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
                INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
                INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
                INNER JOIN unidad u on u.idUnidad = e.idUnidad
                INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra

                WHERE ee.nombreEstado_equipo NOT LIKE "EN USO"
                UNION 
                SELECT  e.idEquipo, e.Cod_inventarioEquipo, 
                        e.Num_serieEquipo, e.ObservacionEquipo, 
                        e.codigoproveedor_equipo, e.macEquipo, 
                        e.imeiEquipo, e.numerotelefonicoEquipo,
                        te.idTipo_equipo, te.nombreTipo_Equipo,
                        ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad,
                        u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
                        moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario
                FROM equipo e
                INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
                INNER JOIN tipo_equipo te on te.idTipo_equipo = moe.idTipo_Equipo
                INNER JOIN unidad u on u.idUnidad = e.idUnidad
                INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra

                INNER JOIN equipo_asignacion ea on ea.idEquipo = e.idEquipo
                INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
                INNER JOIN asignacion a on a.idAsignacion = ea.idAsignacion
                INNER JOIN funcionario f on f.rutFuncionario = a.rutFuncionario
                WHERE ee.nombreEstado_equipo LIKE "EN USO"
                AND a.ActivoAsignacion = 1
                ) as subquery
                WHERE nombreEstado_equipo = %s

    """, (tipo,))
    Equipos = cur.fetchall()
    cur.execute("SELECT * FROM tipo_equipo")
    tipoe_data = cur.fetchall()
    cur.execute("SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo")
    estadoe_data = cur.fetchall()
    cur.execute("SELECT idUnidad, nombreUnidad FROM unidad")
    ubi_data = cur.fetchall()
    cur.execute("SELECT idOrden_compra, nombreOrden_compra FROM orden_compra")
    ordenc_data = cur.fetchall()
    cur.execute("SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo")
    modeloe_data = cur.fetchall()

    return render_template(
        "equipo.html",
        equipo=Equipos,
        tipo_equipo=tipoe_data,
        estado_equipo=estadoe_data,
        orden_compra=ordenc_data,
        Unidad=ubi_data,
        modelo_equipo=modeloe_data,
        page=1,
        lastpage=True,
    )