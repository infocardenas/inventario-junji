from flask import Flask

# crea una instancia de la aplicación Flask, utilizando el nombre del módulo actual para configurar la aplicación correctamente.
app = Flask(__name__)

# Habilitar debug mode
if __name__ == "__main__":
    app.run(debug=True)
    
# protege las cookies y datos de sesion del usuario
app.secret_key = "mysecretkey"