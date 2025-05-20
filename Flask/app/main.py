# Flask/app/main.py
import os
from . import create_app # Importa la función factory desde __init__.py

app = create_app() # Crea la instancia de la aplicación

if __name__ == "__main__":
    # Tu lógica para app.run() con HTTPS para desarrollo local
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Asume que dev_cert.pem y dev_key.pem están en Flask/ (un nivel arriba de app/)
    cert_file_abs = os.path.abspath(os.path.join(script_dir, '../dev_cert.pem'))
    key_file_abs = os.path.abspath(os.path.join(script_dir, '../dev_key.pem'))
    local_dev_port = 8080
    http_port = 3000
    try:
        print(f"Intentando iniciar servidor de desarrollo local en HTTPS en https://localhost:{local_dev_port}")
        app.run(host='0.0.0.0', port=local_dev_port, debug=True, ssl_context=(cert_file_abs, key_file_abs))
    except FileNotFoundError:
        print("ADVERTENCIA: Certificados de desarrollo no encontrados...") # Mensaje abreviado
        app.run(host='0.0.0.0', port=http_port, debug=True)
    except OSError as e:
        print(f"ERROR al iniciar servidor: {e}") # Mensaje abreviado
        app.run(host='0.0.0.0', port=http_port, debug=True)