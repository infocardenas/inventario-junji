from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    make_response,
    send_file,
    session,
    request,
    abort,
    jsonify
)
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
import os
import shutil
from cuentas import loguear_requerido, administrador_requerido
from werkzeug.utils import secure_filename
from env_vars import paths

traslado = Blueprint("traslado", __name__, template_folder="app/templates")

PDFS_DIR = paths["pdf_path"]


@traslado.route("/traslado")
@traslado.route("/traslado/<page>")
@loguear_requerido
def Traslado(page=1):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
                    origen.nombreUnidad as nombreOrigen, 
                    destino.nombreUnidad as nombreDestino,
                    t.estaFirmadoTraslado
                FROM traslado t
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
                ORDER BY idTraslado DESC
                LIMIT %s OFFSET %s
        """,
        (perpage, offset),
    )
    traslados = cur.fetchall()

    #obtener equipos para cada traslado
    for traslado in traslados:
        cur.execute(
            """
            SELECT e.idEquipo, me.nombreModeloequipo, te.nombreTipo_equipo, 
                mae.nombreMarcaEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo
            FROM traslacion tr
            INNER JOIN equipo e ON tr.idEquipo = e.idEquipo
            INNER JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_equipo
            INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
            INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
            INNER JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
            WHERE tr.idTraslado = %s
            """,
            (traslado["idTraslado"],),
        )
        traslado["equipos"] = cur.fetchall()

    
    data = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM traslado")
    total = cur.fetchone()
    # estraer el numero del mensaje
    total = int(str(total).split(":")[1].split("}")[0])
    cur.execute(
        """
        SELECT * 
        FROM unidad u
        ORDER BY u.nombreUnidad
                 """
    )
    unidades = cur.fetchall()
    return render_template(
        'Operaciones/traslado.html',
        traslado=traslados,
        unidades=unidades,
        page=page,
        lastpage=page < (len(traslados) / perpage) + 1,
    )

@traslado.route("/traslado/equipos_unidad/<int:unidad_id>")
def obtener_equipos_unidad(unidad_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.idEquipo, me.nombreModeloequipo, e.Num_serieEquipo, e.Cod_inventarioEquipo
        FROM equipo e
        INNER JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_equipo
        WHERE e.idUnidad = %s AND e.idEstado_equipo IN (
            SELECT idEstado_equipo FROM estado_equipo 
            WHERE nombreEstado_equipo IN ('SIN ASIGNAR', 'EN USO')
        )
    """, (unidad_id,))

    equipos = cur.fetchall()
    return jsonify(equipos)


@traslado.route("/traslado/add_traslado", methods=["GET", "POST"])
@administrador_requerido
def add_traslado():
    if request.method == "POST":
        Origen = request.form["Origen"]
        if(Origen == ""):
            flash("seleccione un origen")
            return redirect(url_for("traslado.Traslado"))
        Origen = int(Origen)
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
                SELECT e.*, 
                    me.nombreModeloequipo, 
                    te.nombreTipo_equipo, 
                    mae.nombreMarcaEquipo, 
                    ee.nombreEstado_equipo,
                    u.nombreUnidad
                FROM equipo e
                INNER JOIN unidad u ON u.idUnidad = e.idUnidad
                INNER JOIN modelo_equipo me ON me.idModelo_equipo = e.idModelo_equipo
                INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
                INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
                INNER JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
                INNER JOIN estado_equipo ee ON e.idEstado_equipo = ee.idEstado_equipo
                WHERE e.idUnidad = %s
                AND (ee.nombreEstado_equipo = "SIN ASIGNAR"
                OR ee.nombreEstado_equipo = "EN USO")

                        """,
                (Origen,),
            )
            equipos_data = cur.fetchall()
            cur.execute(
                """
                SELECT * 
                FROM unidad u
                ORDER BY u.nombreUnidad
                        """
            )
            unidades = cur.fetchall()
            if len(equipos_data) == 0:
                equipos_data = []
                flash("no hay equipos en esta Unidad")
                return redirect(url_for("traslado.Traslado"))
            return render_template(
                'Operaciones/add_traslado.html', 
                equipos=equipos_data, 
                unidades=unidades
            )

        except Exception as e:
            #flash(e.args[1])
            flash("Error al crear")
            return redirect(url_for("traslado.Traslado"))


@traslado.route("/traslado/edit_traslado/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_traslado(id):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
                SELECT t.idTraslado, origen.idUnidad as idUnidadOrigen, destino.idUnidad as idUnidadDestino,
                    t.fechatraslado, t.rutadocumentoTraslado,
                    origen.nombreUnidad as nombreOrigen, destino.nombreUnidad as nombreDestino
                FROM traslado t 
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
                WHERE t.idTraslado = %s
        """,
            (id,),
        )
        data = cur.fetchall()
        cur.execute(
            """
            SELECT * 
            FROM unidad u
            ORDER BY u.nombreUnidad
            """
        )
        unidades = cur.fetchall()
        cur.execute(
            """
            SELECT e.*, 
                me.nombreModeloequipo, 
                te.nombreTipo_equipo, 
                mae.nombreMarcaEquipo
            FROM equipo e
            INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
            INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
            INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
            INNER JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
            ORDER BY e.idEquipo
                    """
        )
        equipos = cur.fetchall()
        return render_template(
            'Operaciones/editTraslado.html',
            traslado=data[0],
            agregar=True,
            unidades=unidades,
            equipo=equipos,
        )

    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for("traslado.Traslado"))


