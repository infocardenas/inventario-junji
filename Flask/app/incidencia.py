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
            i.numDocumentos
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
@incidencia.route("/incidencia/add_incidencia", methods=['POST'])
@administrador_requerido
def add_incidencia():
    if request.method == "POST":
        # 1. Recepción de datos
        datos = {
            'nombreIncidencia': request.form['nombreIncidencia'],
            'observacionIncidencia': request.form['observacionIncidencia'],
            'fechaIncidencia': request.form['fechaIncidencia'],
            'idEquipo': request.form['idEquipo']
        }

        # 2. Validar si el ID del equipo está vacío o es inválido
        if not datos['idEquipo']:
            flash("Error: No se seleccionó un equipo.", "warning")
            return redirect(url_for("equipo.Equipo"))

        try:
            datos['idEquipo'] = int(datos['idEquipo'])
        except ValueError:
            flash("Error: ID de equipo inválido.", "warning")
            return redirect(url_for("equipo.Equipo"))

        # 3. Verificar si ya existe una incidencia activa para el equipo
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) AS count 
            FROM incidencia 
            WHERE idEquipo = %s
        """, (datos['idEquipo'],))
        incidencia_existente = cur.fetchone()

        if incidencia_existente and incidencia_existente['count'] > 0:
            flash("Este equipo ya tiene una incidencia registrada.", "warning")
            return redirect(url_for("incidencia.Incidencia"))

        # 4. Asignar el estado del equipo según la incidencia
        estados_incidencia = {
            'Robo': 3,              # Siniestro
            'Perdido': 4,           # Baja
            'Dañado/Averiado': 5    # Mantención
        }

        nuevo_estado = estados_incidencia.get(datos['nombreIncidencia'])
        if nuevo_estado is None:
            flash("Tipo de incidencia inválido.", "warning")
            return redirect(url_for("incidencia.Incidencia"))

        # 5. Insertar la incidencia en la base de datos
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
                None,  # Ruta del archivo (no se maneja en este paso)
                datos['fechaIncidencia'],
                datos['idEquipo'],
                0
            ))
            mysql.connection.commit()

            # 6. Actualizar el estado del equipo según la incidencia
            cur.execute("""
                UPDATE equipo
                SET idEstado_equipo = %s
                WHERE idEquipo = %s
            """, (nuevo_estado, datos['idEquipo']))
            mysql.connection.commit()

            flash("Incidencia registrada correctamente y estado actualizado.", "success")
            return redirect(url_for("incidencia.Incidencia"))

        except IntegrityError as e:
            mensaje_error = str(e)
            if "Duplicate entry" in mensaje_error:
                flash("Error: La incidencia ya existe.", "warning")
            else:
                flash("Error de integridad en la base de datos: " + mensaje_error, "danger")
            return redirect(url_for("incidencia.Incidencia"))
        except Exception as e:
            flash("Error al crear la incidencia: " + str(e), "danger")
            return redirect(url_for("incidencia.Incidencia"))



        
        
@incidencia.route("/incidencia/delete_incidencia/<id>",  methods=["GET", "POST"])
@administrador_requerido
def delete_incidencia(id):
    # Se asume que la validación de sesión se hace en el decorador @administrador_requerido.
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM incidencia WHERE idIncidencia = %s", (id,))
        mysql.connection.commit()
        flash("Incidencia eliminada correctamente", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("Error al eliminar la incidencia: " + str(e), "danger")
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
   nombreIncidencia = request.form['nombreIncidencia'] 
   ObservacionIncidencia = request.form['observacionIncidencia']
   fechaIncidencia = request.form['fechaIncidencia']

   
   cur = mysql.connection.cursor()
   cur.execute("""
        UPDATE incidencia
        SET nombreIncidencia = %s,
            observacionIncidencia = %s,
            fechaIncidencia = %s
        WHERE idIncidencia = %s
               """, (nombreIncidencia, ObservacionIncidencia, fechaIncidencia, id)) 
   mysql.connection.commit()
   flash("Incidencia actualizada correctamente")
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
    #verificar la existencia de la carpeta incidencia
    #try:
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT idEquipo
    FROM incidencia i
    WHERE i.idIncidencia = %s
                """, (idIncidencia,))
    Incidencia = cur.fetchone()
    print(Incidencia)
    idEquipo = Incidencia['idEquipo']
    cur.execute("""
                SELECT *
                FROM super_equipo e
                WHERE e.idEquipo = %s
                """, (idEquipo,))
    data_equipo = cur.fetchone()
    #if inLinux():
    dir = "pdf"
    #else:
        #dir = "app/pdf"
    carpeta_incidencias = os.path.join(dir, "incidencia_" + str(idIncidencia))
    if(not os.path.exists(carpeta_incidencias)):
        #insertar numero de documentos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE incidencia
            SET numDocumentos = %s
            WHERE idIncidencia = %s
                    """, (0 , Incidencia['idEquipo']))
        mysql.connection.commit()
        print("equipo")
        print(data_equipo)
        return render_template(
            'Operaciones/mostrar_pdf_incidencia.html', 
            idIncidencia=idIncidencia,
            documentos=(), 
            equipo=data_equipo
            )

        
    #except:
        #flash("ERROR")
        #return redirect(url_for("incidencia.Incidencia"))

    #obtener un listado de los nombres de la carpeta
    #generar las tuplas tal que se pueda abrir en otra ventana
    print("pdfTupla añadir documentos")
    pdfTupla = []
    print("antes de crear pdfTupla")
    for fileName in os.listdir(carpeta_incidencias):
        print(fileName)
        #if(fileName.endswith('.pdf') or fileName.endswith('.PDF')): #¿pueden existir .pDf?, se podria arreglar con un split . y la segunda parte toLower asi siempre en minuscula
        pdfTupla.append(fileName) 
    print(pdfTupla)
    pdfTupla = tuple(pdfTupla)

    #TODO:
    #insertar numero de documentos
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE incidencia
        SET numDocumentos = %s
        WHERE idIncidencia = %s
                """, (len(pdfTupla), idIncidencia))
    mysql.connection.commit()
    
    return render_template(
        'Operaciones/mostrar_pdf_incidencia.html', 
        idIncidencia=idIncidencia, 
        documentos=pdfTupla, 
        equipo=data_equipo, 
        location='incidencia'
        )
            
