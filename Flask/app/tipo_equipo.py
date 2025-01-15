from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido
from cerberus import Validator

tipo_equipo = Blueprint("tipo_equipo", __name__, template_folder="app/templates")


# Definir el esquema de validación para tipo_equipo
tipo_equipo_schema = {
    'nombreTipo_Equipo': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 100,
        'regex': '^[a-zA-Z0-9]*$'  # Permitir solo letras, números y espacios
    }
}

# ruta para enviar los datos y visualizar la pagina principal para tipo de equipo
@tipo_equipo.route("/tipo_equipo")
@tipo_equipo.route("/tipo_equipo/<page>")
@loguear_requerido
def tipoEquipo(page=1):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    perpage = getPerPage()
    offset = (int(page) - 1) * perpage
    cur = mysql.connection.cursor()
    total = 0
    cur.execute("SELECT COUNT(*) FROM tipo_equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])
    # Se pediran todos las filas de tipo_equipo. Luego se pediran todas las filas de las
    # marcas asociadas con el tipo de equipo. Luego estas marcas se van a añadir a la
    # tupla del tipo de equipo de manera que se tenga marca_i=(tupla,) donde i = 0 y ++ cada iteracion
    cur.execute("""
        SELECT *
        FROM tipo_equipo te
        LIMIT %s OFFSET %s 
                """,(perpage, offset)
    )
    tipo_equipo_data = cur.fetchall()
    tipo_equipo_con_marcas = None
    # input 1 ({})
    # input 2 ({})
    # input1[i] = {}
    # marcas tiene que ser una tupla de diccionarios

    for i in range(0, len(tipo_equipo_data)):
        print("tipo con marcas")
        print(tipo_equipo_con_marcas)
        cur.execute("""
        SELECT *
        FROM marca_equipo me
        INNER JOIN marca_tipo_equipo mte ON me.idMarca_Equipo = mte.idMarca_Equipo
        INNER JOIN tipo_equipo te ON mte.idTipo_equipo = te.idTipo_equipo
        WHERE te.idTipo_equipo = %s
        """,
            (tipo_equipo_data[i]["idTipo_equipo"],),
        )
        marcas_del_tipo = cur.fetchall()
        print("marcas_del_tipo")
        print(marcas_del_tipo)
        if tipo_equipo_con_marcas == None:
            newdict = tipo_equipo_data[i]
            newdict.update({"marcas": marcas_del_tipo})
            tipo_equipo_con_marcas = (newdict,)
        else:
            newdict = tipo_equipo_data[i]
            newdict.update({"marcas": marcas_del_tipo})
            print("newdict")
            print(newdict)
            print(tipo_equipo_con_marcas)
            tipo_equipo_con_marcas += (newdict,)
            print(tipo_equipo_con_marcas)

    # print("tipo_equipo_con_marcas")
    # print(tipo_equipo_con_marcas)
    cur.execute("SELECT * FROM marca_equipo")
    marcas = cur.fetchall()
    page = int(page)
    return render_template(
        "tipo_equipo.html",
        tipo_equipo=tipo_equipo_data,
        marcas=marcas,
        page=page,
        lastpage=page < (total / perpage) + 1,
    )


# agrega un tipo de equipo
@tipo_equipo.route("/crear_tipo_equipo", methods=["POST"])
@administrador_requerido
def crear_tipo_equipo():
        
        data = {
            'nombreTipo_Equipo': request.form['nombreTipo_equipo']
        }
 # Validar los datos usando Cerberus
        v = Validator(tipo_equipo_schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for("tipo_equipo.tipoEquipo"))
            
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                        INSERT INTO tipo_equipo (nombreTipo_equipo) 
                        VALUES (%s)""",
                (data["nombreTipo_Equipo"],),
            )
        except Exception as e:
                #flash(e.args[1])
                flash("Error al crear")
                return redirect(url_for("tipo_equipo.tipoEquipo"))
        mysql.connection.commit()
        cur.execute(
            """
        SELECT *
        FROM tipo_equipo
        WHERE tipo_equipo.idTipo_equipo = %s
                    """,
            (cur.lastrowid,),
        )
        tipo_equipo = cur.fetchone()
        cur.execute(
            """
                SELECT *
                FROM marca_equipo
                    """
        )
        marcas = cur.fetchall()
        return render_template(
            "enlazar_marcas.html", tipo_equipo=tipo_equipo, marcas=marcas
        )


@tipo_equipo.route("/add_tipo_equipo/<idTipo_equipo>", methods=["POST"])
@administrador_requerido
def add_tipo_equipo(idTipo_equipo):
    print("idTipo_equipo:", idTipo_equipo)

    if request.method == "POST":
        try:
            # Obtener los datos del formulario
            marcas = request.form.getlist("marcas[]")
            observacion = request.form["observacion"]

            # Actualizar tipo_equipo
            cur = mysql.connection.cursor()
            cur.execute(
                """
                UPDATE tipo_equipo 
                SET observacionTipoEquipo = %s
                WHERE tipo_equipo.idTipo_equipo = %s
                """,
                (observacion, idTipo_equipo),
            )
            mysql.connection.commit()

            # Insertar marcas en marca_tipo_equipo
            for marca in marcas:
                print("Agregar marca:", marca)
                cur.execute(
                    """
                    INSERT INTO marca_tipo_equipo (idMarca_Equipo, idTipo_equipo)
                    VALUES (%s, %s)
                    """,
                    (marca, idTipo_equipo),
                )
            mysql.connection.commit()

            flash("Tipo de equipo agregado correctamente")
            return redirect(url_for("tipo_equipo.tipoEquipo"))

        except Exception as e:
            # Capturar y mostrar el error específico
            print("Error:", e)
            flash(f"Error al agregar tipo de equipo: {str(e)}")
            return redirect(url_for("tipo_equipo.tipoEquipo"))



# enviar datos a formulario editar para tipo de equipo segun el ide correspondiente
@tipo_equipo.route("/edit_tipo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_tipo_equipo(id):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            SELECT *
            FROM tipo_equipo te
            INNER JOIN marca_tipo_equipo mte ON mte.idTipo_equipo = te.idTipo_equipo
            INNER JOIN marca_equipo me ON me.idMarca_Equipo = mte.idMarca_Equipo
            WHERE te.idTipo_Equipo = %s
                    """,
            (id,),
        )
        data = cur.fetchall()
        cur.execute("SELECT * FROM marca_equipo")
        marca_data = cur.fetchall()
        cur.execute(
            """
        SELECT *
        FROM marca_equipo me
        LEFT JOIN marca_tipo_equipo mte ON mte.idMarca_Equipo = me.idMarca_Equipo
        """
        )
        marcas = cur.fetchall()
        ultima_marca_aceptada = ""
        marca_anterior = ""
        #En principio deberia ser mas rapido usar una lista y luego trasformarlo a tupla
        marcasModificadas = []
        print("revision marcas " + str(id))
        #no lo añadas a menos que sea 
        marcas_aceptadas = {}
        for i in range(0, len(marcas)):
            marca = marcas[i]
            #print("marca")
            #print(marca)
            #print("ultima marca aceptada")
            #print(ultima_marca_aceptada)
            if marca['nombreMarcaEquipo'] != ultima_marca_aceptada and (str(marca['idTipo_equipo']) == id or marca['idTipo_equipo'] == None):
                #print("aceptada")
                ultima_marca_aceptada = marca['nombreMarcaEquipo']
                marcasModificadas.append(marca)
                #los diccionario son igual a falso para que al encontrar un valor este retorne falso y se rechaze ya que ya existe esa marca
                marcas_aceptadas[ultima_marca_aceptada] = True
            else:
                if i != len(marcas)-1:
                    #print(not marcas_aceptadas.get(marca['nombreMarcaEquipo']))
                    #print(marcas[i+1]['nombreMarcaEquipo'] != marca['nombreMarcaEquipo'])
                    if ((not marcas_aceptadas.get(marca['nombreMarcaEquipo'])) and marcas[i+1]['nombreMarcaEquipo'] != marca['nombreMarcaEquipo']):
                        #print("test")
                        marcasModificadas.append(marca)
                        ultima_marca_aceptada = marca['nombreMarcaEquipo']
                        marcas_aceptadas[ultima_marca_aceptada] = True
                        #print("accepted")
                elif not marcas_aceptadas.get(marca['nombreMarcaEquipo']):
                    marcasModificadas.append(marca)

        marcasModificadas = tuple(marcasModificadas)
        #cur.execute("""
        #SELECT * 
        #FROM marca_equipo
        #""")
        #marca_equipo = cur.fetchall()

        #print("test1")
        #print("Marcas Modificadas")
        #print(marcasModificadas)
        #print("test2")
        #print("Marcas Sin Modificadas")
        #print(marca_equipo)
        return render_template(
            "editTipo_equipo.html",
            tipo_equipo=data[0],
            marcas=marcasModificadas,
        )
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for("tipo_equipo.tipoEquipo"))