@traslado.route("/traslado/delete_multiple", methods=["POST"])
@administrador_requerido
def delete_multiple_traslados():
    data = request.get_json()
    traslados = data.get("traslados", [])

    if not traslados:
        return jsonify({"success": False, "message": "No se proporcionaron traslados para eliminar."}), 400

    try:
        cur = mysql.connection.cursor()

        for id in traslados:
            # Obtener información del traslado
            cur.execute("SELECT * FROM traslado WHERE idTraslado = %s", (id,))
            trasladoABorrar = cur.fetchone()

            if trasladoABorrar:
                # Obtener equipos en la traslación
                cur.execute("SELECT * FROM traslacion WHERE idTraslado = %s", (id,))
                traslaciones = cur.fetchall()

                # Restaurar la unidad original de cada equipo
                for traslacion in traslaciones:
                    cur.execute(
                        """
                        UPDATE equipo
                        SET idUnidad = %s
                        WHERE idEquipo = %s 
                        """,
                        (trasladoABorrar["idUnidadOrigen"], traslacion["idEquipo"]),
                    )

                # Eliminar registros en traslacion
                cur.execute("DELETE FROM traslacion WHERE idTraslado = %s", (id,))

                # Eliminar el traslado
                cur.execute("DELETE FROM traslado WHERE idTraslado = %s", (id,))

        mysql.connection.commit()
        cur.close()

        return jsonify({"success": True, "message": "Traslados eliminados correctamente."})

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "message": "Error en la eliminación de traslados."}), 500


