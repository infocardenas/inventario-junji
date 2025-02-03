from email.mime.application import MIMEApplication
from flask import Blueprint, render_template, request, url_for, redirect, flash, send_file, session
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
import os
import shutil
from werkzeug.utils import secure_filename
from datetime import date
from cuentas import loguear_requerido, administrador_requerido
from traslado import crear_traslado_generico
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import fitz
from env_vars import paths, inLinux

asignacion = Blueprint("asignacion", __name__, template_folder="app/templates")

PDFS_DIR = paths['pdf_path']
@asignacion.route("/asignacion")
@asignacion.route("/asignacion/<page>")
@loguear_requerido
def Asignacion(page=1):
    #La url viene como string por lo que se convierte a int
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()
    #para la tabla
    cur.execute(
        """ 
    SELECT  
        a.idAsignacion,
        a.fecha_inicioAsignacion,
        a.ObservacionAsignacion,
        a.fechaDevolucion,
        a.ActivoAsignacion,
        f.rutFuncionario,
        f.nombreFuncionario,
        f.cargoFuncionario,
        me.nombreModeloequipo,
        te.nombreTipo_equipo,
        mae.nombreMarcaEquipo
    FROM asignacion a
    INNER JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
    LEFT JOIN equipo_asignacion ea ON a.idAsignacion = ea.idAsignacion
    LEFT JOIN equipo e ON e.idEquipo = ea.idEquipo
    LEFT JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
    LEFT JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
    LEFT JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
    LEFT JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
    LIMIT %s OFFSET %s
        """, (perpage, offset)
    )
    data = cur.fetchall()
    print(data)
    for row in data:
        row['fecha_inicio'] = row['fecha_inicioAsignacion'].strftime('%d-%m-%Y') if row['fecha_inicioAsignacion'] else 'N/A'
        row['fecha_devolucion'] = row['fechaDevolucion'].strftime('%d-%m-%Y') if row['fechaDevolucion'] else 'Sin devolver'

    cur.execute(
        """ SELECT 
            f.rutFuncionario,
            f.nombreFuncionario 
        FROM funcionario f
        ORDER BY f.nombreFuncionario
        """
    )
    funcionarios = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM asignacion')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    cur.execute(
        """
    SELECT 
        e.idEquipo,
        e.Cod_inventarioEquipo,
        e.Num_serieEquipo,
        e.codigoproveedor_equipo,
        me.nombreModeloequipo,
        te.nombreTipo_equipo,
        mae.nombreMarcaEquipo,
        u.nombreUnidad
    FROM equipo e
    JOIN modelo_equipo me ON e.idModelo_equipo = me.idModelo_Equipo
    JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
    JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
    JOIN marca_equipo mae ON mte.idMarca_Equipo = mae.idMarca_Equipo
    JOIN estado_equipo ee ON e.idEstado_equipo = ee.idEstado_equipo
    JOIN unidad u ON e.idUnidad = u.idUnidad
    WHERE ee.nombreEstado_equipo = 'SIN ASIGNAR';
        """
    )
    equipos_sin_asignar = cur.fetchall()
    return render_template(
        'GestionR.H/asignacion.html', 
        funcionarios=funcionarios, 
        asignacion=data,
        equipos_sin_asignar = equipos_sin_asignar,
        page=page, 
        lastpage= page < (total / perpage) + 1
        )

