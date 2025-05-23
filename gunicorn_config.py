# ~/inventario-junji/gunicorn_config.py
import os

bind = "0.0.0.0:4443"
workers = 2 # Aquí definimos los workers

certfile = "/etc/ssl/junji_bastian.rama/server_bast_cert.pem"
keyfile = "/etc/ssl/junji_bastian.rama/server_bast_key.pem"

chdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "Flask"))
# chdir = "./Flask" # Podrías usar esta también si corres desde ~/inventario-junji/

wsgi_app = "app.wsgi:app"