def get_unidad_nombre(unidad_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombreUnidad FROM unidad WHERE idUnidad = %s", (unidad_id,))
    result = cur.fetchone()
    return result["nombreUnidad"] if result else "Desconocido"



@traslado.route("/traslado/create_traslado/<int:origen>", methods=["POST"])
@administrador_requerido
def create_traslado(origen):
    fechatraslado = request.form["fechatraslado"]
    destino = request.form["Destino"]
    equipos = request.form.getlist("trasladar[]")

    if not destino or not equipos:
        return jsonify({"success": False, "message": "Destino o equipos no seleccionados"}), 400

    traslado_id = crear_traslado_generico(fechatraslado, destino, origen, equipos)

    return jsonify({
        "success": True,
        "idTraslado": traslado_id,
        "fechatraslado": fechatraslado,
        "nombreOrigen": get_unidad_nombre(origen),
        "nombreDestino": get_unidad_nombre(destino)
    })



##funcion para crear un traslado
def crear_traslado_generico(fechatraslado, Destino, Origen, equipos):
    # Añadir fila a traslado
    cur = mysql.connection.cursor()
    cur.execute(
        """
                    INSERT INTO traslado (
                        fechatraslado,
                        rutadocumentoTraslado,
                        idUnidadDestino,
                        idUnidadOrigen
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
        (fechatraslado, "ruta", Destino, Origen),
    )
    mysql.connection.commit()
    # Encontrar la id de traslado
    trasladoid = cur.lastrowid
    # Añadir las traslaciones para asociar múltiples equipos al traslado
    equipos_lista = []  # Cambiamos a una lista
    for idEquipo in equipos:
        cur.execute(
            """
                        INSERT INTO traslacion (
                            idTraslado,
                            idEquipo
                        )
                        VALUES (%s, %s)
                       """,
            (str(trasladoid), idEquipo),
        )
        mysql.connection.commit()
        cur.execute(
            """
                        UPDATE equipo
                        SET idUnidad = %s
                        WHERE equipo.idEquipo = %s
                        """,
            (Destino, idEquipo),
        )
        mysql.connection.commit()

        cur.execute(
            """
                        SELECT e.*, 
                            me.nombreModeloequipo, 
                            te.nombreTipo_equipo, 
                            mae.nombreMarcaEquipo, 
                            ee.nombreEstado_equipo
                        FROM equipo e
                        INNER JOIN modelo_equipo me ON me.idModelo_equipo = e.idModelo_equipo
                        INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
                        INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
                        INNER JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
                        INNER JOIN estado_equipo ee ON ee.idEstado_equipo = e.idEstado_equipo
                        WHERE e.idEquipo = %s
                        """,
            (idEquipo,),
        )
        equipoTupla = cur.fetchone()
        equipos_lista.append(equipoTupla)  # Añadimos a la lista

    # nombre origen y destino
    cur.execute(
        """
                    SELECT *
                    FROM traslado
                    WHERE traslado.idTraslado = %s 
                    """,
        (str(trasladoid),),
    )
    traslado = cur.fetchone()
    cur.execute(
        """
                    SELECT *
                    FROM unidad
                    WHERE unidad.idUnidad = %s
                    """,
        (traslado["idUnidadOrigen"],),
    )
    UnidadOrigen = cur.fetchone()

    cur.execute(
        """
                    SELECT *
                    FROM unidad
                    WHERE unidad.idUnidad = %s
                    """,
        (traslado["idUnidadDestino"],),
    )
    UnidadDestino = cur.fetchone()

    flash("traslado agregado correctamente")
    create_pdf(traslado, equipos_lista, UnidadOrigen, UnidadDestino)

def create_pdf(traslado, equipos, UnidadOrigen, UnidadDestino):
    print("create_pdf")

    # se añade el encabezado y footer creando una clase PDF que hereda de FPDF y sobreescribe los
    # metodos
    class PDF(FPDF):
        def header(self):
            # logo
            # imageUrl = url_for('static', filename='img/logo_junji.png')
            # print(imageUrl)
            self.image("logo_junji.jpg", 10, 8, 25)
            # font
            self.set_font("times", "B", 12)
            self.set_text_color(170, 170, 170)
            # Title
            self.cell(0, 30, "", border=False, ln=1, align="L")
            self.cell(0, 5, "JUNTA NACIONAL", border=False, ln=1, align="L")
            self.cell(0, 5, "INFANTILES", border=False, ln=1, align="L")
            self.cell(0, 5, "Unidad de Inventarios", border=False, ln=1, align="L")
            # line break
            self.ln(10)
            pass

        def footer(self):
            self.set_y(-30)
            self.set_font("times", "B", 12)
            self.set_text_color(170, 170, 170)
            self.cell(0, 0, "", ln=1)
            self.cell(0, 0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
            self.cell(
                0, 12, "OHiggins Poniente 77 Concepción. Tel: 412125579", ln=1
            )  # problema con el caracter ’
            self.cell(0, 12, "www.junji.cl", ln=1)
            # self.image('logo_inferior.jpg', 30, -30, 25) Las imagenes en el Footer no parecen funcionar correctamente
            pass

    # (Orientacion, unidades, formato)
    # Orientacion P(portrait) o L(landscape)
    pdf = PDF("P", "mm", "A4")

    pdf.add_page()

    titulo = "ACTA DE TRASLADO N°" + str(traslado["idTraslado"])
    creado_por = "Documento creado por: " + session["user"]
    parrafo_1 = "En Concepción {} se procede al traslado de bienes JUNJI de registro inventario desde {} hasta {} el siguiente detalle: ".format(
        traslado["fechatraslado"],
        UnidadOrigen["nombreUnidad"],
        UnidadDestino["nombreUnidad"],
    )
    # encabezado de la tabla
    TABLE_DATA = [
    ("N°", "Articulos", "Serie", "Código Inventario", "Estado", "Modelo"),
    ]
    
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$")
    # print(equipos)
    # contadores de estado

    # ingresa los datos de la tabla como una tupla, donde la primera tupla es el encabezado
    for i, equipo in enumerate(equipos, start=1):
        TABLE_DATA.append((
            str(i),
            equipo["nombreTipo_equipo"],
            equipo["Num_serieEquipo"],
            str(equipo["Cod_inventarioEquipo"]),
            str(equipo["nombreEstado_equipo"]),
            equipo ["nombreModeloequipo"],
        ))

    # print("#$$$$$$#############")
    # print(TABLE_DATA)

    # TABLE_DATA2 = (('N°', 'Articulos', 'Serie', 'Código Inventario', 'Estado'),
    # (str(3), 'AIO', str(0), str(8013913), 'EN USO'),)
    # ("1", "EpsonI5190", "X5NS117668", "8042812", "MAL"),
    # ("2", "EpsonI5190", "X5NS117668", "8042813", "MAL"),
    # ("3", "EpsonI5190", "X5NS117668", "8042814", "MAL"),
    # ("4", "EpsonI5190", "X5NS117668", "8042815", "MAL"),
    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    pdf.cell(0, 10, creado_por, ln=True, align="L")

    pdf.multi_cell(0, 10, parrafo_1)
    # crea una tabla en base a los datos anteriores
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)
    # parrafo_2 = "Se ecuentran X en Bien, Y Regular y Z Mal"

    # pdf.multi_cell(0,10,parrafo_2, ln=True)
    pdf.ln(10)
    nombreEncargado = "Nombre Encargado:"
    rutEncargado = "Numero de RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre Ministro de Fe:"
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
    nombreEncargadoUnidadTI = "Nombre Encargado TI " + session["user"]
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
    # crea dos columnas una para el espacio de firma y otra para los nombres
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(nombreEncargado)
        cols.ln()
        cols.ln()
        cols.write(rutEncargado)
        cols.ln()
        cols.ln()
        cols.write(firmaEncargado)
        cols.ln()
        cols.ln()
        cols.ln()
        cols.ln()

        cols.write(nombreMinistro)
        cols.ln()
        cols.ln()
        cols.write(rutMinistro)
        cols.ln()
        cols.ln()
        cols.write(firma)
        cols.ln()
        cols.ln()
        cols.ln()
        cols.ln()

        cols.write(nombreEncargadoUnidadTI)
        cols.ln()
        cols.ln()
        cols.write(rutMinistro)
        cols.ln()
        cols.ln()
        cols.write(firma)
        cols.ln()
        cols.ln()
        cols.new_column()
        for i in range(0, 3):
            cols.write(text="_________________________")
            cols.ln()
            cols.ln()
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="_________________________")
            cols.ln()
            cols.ln()
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="_________________________")
            cols.ln()
            cols.ln()
    # crear pdf con la id para diferenciar pdfs

    nombrePdf = "traslado" + "_" + str(traslado["idTraslado"]) + ".pdf"
    pdf.output("traslado_{}.pdf".format(traslado["idTraslado"]))
    # print("test")
    # print(str(os.curdir))

    # mover pdf a la carpeta
    shutil.move(nombrePdf, "pdf")
    return redirect(url_for("traslado.Traslado"))


@traslado.route("/traslado/mostrar_pdf/<id>")
@traslado.route("/traslado/mostrar_pdf/<id>/<firmado>")
@loguear_requerido
def mostrar_pdf(id, firmado="0"):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esta ruta")
        return redirect("/ingresar")

    nombrePdf = f"traslado_{id}.pdf" if firmado == "0" else f"traslado_{id}_firmado.pdf"
    dir_pdf = os.path.join("pdf", nombrePdf)

    if not os.path.exists(dir_pdf):
        flash(f"El archivo PDF {nombrePdf} no se encuentra disponible.")
        return redirect("/traslado")  # Redirige a la página principal en vez de caer en error

    return send_file(dir_pdf, as_attachment=True)

@traslado.route("/traslado/buscar/<idTraslado>")
@loguear_requerido
def buscar(idTraslado):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
                    origen.nombreUnidad as nombreOrigen, 
                    destino.nombreUnidad as nombreDestino,
                    t.estaFirmadoTraslado
                FROM traslado t
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
                WHERE t.idTraslado = %s
                ORDER BY idTraslado DESC
        """,
        (idTraslado,),
    )
    data = cur.fetchall()

    cur.execute(
        """
        SELECT * 
        FROM unidad u
        ORDER BY u.nombreUnidad
                 """
    )
    unidades = cur.fetchall()

    return render_template(
        'Operaciones/traslado.html', 
        traslado=data, 
        unidades=unidades, 
        page=1, 
        lastpage=True
    )


@traslado.route("/traslado/listar_pdf/<idTraslado>")
@loguear_requerido
def listar_pdf(idTraslado):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    dir = "pdf"
    nombreFirmado = "traslado_" + str(idTraslado) + "_" + "firmado.pdf"
    # revisa si el archivo esta firmado
    if not os.path.exists(os.path.join(dir, nombreFirmado)):
        # mostrar
        print("#####NombreFirmado = None #######")
        nombreFirmado = "None"
    print("exists")
    return render_template(
        "GestionR.H/firma.html", 
        nombreFirmado=nombreFirmado, 
        id=idTraslado, 
        location="traslado"
    )


@traslado.route("/traslado/adjuntar_pdf/<idTraslado>", methods=["POST"])
@administrador_requerido
def adjuntar_firmado(idTraslado):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    # TODO: revisar que sea pdf
    file = request.files["file"]
    # subir archivo
    dir = "pdf"
    # renombrar archivo
    filename = file.filename
    sfilename = secure_filename(filename)
    file.save(os.path.join(dir, secure_filename(sfilename)))
    os.rename(
        os.path.join(dir, sfilename),
        os.path.join(dir, "traslado_" + str(idTraslado) + "_firmado.pdf"),
    )
    return redirect("/traslado/listar_pdf/" + str(idTraslado))