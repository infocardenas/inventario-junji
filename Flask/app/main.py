from app import app
# Se importan las variables blueprint en las vistas correspondientes para que puedan ser iniciadas a traves de main
from proveedor import proveedor
from tipo_adquisicion import tipo_adquisicion
from orden_compra import orden_compra
from provincia import provincias
from comuna import comuna
from tipo_equipo import tipo_equipo
from Unidad import Unidad
from marca_equipo import marca_equipo
from modelo_equipo import modelo_equipo
from estado_equipo import estado_equipo
from funcionario import funcionario
from equipo import equipo
from devolucion import devolucion
from asignacion import asignacion
from traslado import traslado
from incidencia import incidencia
from buscar import buscar
from utils import utils
from cuentas import cuentas

app.register_blueprint(devolucion)
app.register_blueprint(proveedor)
app.register_blueprint(tipo_adquisicion)
app.register_blueprint(provincias)
app.register_blueprint(orden_compra)
app.register_blueprint(comuna)
app.register_blueprint(tipo_equipo)
app.register_blueprint(Unidad)
app.register_blueprint(marca_equipo)
app.register_blueprint(modelo_equipo)
app.register_blueprint(estado_equipo)
app.register_blueprint(funcionario)
app.register_blueprint(equipo)
app.register_blueprint(asignacion)
app.register_blueprint(traslado)
app.register_blueprint(incidencia)
app.register_blueprint(buscar)
app.register_blueprint(utils)
app.register_blueprint(cuentas)

import os

if __name__ == "__main__":
    # Rutas relativas (para referencia)
    # cert_file_relative = '../dev_cert.pem'
    # key_file_relative = '../dev_key.pem'

    # Reconstruyamos las rutas absolutas aquí para asegurar que usamos las mismas que en la depuración
    script_dir_for_abs = os.path.dirname(os.path.abspath(__file__))
    abs_cert_path_for_run = os.path.abspath(os.path.join(script_dir_for_abs, '../dev_cert.pem'))
    abs_key_path_for_run = os.path.abspath(os.path.join(script_dir_for_abs, '../dev_key.pem'))


    local_dev_port = 8080
    http_port = 3000

    try:
        print(f"Intentando iniciar servidor de desarrollo local en HTTPS en https://localhost:{local_dev_port}")
        # Usar las rutas absolutas aquí:
        app.run(host='0.0.0.0', port=local_dev_port, debug=True, ssl_context=(abs_cert_path_for_run, abs_key_path_for_run))
    except FileNotFoundError:
        print("*********************************************************************")
        print(f"ADVERTENCIA: Certificados de desarrollo (rutas absolutas) no encontrados.")
        print(f"  Ruta intentada para certificado: {abs_cert_path_for_run}")
        print(f"  Ruta intentada para clave: {abs_key_path_for_run}")
        print(f"Ejecutando servidor de desarrollo local en HTTP en http://localhost:{http_port}.")
    except OSError as e:
        if "Errno 98" in str(e) or "Errno 48" in str(e) or "WinError 10048" in str(e): # Address already in use
             print(f"ERROR: El puerto {local_dev_port} o {http_port} ya está en uso.")
        elif "Errno 13" in str(e) or "WinError 10013" in str(e): # Permission denied
             print(f"ERROR: Permiso denegado para usar el puerto. Para puertos < 1024 se necesita admin. Prueba un puerto > 1024.")
        else:
            print(f"ERROR al iniciar el servidor de desarrollo: {e}")
        print(f"Si el error persiste, intenta ejecutar en HTTP en el puerto {http_port}.")
        if not (("Errno 98" in str(e) or "Errno 48" in str(e) or "WinError 10048" in str(e)) and local_dev_port == http_port):
            try:
                app.run(host='0.0.0.0', port=http_port, debug=True)
            except Exception as final_e:
                print(f"No se pudo iniciar el servidor HTTP de respaldo: {final_e}")
