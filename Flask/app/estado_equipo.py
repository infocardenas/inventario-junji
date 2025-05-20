from flask import Blueprint, render_template, request, url_for, redirect, flash, session, jsonify
from . import mysql
from .funciones import getPerPage
from .cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator

estado_equipo = Blueprint('estado_equipo', __name__, template_folder='app/templates')


@estado_equipo.route('/estado_equipo')
@estado_equipo.route('/estado_equipo/<page>')
@loguear_requerido
def estadoEquipo(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()

    # Obtener estados de equipos con conteo
    cur.execute("""
        SELECT ee.idEstado_equipo, ee.nombreEstado_equipo, COUNT(e.idEquipo) AS conteo
        FROM estado_equipo ee
        LEFT JOIN equipo e ON ee.idEstado_equipo = e.idEstado_equipo
        GROUP BY ee.idEstado_equipo, ee.nombreEstado_equipo
        ORDER BY conteo DESC
        LIMIT %s OFFSET %s
    """, (perpage, offset))
    
    data = cur.fetchall()

    # Obtener todas las unidades disponibles
    cur.execute('SELECT idUnidad, nombreUnidad FROM unidad')
    unidades = cur.fetchall()

    cur.execute('SELECT COUNT(*) AS total FROM estado_equipo')
    total_result = cur.fetchone()
    total = total_result["total"] if total_result and "total" in total_result else 0

    cur.close()

    return render_template(
        'Equipo/estado_equipo.html',
        estado_equipo=data,
        unidades=unidades,  # 🔹 Pasamos las unidades al template
        page=page,
        lastpage=page < (total / perpage) + 1
    )


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
        return jsonify({"error": "No autorizado"}), 403

    cur = mysql.connection.cursor()

    query = """
        SELECT e.idEquipo, moe.nombreModeloequipo, te.nombreTipo_equipo, 
               e.Num_serieEquipo, u.nombreUnidad
        FROM equipo e
        INNER JOIN modelo_equipo moe ON moe.idModelo_Equipo = e.idModelo_equipo
        INNER JOIN marca_tipo_equipo mte ON mte.idMarcaTipo = moe.idMarca_Tipo_Equipo
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        INNER JOIN estado_equipo ee ON ee.idEstado_equipo = e.idEstado_Equipo
        INNER JOIN unidad u ON u.idUnidad = e.idUnidad
        WHERE ee.nombreEstado_equipo = %s
    """

    cur.execute(query, (tipo,))
    equipos = cur.fetchall()
    cur.close()

    # 🔹 Convertir resultados en formato JSON para la respuesta
    equipos_json = [
        {
            "idEquipo": equipo["idEquipo"],
            "nombreModeloequipo": equipo["nombreModeloequipo"],
            "nombreTipo_equipo": equipo["nombreTipo_equipo"],
            "Num_serieEquipo": equipo["Num_serieEquipo"],
            "nombreUnidad": equipo["nombreUnidad"]
        }
        for equipo in equipos
    ]

    return jsonify(equipos_json)