#Funcion que pide las marcas y 
#def getMarcas():
    #pass
# actualiza un elemento de tipo de equipo segun el id correspondiente
@tipo_equipo.route("/update_tipo_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_tipo_equipo(id):
    print("update tipo equipo")
    if request.method == "POST":
        data = {
            'nombreTipo_Equipo': request.form['nombreTipo_equipo']
        }
        ids_marca = request.form.getlist("marcas[]")
        print("ids_marca")
        print(ids_marca)

         # Validar los datos usando Cerberus
        v = Validator(tipo_equipo_schema)
        if not v.validate(data):
            flash("Caracteres no permitidos")
            return redirect(url_for("tipo_equipo.tipoEquipo"))

        cur = mysql.connection.cursor()
        cur.execute(
            """
        SELECT * 
        FROM tipo_equipo 
        WHERE idTipo_equipo = %s
                    """,
            (id,),
        )
        tipo_equipo = cur.fetchone()
        cur.execute(
            """ 
        UPDATE tipo_equipo
        SET nombreTipo_equipo = %s
        WHERE idTipo_equipo = %s
        """,
            (data["nombreTipo_Equipo"], id),
        )
        #editar la relacion entre tipo y marcas
        cur.execute("""
        DELETE FROM marca_tipo_equipo
        WHERE idTipo_equipo = %s
        """, (id,))
        
        for id_marca in ids_marca:
            cur.execute("""
            INSERT INTO marca_tipo_equipo
            (idTipo_equipo, idMarca_Equipo)
            VALUES (%s, %s)
            """, (id,id_marca))
        mysql.connection.commit()
        return redirect(url_for("tipo_equipo.tipoEquipo"))



# elimina el registro segun el id
@tipo_equipo.route("/delete_tipo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_tipo_equipo(id):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            DELETE
            FROM marca_tipo_equipo
            WHERE marca_tipo_equipo.idTipo_equipo = %s
                    """,
            (id,),
        )
        cur.execute("DELETE FROM tipo_equipo WHERE idTipo_equipo = %s", (id,))
        mysql.connection.commit()
        flash("Tipo de equipo eliminado correctamente")
        return redirect(url_for("tipo_equipo.tipoEquipo"))
    except Exception as e:
        #flash(e.args[1])
        flash("Error al crear")
        return redirect(url_for("tipo_equipo.tipoEquipo"))
