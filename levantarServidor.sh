#!/bin/bash
# ...
CONFIG_FILE="/home/junji/inventario-junji/gunicorn_config.py"
GUNICORN_EXEC="/home/junji/inventario-junji/Flask/venv_https_test/bin/gunicorn"

echo "Iniciando Gunicorn para el inventario..."
sudo "$GUNICORN_EXEC" -c "$CONFIG_FILE" 