@asignacion.route("/add_asignacion", methods=["GET"])
@asignacion.route("/add_asignacion/<idEquipo>")
@administrador_requerido
def add_asignacion(idEquipo = "None"):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if(idEquipo != "None"):
        idEquipo = int(idEquipo)
    cur = mysql.connection.cursor()
    #los funcionarios son para el select en el formulario de agregar
    cur.execute("""
                SELECT *
                FROM funcionario f
                """)
    funcionarios_data = cur.fetchall()

    #estos son los equipos que van en la tabla para adjuntar a la asignacion
    #tienen que ser los sin asignar por que los otros ya estan asignados a otros 
    #funcionarios
    cur.execute("""
                SELECT e.*, 
                    me.nombreModeloequipo, 
                    te.nombreTipo_equipo, 
                    u.nombreUnidad, 
                    ee.nombreEstado_equipo
                FROM equipo e
                INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
                INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
                INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
                INNER JOIN unidad u ON e.idUnidad = u.idUnidad
                INNER JOIN estado_equipo ee ON ee.idEstado_Equipo = e.idEstado_Equipo
                WHERE ee.nombreEstado_equipo = %s
                """, ("SIN ASIGNAR",))
    equipos_data = cur.fetchall()
    return render_template(
        'GestionR.H/add_asignacion.html',
        equipos=equipos_data,
        funcionarios=funcionarios_data,
        equipoSeleccionado = idEquipo
        )



# enviar datos a vista editar
@asignacion.route("/asignacion/edit_asignacion/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        #se obtiene la asignacion actual
        cur.execute(
            """ 
           SELECT  
                a.idAsignacion,
                a.fecha_inicioAsignacion,
                a.observacionAsignacion,
                a.rutaactaAsignacion,
                a.rutFuncionario,
                f.nombreFuncionario,
                d.fechaDevolucion
                FROM asignacion a
                INNER JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
                LEFT JOIN devolucion d ON a.idDevolucion = d.idDevolucion
            WHERE idAsignacion = %s""",
            (id,),
        )
        #esto para los select
        data = cur.fetchone()
        cur.execute("SELECT * FROM funcionario")
        f_data = cur.fetchall()
        #creo que el equipo se deberia porder borrar
        cur.execute("SELECT * FROM equipo")
        eq_data = cur.fetchall()
        #print(data)
        #print(data['observacionAsignacion'])
        return render_template(
            'GestionR.H/editAsignacion.html', 
            asignacion=data, 
            funcionario=f_data, 
            equipo=eq_data
        )
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))


