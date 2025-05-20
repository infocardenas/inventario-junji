# Flask/app/wsgi.py
from . import create_app # Importa la función factory desde __init__.py

app = create_app() # Crea la instancia de la aplicación para Gunicorn

# Si Gunicorn necesita explícitamente un objeto llamado 'application', puedes añadir:
# application = app
# Pero vamos a probar primero con 'app' y Gunicorn apuntando a app.wsgi:app