@incidencia.route("/incidencia/mostrar_pdf/<id>/<nombrePdf>")
@loguear_requerido
def mostrar_pdf(id, nombrePdf):
    try:
        nombrePdf = nombrePdf
        dir = 'pdf'
        #busca la carpeta de la incidencia asociada a la id
        carpeta_incidencias = os.path.join(dir, "incidencia_" + str(id))
        file = os.path.join(carpeta_incidencias, nombrePdf)
        print("file")
        print(file)
        return send_file(file, as_attachment=False )
    except:
        flash("no se encontro pdf")
        return redirect(url_for("incidencia.Incidencia"))
#def create_pdf(Incidencia):
    
    #class PDF(FPDF):
        #def header(self):
            ##logo
            ##imageUrl = url_for('static', filename='img/logo_junji.png')
            ##print(imageUrl)
            #self.image('logo_junji.png', 10, 8, 25)
            ##font
            #self.set_font('times', 'B', 12)
            #self.set_text_color(170,170,170)
            ##Title
            #self.cell(0, 30, '', border=False, ln=1, align='L')
            #self.cell(0, 5, 'JUNTA NACIONAL', border=False, ln=1, align='L')
            #self.cell(0, 5, 'INFANTILES', border=False, ln=1, align='L')
            #self.cell(0, 5, 'Unidad de Inventarios', border=False, ln=1, align='L')
            ##line break
            #self.ln(10)
        
        #def footer(self):
            #self.set_y(-30)
            #self.set_font('times', 'B', 12)
            #self.set_text_color(170,170,170)
            #self.cell(0,0, "", ln=1)
            #self.cell(0,0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
            #self.cell(0,12, "OHiggins Poniente 77 Concepción. 041-2125541", ln=1) #problema con el caracter ’
            #self.cell(0,12, "www.junji.cl", ln=1)
     
    #pdf = PDF('P', 'mm', 'A4')
    #pdf.add_page()


    #nombrePdf = "incidencia_" + str(Incidencia['idIncidencia']) + ".pdf"
    #pdf.output(nombrePdf)
    #shutil.move(nombrePdf, "app/pdf")
    #return

#@incidencia.route("/incidencia/mostrar_pdf/<id>")
#def mostrar_pdf(id):
    #pass
    

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