# actualizar
@asignacion.route("/asignacion/update_asignacion/<id>", methods=["POST"])
@administrador_requerido
def update_asignacion(id):
    if request.method == "POST":
        #obtener informacion del formulario
        fechaasignacion = request.form["fechaasignacion"]
        observacionasignacion = request.form["observacionasignacion"]
        rutFuncionario = request.form["rutFuncionario"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE asignacion
            SET fecha_inicioAsignacion = %s,
                ObservacionAsignacion = %s,
                rutFuncionario = %s
            WHERE idAsignacion = %s
            """,
                (
                    fechaasignacion,
                    observacionasignacion,
                    rutFuncionario,
                    id,
                ),
            )
            mysql.connection.commit()
            flash("asignacion actualizado correctamente")
            return redirect(url_for("asignacion.Asignacion"))
        except Exception as e:

            flash("Error al crear")
            #flash(e.args[1])
            return redirect(url_for("asignacion.Asignacion"))


# eliminar
@asignacion.route("/delete_asignacion/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT *
                    FROM asignacion
                    WHERE idAsignacion = %s
                    """, (id,))
        asignacionAborrar = cur.fetchone()
        #encontrar todas las tablas equipo_asignacion que contengan la id de la asignacion
        cur.execute("""SELECT *
                        FROM equipo_asignacion
                        WHERE idAsignacion= %s
        """, (id,))
        asignaciones = cur.fetchall()
        #revisar cada equipo_asignacion individualmente
        for asignacion in asignaciones:
            idEquipo = asignacion['idEquipo']
            #encontrar la id del estado sin asignar
            cur.execute("""
                        SELECT *
                        FROM estado_equipo
                        WHERE nombreEstado_equipo = %s
                        """, ("SIN ASIGNAR",))
            estado_equipo_data = cur.fetchone()
            #cambiar el estado de cada equipo en la asignacion eliminada a sin asignar
            cur.execute("""
                        UPDATE equipo
                        SET idEstado_equipo = %s
                        WHERE idEquipo = %s
                        """, (estado_equipo_data['idEstado_equipo'], idEquipo))
            mysql.connection.commit()
        cur.execute("DELETE FROM equipo_asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        cur.execute("DELETE FROM asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        flash("asignacion eliminado correctamente")
        return redirect(url_for("asignacion.Asignacion"))
    except Exception as e:
        flash("Error al crear")
        #flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))

# Esta función extrae la informacion del formulario
@asignacion.route("/asignacion/create_asignacion", methods=["POST"])
@administrador_requerido
def create_asignacion():
    if request.method == "POST":
        fecha_asignacion = request.form.get('fecha-asignacion') 
        rut_funcionario = request.form.get('rut_funcionario')
        observacion = request.form.get('observacion')
        id_equipos = request.form.getlist('equiposAsignados[]')
        realizar_traslado = request.form.get('traslado')

        return creacionAsignacion(fecha_asignacion, observacion, rut_funcionario, id_equipos, realizar_traslado)


#Este metodo es el que crea la asignacion
@administrador_requerido
def creacionAsignacion(fecha_asignacion, observacion, rut, id_equipos, realizar_traslado):
    cur = mysql.connection.cursor()
    #el 1 al final de values es por el ActivoAsignacion que muestra que la asignacion no ha sido devuelta
    cur.execute("""
        INSERT INTO asignacion (
            fecha_inicioAsignacion,
            ObservacionAsignacion,
            rutaactaAsignacion, 
            rutFuncionario,
            ActivoAsignacion
        )
        VALUES (%s, %s, %s, %s, 1)
        """, (fecha_asignacion, observacion, 'ruta', rut))
    mysql.connection.commit()

    # Recuperar el ID de la asignación recién insertada
    asignacion_id = cur.lastrowid


    TuplaEquipos = ()
    # Iterar sobre los equipos y realizar las operaciones necesarias
    for id_equipo in id_equipos:
        # Insertar en la tabla Equipo_asignacion
        cur.execute("""
            INSERT INTO equipo_asignacion (idAsignacion, idEquipo)
            VALUES (%s, %s)
            """, (str(asignacion_id),id_equipo))
        mysql.connection.commit()
        #encontrar la id del estado EN USO
        cur.execute("""
                    SELECT *
                    FROM estado_equipo
                    WHERE nombreEstado_equipo = %s
                    """, ("EN USO",))
        estado_equipo_data = cur.fetchone() 
            
        #cambiar el estado de los equipos a en uso
        cur.execute("""
                    UPDATE equipo
                    SET idEstado_equipo = %s
                    WHERE idEquipo = %s
                    """, (estado_equipo_data['idEstado_equipo'], id_equipo))
        mysql.connection.commit()
            
        #Seleccionar el equipo de equipo_asignacion y agregarlo a una tupla para el excel

        cur.execute("""
                    SELECT e.*, 
                        me.nombreModeloequipo, 
                        te.nombreTipo_equipo, 
                        mae.nombreMarcaEquipo, 
                        ee.nombreEstado_equipo
                    FROM equipo e
                    INNER JOIN modelo_equipo me ON me.idModelo_Equipo = e.idModelo_Equipo
                    INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
                    INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
                    INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
                    INNER JOIN estado_equipo ee ON ee.idEstado_equipo = e.idEstado_equipo
                    WHERE e.idEquipo = %s
                    """, (id_equipo,))
        equipoTupla = cur.fetchone()
        TuplaEquipos = TuplaEquipos + (equipoTupla,)

    flash("Asignación creada correctamente")
    #agregar argumentos para el excel
    cur.execute("""
                SELECT *
                FROM funcionario f
                WHERE f.rutFuncionario = %s
                """, (rut,))
    Funcionario = cur.fetchone()
    cur.execute("""
                SELECT *
                FROM unidad u
                WHERE u.idUnidad = %s
                """, (Funcionario['idUnidad'],))
    Unidad = cur.fetchone()
    cur.execute("""
                SELECT *
                FROM asignacion a
                WHERE a.idAsignacion = %s
                """, (asignacion_id,))
    Asignacion = cur.fetchone()


    pdf_asignacion = crear_pdf(Funcionario, Unidad, Asignacion, TuplaEquipos)
    if(realizar_traslado and Funcionario['idUnidad'] == 1):
        #TODO: que hacer si multiples equipos vienen de distintas direcciones

        #mover desde su posicion actual a la posicion del funcionario
        #primero revisar si las posiciones son iguales.

        
        #si son distintas redirigir al metodo de crear traslado con
        #la informacion de la asignacion

        crear_traslado_generico(fecha_asignacion, Funcionario['idUnidad']
                                ,Unidad['idUnidad'], id_equipos)
    return redirect(url_for('asignacion.Asignacion'))

def crear_pdf(Funcionario, Unidad, Asignacion, Equipos):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    class PDF(FPDF):
        def header(self):
            #imagen del encabezado
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

    #P Portrait -> Vertical
    #mm milimetros
    #A4 formato de tamaño

    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    titulo = "ACTA De Asignacion de Equipo Informatico N°" + str(Asignacion['idAsignacion'])

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    creado_por = "Documento creado por: " + session['user']
    pdf.cell(0, 10, creado_por, ln=True, align="L")
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombreFuncionario = Funcionario["nombreFuncionario"]
    nombreUnidad = Unidad["nombreUnidad"]
    fechaAsignacion = str(Asignacion["fecha_inicioAsignacion"])

    pdf.ln(10)
    #se hace en columnas para que quede ordenado
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(presentacion1)
        cols.ln()
        cols.write(presentacion2)
        cols.ln()
        cols.write(presentacion22)
        cols.ln()
        cols.ln()
        cols.write(presentacion3)
        cols.ln()
        cols.new_column()
        #lo que se escribe despues de new_column va en la siguiente columna
        cols.write(nombreFuncionario)
        cols.ln()
        cols.write(nombreUnidad)
        cols.ln()
        cols.write(fechaAsignacion)

    pdf.ln(20)
    #Encabezado de la tabla
    TABLE_DATA = (
        ("N°", "Tipo_Equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    i = 0
    for equipo in Equipos:
        id = str(equipo["idEquipo"])
        tipo_equipo = equipo["nombreTipo_equipo"]
        marca = equipo["nombreMarcaEquipo"]
        modelo = equipo["nombreModeloequipo"]
        num_serie = str(equipo["Num_serieEquipo"])
        num_inventario = str(equipo["Cod_inventarioEquipo"])

        i += 1

        TABLE_DATA = TABLE_DATA + (
            (str(i), tipo_equipo, marca, modelo, num_serie, num_inventario),
        )
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)

    observacion = "Esta es una observacion"

    pdf.ln(10)
    nombreEncargado = "Nombre Encargado TI:" + session['user']
    rutEncargado = "Numero de RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre Funcionario:"
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
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
    nombrePdf = "asignacion_" + str(Asignacion["idAsignacion"]) + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, "pdf/" + nombrePdf)
    #try:
    #funcion para enviar un correo a un funcionario (se envia el acta)
        #enviar_correo(nombrePdf, 'correo')
    #except:
        #TODO: agregar error
        #flash("no se pudo enviar el correo")
    return nombrePdf

@asignacion.route("/asignacion/mostrar_pdf/<id>")
@loguear_requerido
def mostrar_pdf(id):
    if inLinux():
        nombrePdf = "asignacion_" + str(id) + ".pdf"
        dir = 'pdf' 
        file = os.path.join(dir, nombrePdf)
        if os.path.exists(file):
            print('file')
            return send_file(file, as_attachment=True)
        else:
            flash("no se encontro el pdf")
            return redirect("/asignacion")
    else:
        nombrePdf = "asignacion_" + str(id) + ".pdf"
        dir = 'pdf' 
        file = os.path.join(dir, nombrePdf)
        if os.path.exists(file):
            print("mostrar_pdf")
            print(file)
            return send_file(file, as_attachment=True)
        else:
            flash("no se encontro el pdf")
            return redirect("/asignacion")
        #flash("no se encontro el pdf")
        #return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/devolver/<id>")
@administrador_requerido
def devolver(id):
    today = date.today()
    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE asignacion a
    SET a.ActivoAsignacion = 0,
        fechaDevolucion = %s
    WHERE a.idAsignacion = %s
                """, (today, id,))
    mysql.connection.commit()

    #buscar argumentos
    cur.execute("""
    SELECT *
    FROM asignacion a
    WHERE a.idAsignacion = %s
                """, (id,))
    Asignacion = cur.fetchone()
    cur.execute("""
    SELECT *
    FROM funcionario f
    WHERE f.rutFuncionario = %s
                """, (Asignacion['rutFuncionario'], ))
    Funcionario = cur.fetchone()
    cur.execute("""
    SELECT *
    FROM unidad u
    WHERE u.idUnidad = %s
                """, (str(Funcionario['idUnidad']),))
    Unidad = cur.fetchone()
    
    cur.execute("""
    SELECT * 
    FROM equipo_asignacion ea
    WHERE ea.idAsignacion = %s
                """, (str(Asignacion['idAsignacion']),))
    equipo_asignacion_data = cur.fetchall()

    tupla_equipos = ()
    for equipo_asignacion in equipo_asignacion_data:
        cur.execute("""
        SELECT e.*, 
            me.nombreModeloequipo, 
            te.nombreTipo_equipo, 
            mae.nombreMarcaEquipo, 
            ee.nombreEstado_equipo, 
            u.nombreUnidad
        FROM equipo e
        INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
        INNER JOIN marca_tipo_equipo mte ON me.idMarca_Tipo_Equipo = mte.idMarcaTipo
        INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = mte.idMarca_Equipo
        INNER JOIN unidad u ON e.idUnidad = u.idUnidad
        INNER JOIN estado_equipo ee ON ee.idEstado_equipo = e.idEstado_Equipo
        WHERE e.idEquipo = %s
                    """, (str(equipo_asignacion['idEquipo']),))
        equipo = cur.fetchone()

        cur.execute("""
        SELECT *
        FROM estado_equipo ee
        WHERE ee.nombreEstado_equipo = "SIN ASIGNAR"
                    """)
        estadoEquipo = cur.fetchone()
        cur.execute("""
        UPDATE equipo
        SET idEstado_equipo = %s
        WHERE idEquipo = %s
                    """, (str(estadoEquipo['idEstado_equipo']), str(equipo['idEquipo'])))
        mysql.connection.commit()
        tupla_equipos = tupla_equipos + (equipo,)


    crear_pdf_devolucion(Funcionario, Unidad, Asignacion, tupla_equipos)
    return redirect(url_for('asignacion.Asignacion'))


def crear_pdf_devolucion(
        Funcionario,
        Unidad,
        Asignacion,
        Equipos):
    class PDF(FPDF):
        def header(self):
            #logo
            #imageUrl = url_for('static', filename='img/logo_junji.png')
            #print(imageUrl)
            self.image('logo_junji.jpg', 10, 8, 25)
            #font
            self.set_font('times', 'B', 12)
            self.set_text_color(170,170,170)
            #Title
            self.cell(0, 30, '', border=False, ln=1, align='L')
            self.cell(0, 5, 'JUNTA NACIONAL', border=False, ln=1, align='L')
            self.cell(0, 5, 'INFANTILES', border=False, ln=1, align='L')
            self.cell(0, 5, 'Unidad de Inventarios', border=False, ln=1, align='L')
            #line break
            self.ln(10)

        def footer(self):
                self.set_y(-30)
                self.set_font('times', 'B', 12)
                self.set_text_color(170,170,170)
                self.cell(0,0, "", ln=1)
                self.cell(0,0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
                self.cell(0,12, "OHiggins Poniente 77 Concepción. Tel: 412125579", ln=1) #problema con el caracter ’
                self.cell(0,12, "www.junji.cl", ln=1)
        
    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    titulo = "ACTA Devolucion de Equipo Informatico N°" + str(Asignacion['idAsignacion'])
    creado_por = "Documento creado por: " + session['user']

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    pdf.cell(0, 10, creado_por, ln=True, align="L")
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombreFuncionario = Funcionario["nombreFuncionario"]
    nombreUnidad = Unidad["nombreUnidad"]
    fechaAsignacion = str(Asignacion["fecha_inicioAsignacion"])

    pdf.ln(10)
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(presentacion1)
        cols.ln()
        cols.write(presentacion2)
        cols.ln()
        cols.write(presentacion22)
        cols.ln()
        cols.ln()
        cols.write(presentacion3)
        cols.ln()
        cols.new_column()
        cols.write(nombreFuncionario)
        cols.ln()
        cols.write(nombreUnidad)
        cols.ln()
        cols.write(fechaAsignacion)

    pdf.ln(20)
    TABLE_DATA = (
        ("N°", "Tipo_Equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    i = 0
    for equipo in Equipos:
        id = str(equipo["idEquipo"])
        tipo_equipo = equipo["nombreTipo_equipo"]
        marca = equipo["nombreMarcaEquipo"]
        modelo = equipo["nombreModeloequipo"]
        num_serie = str(equipo["Num_serieEquipo"])
        num_inventario = str(equipo["Cod_inventarioEquipo"])

        i += 1

        TABLE_DATA = TABLE_DATA + (
            (str(i), tipo_equipo, marca, modelo, num_serie, num_inventario),
        )
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)

    observacion = "Esta es una observacion"
    pdf.ln(10)
    nombreEncargado = "Nombre Encargado TI:" 
    rutEncargado = "Numero de RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre Funcionario:"
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
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
    creado_por = "documento creado por: " + session['user']
    nombrePdf = "devolucion_" + str(Asignacion["idAsignacion"]) + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, "pdf/")

@asignacion.route("/asignacion/mostrar_pdf_devolucion/<id>")
@loguear_requerido
def mostrar_pdf_devolucion(id):
    try:
        nombrePdf = "devolucion_" + str(id) + ".pdf"
        dir = 'pdf' 
        file = os.path.join(dir, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/buscar/<idAsignacion>")
@loguear_requerido
def buscar(idAsignacion):
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT  
        a.idAsignacion,
        a.fecha_inicioAsignacion,
        a.observacionAsignacion,
        a.rutaactaAsignacion,
        f.nombreFuncionario,
        a.fechaDevolucion,
        a.ActivoAsignacion
    FROM asignacion a
    INNER JOIN funcionario f ON a.rutFuncionario = f.rutFuncionario
    WHERE a.idAsignacion = %s
        """, (idAsignacion,)
    )
    #solo tiene un elemento pero se extraen todas para reusar el html
    Asignaciones = cur.fetchall()

    cur.execute(
        """ SELECT 
            f.rutFuncionario,
            f.nombreFuncionario 
        FROM funcionario f
        ORDER BY f.nombreFuncionario
        """
    )
    funcionarios = cur.fetchall()

    return render_template(
        'GestionR.H/asignacion.html',  
        funcionarios=funcionarios, 
        asignacion=Asignaciones,
        page=1, 
        lastpage=True
    )
