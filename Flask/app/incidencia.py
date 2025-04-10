from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file, session
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
import os, time
from cerberus import Validator
from MySQLdb import IntegrityError 
import shutil 
from werkzeug.utils import secure_filename
from env_vars import paths, inLinux
incidencia = Blueprint("incidencia", __name__, template_folder="app/templates")
PDFS_INCIDENCIAS = paths['pdf_path']

#pestaña principal de incidencias
@incidencia.route("/incidencia")
@incidencia.route("/incidencia/<page>")
@loguear_requerido
def Incidencia(page = 1):
    page = int(page)
    perpage = getPerPage()
    offset = (page -1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(
    """
        SELECT i.idIncidencia, i.nombreIncidencia, i.observacionIncidencia,
            i.rutaactaIncidencia, i.fechaIncidencia, i.idEquipo,
            e.cod_inventarioEquipo, e.Num_serieEquipo, 
            te.nombreTipo_equipo, me.nombreModeloequipo,
            i.numDocumentos, i.estadoIncidencia
        FROM incidencia i
        INNER JOIN equipo e ON i.idEquipo = e.idEquipo
        INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
        INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        LIMIT %s OFFSET %s
        """, (perpage, offset)
    )
    data = cur.fetchall()
    print("Informaicion de incidencias")
    print(data)
    cur.execute('SELECT COUNT(*) AS total FROM incidencia')
    total = cur.fetchone()['total']

    return render_template(
        'Operaciones/incidencia.html', 
        incidencia=data,
        page=page, 
        lastpage= page < (total/perpage)+1
        )

#form que se accede desde equipo para crear incidencia
@incidencia.route("/incidencia/form/<idEquipo>")
@administrador_requerido
def incidencia_form(idEquipo):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT *
                FROM super_equipo e
                WHERE e.idEquipo = %s
                """, (idEquipo,))
    equipo = cur.fetchone()
    print("equipo")
    print(equipo)
    return render_template(
        'Operaciones/add_incidencia.html', 
        equipo=equipo
        )

# Ruta para agregar una incidencia
@incidencia.route("/incidencia/add_incidencia", methods=['POST'])
@administrador_requerido
def add_incidencia():
    if request.method == "POST":
        # 1. Recepción de datos del formulario
        datos = {
            'nombreIncidencia': request.form['nombreIncidencia'],
            'observacionIncidencia': request.form['observacionIncidencia'],
            'fechaIncidencia': request.form['fechaIncidencia'],
            'idEquipo': request.form['idEquipo']
        }

        # 2. Validar que el ID del equipo sea válido
        if not datos['idEquipo']:
            flash("Error: No se seleccionó un equipo.", "warning")
            return redirect(url_for("equipo.Equipo"))

        try:
            datos['idEquipo'] = int(datos['idEquipo'])
        except ValueError:
            flash("Error: ID de equipo inválido.", "warning")
            return redirect(url_for("equipo.Equipo"))

        cur = mysql.connection.cursor()

        # 3. Verificar si el equipo existe
        cur.execute("SELECT idEquipo FROM equipo WHERE idEquipo = %s", (datos['idEquipo'],))
        equipo_existente = cur.fetchone()
        if not equipo_existente:
            flash("Error: El equipo no existe.", "warning")
            cur.close()
            return redirect(url_for("equipo.Equipo"))
        

        #!CAMBIAR LOGICA PARA COMENZAR A TRABAJAR CON LOS ESTADOS DE LA INCIDENCIA
        # 5. Verificar si existe una incidencia activa para el equipo
        cur.execute("""
            SELECT idIncidencia
            FROM incidencia
            WHERE idEquipo = %s
            AND estadoIncidencia = 'pendiente'
        """, (datos['idEquipo'],))
        incidencia_activa = cur.fetchone()
        if incidencia_activa:
            flash("Error: Ya existe una incidencia pendiente para este equipo.", "warning")
            cur.close()
            return redirect(url_for("incidencia.Incidencia"))
        
        #!------------------------------------------------------------------------
        # 6. Determinar el nuevo estado del equipo
        estados_incidencia = {
            'Robo': 3,             # Siniestro
            'Perdido': 4,          # Baja
            'Dañado/Averiado': 5   # Dañado
        }
        nuevo_estado = estados_incidencia.get(datos['nombreIncidencia'])

        if nuevo_estado is None:
            flash("Tipo de incidencia inválido.", "warning")
            cur.close()
            return redirect(url_for("incidencia.Incidencia"))

        # 7. Actualizar el estado del equipo
        try:
            cur.execute("""
                UPDATE equipo
                SET idEstado_equipo = %s
                WHERE idEquipo = %s
            """, (nuevo_estado, datos['idEquipo']))
            mysql.connection.commit()
        except Exception as e:
            flash("Error al actualizar el estado del equipo: " + str(e), "danger")
            cur.close()
            return redirect(url_for("incidencia.Incidencia"))

        # 8. Insertar la incidencia en la base de datos
        try:
            cur.execute("""
                INSERT INTO incidencia (
                    nombreIncidencia,
                    observacionIncidencia,
                    rutaactaIncidencia,
                    fechaIncidencia,
                    idEquipo,
                    numDocumentos
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                datos['nombreIncidencia'],
                datos['observacionIncidencia'],
                None,  # Ruta del archivo (se actualizará después)
                datos['fechaIncidencia'],
                datos['idEquipo'],
                0
            ))
            mysql.connection.commit()

            # Obtener el ID de la incidencia recién creada
            cur.execute("SELECT LAST_INSERT_ID() as idIncidencia")
            idIncidencia = cur.fetchone()['idIncidencia']
            datos['idIncidencia'] = idIncidencia

            # Crear el PDF y obtener la ruta
            ruta_pdf = create_pdf(datos)

            # Actualizar la incidencia con la ruta del PDF
            cur.execute("""
                UPDATE incidencia
                SET rutaactaIncidencia = %s
                WHERE idIncidencia = %s
            """, (ruta_pdf, idIncidencia))
            mysql.connection.commit()

            flash("Incidencia registrada y PDF generado correctamente.", "success")

        except IntegrityError as e:
            mensaje_error = str(e)
            if "Duplicate entry" in mensaje_error:
                flash("Error: La incidencia ya existe.", "warning")
            else:
                flash("Error de integridad en la base de datos: " + mensaje_error, "danger")
        except Exception as e:
            flash("Error al crear la incidencia: " + str(e), "danger")

        finally:
            cur.close()

        return redirect(url_for("incidencia.Incidencia"))

