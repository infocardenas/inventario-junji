# Flask/app/__init__.py
from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os

# Importa tus variables de 'cuentas' y 'funciones' si son necesarias para la configuración global
# o para las extensiones. Asegúrate de que estas importaciones sean relativas.
from .env_vars import cuentas # Asumiendo que env_vars.py está en Flask/app/
                              # y define la variable 'cuentas'
                              # Si env_vars.py está en Flask/, sería from ..env_vars import cuentas

# Crea instancias de las extensiones SIN inicializarlas con la app todavía
mysql = MySQL()
bcrypt = Bcrypt()

def create_app():
    """Función factory para crear la instancia de la aplicación Flask."""
    app_instance = Flask(__name__)

    # --- Configuración Centralizada de la App ---
    app_instance.secret_key = "mysecretkey"

   # Configuramos la conexión a la base de datos
    app_instance.config['MYSQL_USER'] = os.getenv('MYSQL_USER') or cuentas['nombre_usuario']
    app_instance.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD') or cuentas['contrasenna']
    app_instance.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST') or 'localhost'  # localhost
    app_instance.config['MYSQL_DB'] = os.getenv('MYSQL_DB') or 'inventariofinal'
    app_instance.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app_instance.config['MYSQL_DATABASE_DEBUG'] = True  # Habilitar depuración para ver más detalles

    # Inicializar extensiones CON la app_instance configurada
    mysql.init_app(app_instance)
    bcrypt.init_app(app_instance)
    # -----------------------------------------

    # --- Registrar Blueprints ---
    # Usar importaciones relativas para tus blueprints
    # from .main import main_routes # Necesitarás definir main_routes como un Blueprint en main.py
    from .proveedor import proveedor
    from .tipo_adquisicion import tipo_adquisicion
    from .orden_compra import orden_compra
    from .provincia import provincias
    from .comuna import comuna
    from .tipo_equipo import tipo_equipo
    from .Unidad import Unidad
    from .marca_equipo import marca_equipo
    from .modelo_equipo import modelo_equipo
    from .estado_equipo import estado_equipo
    from .funcionario import funcionario
    from .equipo import equipo
    from .devolucion import devolucion
    from .asignacion import asignacion
    from .traslado import traslado
    from .incidencia import incidencia
    from .buscar import buscar
    from .utils import utils
    from .cuentas import cuentas as cuentas_blueprint # El blueprint de cuentas

    # Registra tus blueprints
    # app_instance.register_blueprint(main_routes) # Si main.py define un blueprint
    app_instance.register_blueprint(proveedor)
    app_instance.register_blueprint(tipo_adquisicion)
    app_instance.register_blueprint(orden_compra)
    app_instance.register_blueprint(provincias)
    app_instance.register_blueprint(comuna)
    app_instance.register_blueprint(tipo_equipo)
    app_instance.register_blueprint(Unidad)
    app_instance.register_blueprint(marca_equipo)
    app_instance.register_blueprint(modelo_equipo)
    app_instance.register_blueprint(estado_equipo)
    app_instance.register_blueprint(funcionario)
    app_instance.register_blueprint(equipo)
    app_instance.register_blueprint(devolucion)
    app_instance.register_blueprint(asignacion)
    app_instance.register_blueprint(traslado)
    app_instance.register_blueprint(incidencia)
    app_instance.register_blueprint(buscar)
    app_instance.register_blueprint(utils)
    app_instance.register_blueprint(cuentas_blueprint) # Usando el alias para el blueprint
    # -----------------------------------

    return app_instance