#@asignacion.route("/asignacion/buscar_devolucion/<idDevolucion>")
#@loguear_requerido
#def buscar_devolucion():

    #pass

@asignacion.route("/asignacion/devolver_uno/<id_equipo>")
@administrador_requerido
def devolver_uno(id_equipo):
    def consulta():
        cur = mysql.connection.cursor()
        #encontrar la id de la asignacion del equipo
        cur.execute("""
        SELECT * 
        FROM equipo_asignacion ea
        INNER JOIN asignacion a ON ea.idAsignacion = a.idAsignacion 
        WHERE ea.idEquipo = %s
        AND a.ActivoAsignacion = 1
                    """, (id_equipo,))
        asignacion_vieja = cur.fetchone()
        #si tiene mas de uno seguir de lo contrario redirigir a devolucion
        #encontar todos los equipos excepto el que se devuelve
        cur.execute("""
        SELECT *
        FROM equipo_asignacion ea
        WHERE NOT ea.idEquipo = %s
        AND ea.idAsignacion = %s
                    """, (id_equipo, asignacion_vieja['idAsignacion']))
        equipos = cur.fetchall()
        return (asignacion_vieja, equipos)
    resultados_consulta = consulta()
    equipos = resultados_consulta[1]
    asignacion_vieja = resultados_consulta[0]

    if len(equipos) == 0:
        return devolver(asignacion_vieja['idAsignacion'])
    #else:
        #flash("Este equipo forma parte de una asignacion de multiples equipos")
        #return redirect('/equipo')
    #extraer las ids
    equipos_id = []
    for equipo in equipos:
        equipos_id.append(equipo['idEquipo'])

        
    print("asignacion vieja")
    print(asignacion_vieja)
    devolver(asignacion_vieja['idAsignacion'])
    creacionAsignacion(str(date.today()), asignacion_vieja['ObservacionAsignacion'], 
                asignacion_vieja['rutFuncionario'], equipos_id, True)


    #cambiar redirect
    return redirect("/equipo")

