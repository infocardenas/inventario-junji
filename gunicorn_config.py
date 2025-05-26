# ~/inventario-junji/gunicorn_config.py
import os

bind = "0.0.0.0:4443"
workers = 2 # Aquí definimos los workers

certfile = "/etc/ssl/junji_bastian.rama/server_bast_cert.pem"
keyfile = "/etc/ssl/junji_bastian.rama/server_bast_key.pem"

chdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "Flask"))
# chdir = "./Flask" # Podrías usar esta también si corres desde ~/inventario-junji/

wsgi_app = "app.wsgi:app"

# --- Configuración de Logging ---
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Opciones para loglevel: 'debug', 'info', 'warning', 'error', 'critical'
# 'info' mostrará inicios de workers, advertencias SSL, y errores de aplicación.
# 'error' ocultará las advertencias SSL pero también los mensajes informativos de Gunicorn.
loglevel = 'error' 

# Formato detallado para el log de acceso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" ProcessTime:%(L)s PID:%(p)s'