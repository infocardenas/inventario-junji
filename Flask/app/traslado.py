from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    send_file,
    session,
    request,
    jsonify
)
from . import mysql
from fpdf import FPDF
from .funciones import getPerPage
import os
import shutil
from .cuentas import loguear_requerido, administrador_requerido
from werkzeug.utils import secure_filename
from env_vars import paths

traslado = Blueprint("traslado", __name__, template_folder="app/templates")

PDFS_DIR = paths["pdf_path"]

@traslado.route("/traslado")
@traslado.route("/traslado/<int:page>")
@loguear_requerido
def Traslado(page=1):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")

    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
               origen.nombreUnidad as nombreOrigen, 
               destino.nombreUnidad as nombreDestino,
               t.estaFirmadoTraslado
        FROM traslado t
        INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
        INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
        ORDER BY idTraslado DESC
        LIMIT %s OFFSET %s
    """, (perpage, offset))
    
    traslados = cur.fetchall()

    # Obtener equipos para cada traslado
    for traslado in traslados:
        cur.execute("""
            SELECT e.idEquipo, me.nombreModeloequipo, te.nombreTipo_equipo, 
                   mae.nombreMarcaEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo
            FROM traslacion tr
            INNER JOIN equipo e ON tr.idEquipo = e.idEquipo
            INNER JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_equipo
            INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
            INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
            INNER JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
            WHERE tr.idTraslado = %s
        """, (traslado["idTraslado"],))
        traslado["equipos"] = cur.fetchall()

    # Obtener el total de traslados
    cur.execute("SELECT COUNT(*) AS total FROM traslado")
    total = cur.fetchone()['total']
    
    # Calcular la última página
    lastpage = (total + perpage - 1) // perpage

    cur.execute("SELECT * FROM unidad ORDER BY nombreUnidad")
    unidades = cur.fetchall()

    return render_template(
        'Operaciones/traslado.html',
        traslado=traslados,
        unidades=unidades,
        page=page,
        lastpage=lastpage
    )
def getPerPage():
    return 10  # Cambia este número si quieres más o menos resultados por página

@traslado.route("/traslado/equipos_unidad/<int:unidad_id>")
def obtener_equipos_unidad(unidad_id):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT e.idEquipo, me.nombreModeloequipo, e.Num_serieEquipo, e.Cod_inventarioEquipo,
           te.nombreTipo_equipo, mae.nombreMarcaEquipo
    FROM equipo e
    INNER JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_equipo
    INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
    INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
    INNER JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
    WHERE e.idUnidad = %s 
    AND e.idEstado_equipo IN (
        SELECT idEstado_equipo FROM estado_equipo 
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
            flash("Error al crear")
            return redirect(url_for("traslado.Traslado"))


@traslado.route("/traslado/edit_traslado/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_traslado(id):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    
    if request.method == "POST":
        # Obtener la nueva fecha del formulario
        nueva_fecha = request.form.get("fechaTraslado")
        if not nueva_fecha:
            flash("La fecha de traslado es requerida")
            return redirect(url_for("traslado.Traslado"))
        
        try:
            # Actualizar la fecha del traslado en la base de datos
            cur = mysql.connection.cursor()
            cur.execute(
                """
                UPDATE traslado
                SET fechatraslado = %s
                WHERE idTraslado = %s
                """,
                (nueva_fecha, id),
            )
            mysql.connection.commit()
            flash("Fecha de traslado actualizada correctamente")
        except Exception as e:
            print("Error al actualizar la fecha del traslado:", e)
            flash("Ocurrió un error al actualizar la fecha del traslado")
        finally:
            cur.close()
        
        return redirect(url_for("traslado.Traslado"))
    
    # Si el método es GET, cargar los datos del traslado para renderizar el modal
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            SELECT t.idTraslado, t.fechatraslado
            FROM traslado t
            WHERE t.idTraslado = %s
            """,
            (id,),
        )
        traslado = cur.fetchone()
        return render_template(
            'Operaciones/editTraslado.html',
            traslado=traslado,
        )
    except Exception as e:
        print("Error al cargar los datos del traslado:", e)
        flash("Ocurrió un error al cargar los datos del traslado")
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

    if destino == str(origen):  # Convertimos origen a str para evitar errores de comparación
        return jsonify({"success": False, "message": "El destino no puede ser igual al origen"}), 400

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

    class PDF(FPDF):
        def header(self):

            self.image("static/img/logo_junji.png", 10, 8, 32)
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
            pass

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

                

    pdf.ln(10)
    nombreEncargado = "Nombre del encargado TI:"
    rutEncargado = "RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre del funcionario:"
    rutMinistro = "RUT:"
    firma = "Firma"
    with pdf.text_columns(text_align="J", ncols=2, gutter=30) as cols:
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
        cols.ln() # <-- Aquí se muestra la observación real
        cols.new_column()
        for i in range(0, 3):
            if i == 0:
                cols.write(text= session['user'])
            else:
                cols.write(text="___________________________________")
            cols.ln()
            cols.ln()
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="___________________________________")
            cols.ln()
            cols.ln()
    # crear pdf con la id para diferenciar pdfs

    nombrePdf = "traslado" + "_" + str(traslado["idTraslado"]) + ".pdf"
    pdf.output("traslado_{}.pdf".format(traslado["idTraslado"]))
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

    return send_file(dir_pdf, as_attachment=False)

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
@traslado.route("/traslado/listar_pdf/<idTraslado>/<devolver>")
@loguear_requerido
def listar_pdf(idTraslado, devolver="None"):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")

    dir = "pdf"   

    if devolver == "None":
        nombreFirmado = "traslado_" + str(idTraslado) + "_" + "firmado.pdf"
        location = "traslado"
    else:
        nombreFirmado = "devolucion_" + str(idTraslado) + "_" + "firmado.pdf"
        location = "devolucion"

    # Revisa si el archivo está firmado
    if not os.path.exists(os.path.join(dir, "firmas_traslados", nombreFirmado)) and not os.path.exists(os.path.join(dir, "firmas_devoluciones", nombreFirmado)):
        # Si no existe el archivo firmado
        nombreFirmado = "No existen firmas para este documento"
    
    return render_template(
        'GestionR.H/firma.html',
        nombreFirmado=nombreFirmado,
        id=idTraslado,
        location=location
    )