@asignacion.route("/asignacion/listar_pdf/<idAsignacion>")
@asignacion.route("/asignacion/listar_pdf/<idAsignacion>/<devolver>")
@loguear_requerido
def listar_pdf(idAsignacion, devolver="None"):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    dir = 'pdf'   
    if devolver == "None":
        nombreFirmado = "asignacion_" + str(idAsignacion) + "_" + "firmado.pdf"
        location = "asignacion"
    else:
        nombreFirmado = "devolucion_" + str(idAsignacion) + "_" + "firmado.pdf"
        #print(nombreFirmado)
        location = "devolucion"
    #revisa si el archivo esta firmado
    if not os.path.exists(os.path.join(dir, nombreFirmado)):
        #mostrar
        #print("#####NombreFirmado = None #######")
        nombreFirmado = "None"
    #print("exists")
    return render_template(
        'GestionR.H/firma.html', 
        nombreFirmado=nombreFirmado, 
        id=idAsignacion, 
        location=location
        )





@asignacion.route("/devolucion/mostrar_pdf/<id>/<nombreArchivo>")
@loguear_requerido
def mostrar_pdf_devolucion_fimarmado(id, nombreArchivo):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        nombrePdf = "devolucion_" + str(id) + "_firmado.pdf"
        dir = 'pdf' 
        file = os.path.join(dir, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/mostrar_pdf/<id>/<nombreArchivo>")
@loguear_requerido
def mostrar_pdf_asignacion_fimarmado(id, nombreArchivo):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        nombrePdf = "asignacion_" + str(id) + "_firmado.pdf"
        dir =  'pdf'
        file = os.path.join(dir, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/adjuntar_pdf/<idAsignacion>", methods=["POST"])
@administrador_requerido
def adjuntar_pdf_asignacion(idAsignacion):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    #TODO: revisar que sea pdf
    file = request.files["file"]
    #subir archivo
    if inLinux:
        dir = 'pdf'
    else:
        dir = 'app/pdf' #TODO cuando la ruta relativa es app/pdf y cuando es pdf?
    filenameToDelete = "asignacion_" + str(idAsignacion) + "_firmado.pdf"
    filenameToDelete = secure_filename(filenameToDelete)
    if os.path.exists(os.path.join(dir, filenameToDelete)):
        os.remove(os.path.join(dir, filenameToDelete))
    #renombrar archivo
    filename = file.filename
    sfilename = secure_filename(filename)
    file.save(os.path.join(
        dir, secure_filename(sfilename)
    ))

    os.rename(os.path.join(dir, sfilename), 
              os.path.join(dir, "asignacion_" + str(idAsignacion) + "_firmado.pdf"))
    flash("Se subio la firma correctamente")
    return redirect("/asignacion/listar_pdf/" + str(idAsignacion))

@asignacion.route("/devolucion/adjuntar_pdf/<idAsignacion>", methods=["POST"])
@administrador_requerido
def adjuntar_pdf_devolucion(idAsignacion):
    #TODO: revisar que sea pdf
    #si existe eliminar
    dir = 'pdf'
    filenameToDelete = "devolucion_" + str(idAsignacion) + "_firmado.pdf"
    if os.path.exists(os.path.join(dir, filenameToDelete)):
        os.remove(os.path.join(dir, filenameToDelete))
    file = request.files["file"]
    #subir archivo
    #renombrar archivo
    filename = file.filename
    sfilename = secure_filename(filename)
    file.save(os.path.join(
        dir, secure_filename(sfilename)
    ))
    os.rename(os.path.join(dir, sfilename), 
              os.path.join(dir, "devolucion_" + str(idAsignacion) + 
                           "_firmado.pdf"))
    return redirect("/asignacion/listar_pdf/" + str(idAsignacion) + 
                    "/devolver")
#/asignacion/listar_pdf/<idAsignacion>/<devolver>

#junji
#Tijunji2017
#def enviar_asignacion(Asignacion):
    #asunto = 'Nueva Asignacion'
    #cuerpo = """
    #<html>
        #<body>
        #<p>pretender que este correo se envia a </p>
        #<table>
            #<thead>
                #<tr>
                    #<th>N°</th>
                    #<th>Tipo Equipo</th>
                    #<th>Marca</th>
                    #<th>Modelo</th>
                    #<th>N° Serie</th>
                    #<th>N° Inventario</th>
                #</tr>
            #</thead>
            #<tbody>
                #<tr>
                    #<td>{}</td>
                    #<td>{}</td>
                    #<td>{}</td>
                    #<td>{}</td>
                    #<td>{}</td>
                    #<td>{}</td>
                    #<td>{}</td>
                #</tr>
            #</tbody>
        #</table>
        #</body>
    #</html>
    #""".format(1, Asignacion[''])
    #enviar_correo(asunto, 'correo', cuerpo, 'filename')
    #pass


######## Echar ojo a esto ###########
def enviar_correo(filename, correo):
    #correo = "cacastilloc@junji.cl"
    print("enviar_correo")
    remitente = 'martin.castro@junji.cl'
    destinatario = 'martin.castro@junji.cl'
    asunto = 'Se le han asignado los siguientes equipos'
    cuerpo = """

            """.format(correo)
    username = 'martin.castro@junji.cl'
    password = 'junji.2024'

    mensaje = MIMEMultipart()

    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    with open(filename, "rb") as pdf_file:
        pdf = MIMEApplication(pdf_file.read(), _subtype='pdf')
    pdf.add_header('Content-Disposition', 'attachment', filename=filename)
    mensaje.attach(pdf)

    mensaje.attach(MIMEText(cuerpo, 'plain'))

    texto = mensaje.as_string()
    server_smtp1 = 'smtp.office365.com'
    server_smtp2 = 'smtp-mail.outlook.com'
    server = smtplib.SMTP('smtp.office365.com', port=587)
    server.starttls()
    server.login(username, password)
    server.sendmail(remitente, destinatario, texto)
    server.quit()

#def enviar_correo(asunto, correo, cuerpo, filename):
    ##correo = "cacastilloc@junji.cl"
    #print("enviar_correo")
    #remitente = 'martin.castro@junji.cl'
    #destinatario = 'mauricio.cardenas@junji.cl'
    #username = 'martin.castro@junji.cl'
    #password = 'junji.2024'

    #mensaje = MIMEMultipart()

    #mensaje['From'] = remitente
    #mensaje['To'] = destinatario
    #mensaje['Subject'] = asunto

    #mensaje.attach(MIMEText(cuerpo, 'html'))

    #texto = mensaje.as_string()
    #server_smtp1 = 'smtp.office365.com'
    #server_smtp2 = 'smtp-mail.outlook.com'
    #server = smtplib.SMTP('smtp.office365.com', port=587)
    #server.starttls()
    #server.login(username, password)
    ##print("before send mail")
    ##print(destinatario + "__")
    #server.sendmail(remitente, destinatario, texto)
    ##print("after send mail")
    #server.quit()