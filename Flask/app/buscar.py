from flask import Blueprint, render_template, request
from db import mysql
from cuentas import loguear_requerido
buscar = Blueprint("buscar", __name__, template_folder="app/templates")

@buscar.route("/buscar", methods=["GET", "POST"])
@loguear_requerido
def Buscar():
    busqueda_data = request.args.get('busqueda') 

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT e.Cod_inventarioEquipo as clave, 
                e.Num_serieEquipo as nombre, 
                e.codigoproveedor_equipo as codigo,
                e.idEquipo as id, 
                "equipo" as tipo
    FROM equipo e
    UNION
    SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario,
                f.rutFuncionario, "funcionario"
    FROM funcionario f
    UNION
    SELECT u.direccionUnidad, u.nombreUnidad, mo.nombreModalidad,
                 u.idUnidad, "unidad"
    FROM unidad u
        INNER JOIN modalidad mo ON mo.idModalidad = u.idModalidad
        UNION
        SELECT a.fecha_inicioAsignacion as clave, 
                a.ActivoAsignacion as nombre,
                a.observacionAsignacion as codigo,
                a.idAsignacion as id,
                "asignacion" as tipo
        FROM asignacion a
        UNION
        SELECT i.fechaIncidencia,
                i.nombreIncidencia,
                i.observacionIncidencia,
                i.idIncidencia,
                "incidencia"
        FROM incidencia i
        UNION
        SELECT t.fechaTraslado,
                origen.nombreUnidad,
                destino.nombreUnidad,
                t.idTraslado,
                "traslado"
        FROM traslado t 
        INNER JOIN unidad origen ON origen.idUnidad = t.idUnidadOrigen
        INNER JOIN unidad destino ON destino.idUnidad = t.idUnidadDestino
        """)
    items_data = cur.fetchall()

    return render_template("buscar.html", busqueda=busqueda_data, 
                items=items_data)