@incidencia.route("/incidencia/delete_incidencia/<id>", methods=["GET", "POST"])
@administrador_requerido
def delete_incidencia(id):
    # Se asume que la validación de sesión se hace en el decorador @administrador_requerido.
    cur = mysql.connection.cursor()
    try:
        # Verificar el estado de la incidencia
        cur.execute("""
            SELECT estadoIncidencia
            FROM incidencia
            WHERE idIncidencia = %s
        """, (id,))
        incidencia = cur.fetchone()

        if not incidencia:
            flash("Error: La incidencia no existe.", "danger")
            return redirect(url_for("incidencia.Incidencia"))

        estado = incidencia["estadoIncidencia"]

        # Validar que el estado sea "cerrado", "equipo reparado" o "equipo cambiado"
        if estado not in ["cerrado", "equipo reparado", "equipo cambiado"]:
            flash(f"Error: Solo se pueden eliminar incidencias con estado 'cerrado', 'equipo reparado' o 'equipo cambiado'. Estado actual: {estado}.", "warning")
            return redirect(url_for("incidencia.Incidencia"))

        # Eliminar la incidencia si cumple con los criterios
        cur.execute("DELETE FROM incidencia WHERE idIncidencia = %s", (id,))
        mysql.connection.commit()
        flash("Incidencia eliminada correctamente", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("Error al eliminar la incidencia: " + str(e), "danger")
    finally:
        cur.close()

    return redirect(url_for("incidencia.Incidencia"))

@incidencia.route("/incidencia/edit_incidencia/<id>", methods=["GET", "POST"])
@administrador_requerido
def edit_incidencia(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT *
            FROM incidencia
            WHERE incidencia.idIncidencia = %s
                """, (id,))
    incidencia = cur.fetchone()
    return render_template(
        "Operaciones/edit_incidencia.html", 
        incidencia=incidencia
        )

@incidencia.route("/incidencia/update_incidencia/<id>", methods=["POST"])
@administrador_requerido
def update_incidencia(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")

    # Obtener datos del formulario
    estadoIncidencia = request.form.get('estadoIncidencia', '').strip()
    nombreIncidencia = request.form.get('nombreIncidencia', '').strip()
    ObservacionIncidencia = request.form.get('observacionIncidencia', '').strip()
    fechaIncidencia = request.form.get('fechaIncidencia', '').strip()

    # Si ObservacionIncidencia está vacío, asignar None (para almacenar NULL en la BD)
    if not ObservacionIncidencia:
        ObservacionIncidencia = None

    # Mapear estados de incidencia a estados de equipo
    estados_equipo = {
        'pendiente': {
            'Robo': 3,              # Siniestro
            'Perdido': 4,           # Baja
            'Dañado/Averiado': 5    # Mantención
        },
        'abierta': {
            'Robo': 3,
            'Perdido': 4,
            'Dañado/Averiado': 5
        },
        'servicio tecnico': 5,       # Mantención
        'equipo reparado': None,     # Depende de si está asignado
        'equipo cambiado': 2,        # En Uso
        'cerrado': None              # Depende de si está asignado
    }

    cur = mysql.connection.cursor()

    # Actualizar la incidencia
    cur.execute("""
        UPDATE incidencia
        SET estadoIncidencia = %s,
            nombreIncidencia = %s,
            observacionIncidencia = %s,
            fechaIncidencia = %s
        WHERE idIncidencia = %s
    """, (estadoIncidencia, nombreIncidencia, ObservacionIncidencia, fechaIncidencia, id))
    mysql.connection.commit()

    # Obtener el ID del equipo relacionado con la incidencia
    cur.execute("SELECT idEquipo FROM incidencia WHERE idIncidencia = %s", (id,))
    equipo = cur.fetchone()
    if not equipo:
        flash("No se encontró el equipo relacionado con la incidencia.", "danger")
        return redirect(url_for("incidencia.Incidencia"))

    idEquipo = equipo['idEquipo']

    # Determinar el nuevo estado del equipo
    nuevo_estado_equipo = None
    if estadoIncidencia in ['pendiente', 'abierta']:
        nuevo_estado_equipo = estados_equipo[estadoIncidencia].get(nombreIncidencia)
    elif estadoIncidencia == 'servicio tecnico':
        nuevo_estado_equipo = estados_equipo['servicio tecnico']
    elif estadoIncidencia in ['equipo reparado', 'cerrado']:
        # Verificar si el equipo está asignado a un funcionario
        cur.execute("""
            SELECT nombreFuncionario
            FROM super_equipo
            WHERE idEquipo = %s
        """, (idEquipo,))
        asignacion = cur.fetchone()
        if asignacion and asignacion['nombreFuncionario']:
            nuevo_estado_equipo = 2  # En Uso
        else:
            nuevo_estado_equipo = 1  # Sin Asignar
    elif estadoIncidencia == 'equipo cambiado':
        nuevo_estado_equipo = estados_equipo['equipo cambiado']

    # Actualizar el estado del equipo si se determinó un nuevo estado
    if nuevo_estado_equipo is not None:
        cur.execute("""
            UPDATE equipo
            SET idEstado_equipo = %s
            WHERE idEquipo = %s
        """, (nuevo_estado_equipo, idEquipo))
        mysql.connection.commit()

    flash("Incidencia y estado del equipo actualizados correctamente.", "success")
    return redirect(url_for("incidencia.Incidencia"))

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@incidencia.route("/incidencia/adjuntar_pdf/<id>", methods=["POST"])
@administrador_requerido
def adjuntar_pdf(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    #guardar pdf
    file = request.files["file"]
    print("adjuntar incidencia")
    print("inLinux" + str(inLinux()))
    #if inLinux():
    dir ="pdf"
    #else:
        #dir = 'app/pdf' 
    carpeta_incidencias = os.path.join(dir, "incidencia_" + str(id))
    print(carpeta_incidencias)
    #podria dar error pero mejor que tire error y ver cual es
    print(carpeta_incidencias)
    if not os.path.isdir(carpeta_incidencias):
        os.mkdir(carpeta_incidencias)
        print("se creo la carpeta de la incidencia")
    fileName = file.filename
    file.save(os.path.join(
        carpeta_incidencias,
        secure_filename(fileName)
    ))

    
    #obtener incidencia

    cur = mysql.connection.cursor()
    cur.execute("""
                    SELECT *
                     FROM incidencia i
                     WHERE i.idIncidencia = %s
                """, (id,))
    obj_incidencia = cur.fetchone()
    print(obj_incidencia)
    #redirigir a si add_pdf_incidencia
    flash("se subio correctamente")
    return redirect("/incidencia/listar_pdf/" + str(obj_incidencia['idIncidencia']))


@incidencia.route("/incidencia/listar_pdf/<idIncidencia>")
@loguear_requerido
def listar_pdf(idIncidencia):
    # 📂 Ruta de la carpeta donde están los PDFs de esta incidencia
    pdf_directory = "pdf/Incidencias"
    carpeta_incidencia = os.path.join(pdf_directory, f"incidencia_{idIncidencia}")

    # 🔍 Verificar si la carpeta de la incidencia existe
    if not os.path.exists(carpeta_incidencia):
        flash("No hay documentos para esta incidencia.", "warning")
        return redirect(url_for("incidencia.Incidencia"))

    # 📄 Obtener la lista de PDFs en la carpeta
    pdfTupla = tuple(
        fileName for fileName in os.listdir(carpeta_incidencia)
        if fileName.lower().endswith('.pdf')  # Filtra solo archivos PDF
    )

    # 🔄 Actualizar el número de documentos en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE incidencia
        SET numDocumentos = %s
        WHERE idIncidencia = %s
    """, (len(pdfTupla), idIncidencia))
    mysql.connection.commit()

    # 📊 Obtener datos del equipo relacionado con la incidencia
    cur.execute("""
        SELECT * FROM super_equipo WHERE idEquipo = (
            SELECT idEquipo FROM incidencia WHERE idIncidencia = %s
        )
    """, (idIncidencia,))
    data_equipo = cur.fetchone()

    return render_template(
        'Operaciones/mostrar_pdf_incidencia.html', 
        idIncidencia=idIncidencia, 
        documentos=pdfTupla,  # Lista de PDFs encontrados
        equipo=data_equipo, 
        location='incidencia'
    )
            
@incidencia.route("/incidencia/mostrar_pdf/<id>/")
def mostrar_pdf(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT rutaactaIncidencia FROM incidencia WHERE idIncidencia = %s", (id,))
    resultado = cur.fetchone()
    
    if resultado and resultado['rutaactaIncidencia']:
        return send_file(resultado['rutaactaIncidencia'], as_attachment=False)
    else:
        flash("No se encontró el archivo PDF.", "warning")
        return redirect(url_for("incidencia.Incidencia"))


def create_pdf(incidencia):
    from flask import current_app

    cur = mysql.connection.cursor()

    # 📌 Consultar la información del equipo dentro de esta función
    cur.execute("""
        SELECT nombreTipo_equipo, nombreMarcaEquipo, nombreModeloequipo, Num_serieEquipo, Cod_inventarioEquipo
        FROM super_equipo
        WHERE idEquipo = %s
    """, (incidencia['idEquipo'],))

    equipo = cur.fetchone()

    if not equipo:
        current_app.logger.error(f"No se encontró información del equipo con ID {incidencia['idEquipo']}")
        return None  # Evita errores si no hay equipo

    class PDF(FPDF):
        def header(self):
            self.image('static/img/logo_junji.png', 10, 8, 25)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(50, 50, 50)
            self.cell(0, 10, 'JUNTA NACIONAL DE JARDINES INFANTILES', ln=True, align='C')
            self.cell(0, 10, 'Unidad de Inventarios', ln=True, align='C')
            self.ln(10)

        def footer(self):
            self.set_y(-30)
            self.set_font('Arial', 'I', 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, 'Junta Nacional de Jardines Infantiles - JUNJI', ln=True, align='C')
            self.cell(0, 10, 'OHiggins Poniente 77 Concepción - Tel: 041-2125541', ln=True, align='C')
            self.cell(0, 10, 'www.junji.cl', ln=True, align='C')

    # 📂 Crear la carpeta de la incidencia si no existe
    pdf_directory = "pdf/Incidencias"
    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)

    incidencia_folder = os.path.join(pdf_directory, f"incidencia_{incidencia['idIncidencia']}")
    if not os.path.exists(incidencia_folder):
        os.makedirs(incidencia_folder)

    # 📄 Crear el PDF
    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # 📌 Título del documento
    titulo = f"ACTA de Incidencia N° {incidencia['idIncidencia']}"
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)

    # 📌 Información general de la incidencia
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Información de la Incidencia:", ln=True)
    pdf.set_font("Arial", "", 12)

    pdf.cell(50, 10, "Nombre:", border=0)
    pdf.cell(100, 10, incidencia["nombreIncidencia"], border=0, ln=True)

    pdf.cell(50, 10, "Fecha:", border=0)
    pdf.cell(100, 10, incidencia["fechaIncidencia"], border=0, ln=True)

    pdf.ln(10)

    # 📌 Información del equipo afectado
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Equipo Afectado:", ln=True)
    pdf.set_font("Arial", "", 12)

    pdf.cell(50, 10, "Tipo de Equipo:", border=0)
    pdf.cell(100, 10, equipo["nombreTipo_equipo"], border=0, ln=True)

    pdf.cell(50, 10, "Marca:", border=0)
    pdf.cell(100, 10, equipo["nombreMarcaEquipo"], border=0, ln=True)

    pdf.cell(50, 10, "Modelo:", border=0)
    pdf.cell(100, 10, equipo["nombreModeloequipo"], border=0, ln=True)

    pdf.cell(50, 10, "Número de Serie:", border=0)
    pdf.cell(100, 10, equipo["Num_serieEquipo"], border=0, ln=True)

    pdf.cell(50, 10, "Código de Inventario:", border=0)
    pdf.cell(100, 10, equipo["Cod_inventarioEquipo"], border=0, ln=True)

    pdf.ln(10)

    # 📌 Observaciones
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Observaciones:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, incidencia["observacionIncidencia"])
    pdf.ln(10)

    # 📌 Sección para firmas
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Firmas:", ln=True)
    pdf.ln(15)

    # 📌 Espacio para firmas
    pdf.cell(90, 10, "Nombre del Encargado:", border=0)
    pdf.cell(90, 10, "Nombre del Funcionario:", border=0, ln=True)
    pdf.cell(90, 10, "_____________________________", border=0)
    pdf.cell(90, 10, "_____________________________", border=0, ln=True)
    pdf.ln(5)

    pdf.cell(90, 10, "Firma del Encargado:", border=0)
    pdf.cell(90, 10, "Firma del Funcionario:", border=0, ln=True)
    pdf.cell(90, 10, "_____________________________", border=0)
    pdf.cell(90, 10, "_____________________________", border=0, ln=True)

    # 📄 Guardar el PDF en la carpeta de la incidencia
    nombre_pdf = f"incidencia_{incidencia['idIncidencia']}.pdf"
    ruta_pdf = os.path.join(incidencia_folder, nombre_pdf)
    pdf.output(ruta_pdf)

    return ruta_pdf

    

@incidencia.route("/incidencia/buscar/<idIncidencia>")
@loguear_requerido
def buscar(idIncidencia):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    
    cur = mysql.connection.cursor()
    
    # Obtener la incidencia por su ID
    cur.execute("""
        SELECT i.idIncidencia, i.nombreIncidencia, i.observacionIncidencia,
            i.rutaactaIncidencia, i.fechaIncidencia, i.idEquipo,
            e.cod_inventarioEquipo, e.Num_serieEquipo, 
            te.nombreTipo_equipo, me.nombreModeloequipo,
            i.numDocumentos, e.idEquipo
        FROM incidencia i
        INNER JOIN equipo e ON i.idEquipo = e.idEquipo
        INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
        INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE i.idIncidencia = %s
    """, (idIncidencia,))
    data = cur.fetchone()  # Cambiado a fetchone() porque idIncidencia es único.

    # Obtener el total de incidencias
    cur.execute('SELECT COUNT(*) AS total FROM incidencia')
    total = cur.fetchone()['total']  # Simplificado.

    return render_template(
        "Operaciones/incidencia.html", 
        Incidencia=[data],  # Envolvemos en una lista para mantener compatibilidad con el template.
        page=1, 
        lastpage=True
    )