@traslado.route("/traslado/mostrar_pdf/<id>/")
@loguear_requerido
def mostrar_pdf_traslado_firmado(id):
    if "user" not in session:
        flash("Se necesita ingresar para acceder a esta ruta")
        return redirect("/ingresar")
    
    try:
        # Definir el nombre del archivo PDF basado en el ID
        nombrePDF = "traslado_" + str(id) + "_firmado.pdf"
        file_path = os.path.join("pdf/firmas_traslados", nombrePDF)

        # Verificar si el archivo existe antes de enviarlo
        if not os.path.exists(file_path):
            flash("No se encontró el archivo PDF solicitado.")
            return redirect(url_for('traslado.listar_pdf', idTraslado=id))  # Redirige a la página de traslados

        # Si el archivo existe, enviarlo para su visualización
        return send_file(file_path, as_attachment=False)

    except FileNotFoundError:
        flash("El archivo PDF no se encuentra en el servidor.")
        return redirect(url_for('traslado.listar_pdf', idTraslado=id))  # Redirige en caso de error con el archivo

    except Exception as e:
        # Captura cualquier otra excepción y muestra un mensaje genérico
        flash(f"Error al intentar mostrar el archivo: {str(e)}")
        return redirect(url_for('traslado.listar_pdf', idTraslado=id))  # Redirige en caso de cualquier otro error

    

# Ruta para subir un archivo PDF relacionado con el traslado
@traslado.route("/traslado/adjuntar_pdf/<idTraslado>", methods=["POST"])
@administrador_requerido
def adjuntar_pdf_traslado(idTraslado):
    if "user" not in session:
        flash("You are NOT authorized")
        return redirect("/ingresar")
    # Definir la carpeta donde se guardará el archivo
    dir = "pdf/firmas_traslados"

    # Crear la carpeta si no existe
    os.makedirs(dir, exist_ok=True)

    # Nombre del archivo que debe eliminarse si ya existe
    filenameToDelete = f"traslado_{idTraslado}_firmado.pdf"
    file_path = os.path.join(dir, filenameToDelete)

    # Verificar si el archivo ya existe y eliminarlo
    if os.path.exists(file_path):
        os.remove(file_path)

    # Obtener el archivo desde la solicitud
    file = request.files["file"]

    # Guardar el archivo con un nombre seguro
    sfilename = secure_filename(file.filename)
    temp_file_path = os.path.join(dir, sfilename)
    file.save(temp_file_path)

    # Renombrar el archivo al formato correcto
    new_file_path = os.path.join(dir, f"traslado_{idTraslado}_firmado.pdf")
    
    # Eliminar el archivo si ya existe antes de renombrar
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    os.rename(temp_file_path, new_file_path)


    # Redirigir a la lista de PDFs del traslado
    return redirect(f"/traslado/listar_pdf/{idTraslado}")


