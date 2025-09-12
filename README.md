# Sistema de Gestión de Inventario - JUNJI

Este proyecto es una aplicación web desarrollada para la gestión y seguimiento del inventario de la Junta Nacional de Jardines Infantiles (JUNJI). Permite realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre los activos, optimizando el control de stock en tiempo real.

El sistema está construido siguiendo las mejores prácticas de desarrollo, desacoplando la configuración del código fuente para mayor seguridad y portabilidad.

---

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.12 con el micro-framework [Flask](https://flask.palletsprojects.com/).
* **Base de Datos:** MySQL (se recomienda versión 8.0 o superior).
* **Gestión de Dependencias:** Pip con `requirements.txt`.
* **Configuración de Entorno:** Archivo `.env`.

---

## 🚀 Guía de Instalación y Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

### 1. Prerrequisitos

Asegúrate de tener instalado el siguiente software:

* [Python](https://www.python.org/downloads/) (versión 3.12 o compatible)
* [Git](https://git-scm.com/) (para clonar el repositorio)
* [MySQL Server](https://dev.mysql.com/downloads/mysql/)
* [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) (Recomendado para la gestión visual de la base de datos)

### 2. Clonar el Repositorio

Abre tu terminal, navega a la carpeta donde deseas guardar el proyecto y clónalo:

```bash
git clone https://github.com/infocardenas/inventario-junji.git
cd inventario-junji
````

### 3\. Configurar el Entorno Virtual y las Dependencias

Es fundamental utilizar un entorno virtual para aislar las librerías de este proyecto y evitar conflictos con otros.

```bash
# 1. Crear el entorno virtual (se creará una carpeta "venv")
python -m venv venv

# 2. Activar el entorno virtual
# En Windows (CMD/PowerShell):
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 3. Instalar todas las dependencias necesarias
pip install -r requirements.txt
```

> **Nota:** Si realizas cambios o instalas una nueva librería, recuerda actualizar el archivo `requirements.txt` con el comando `pip freeze > requirements.txt`.

### 4\. Configurar la Conexión a la Base de Datos

La aplicación se conecta a la base de datos utilizando credenciales que se cargan de forma segura desde un archivo `.env`.

1.  **Crear el archivo de entorno:**
    Crea una copia del archivo de ejemplo `.env.example` y renómbrala a `.env`. Este archivo `.env` será ignorado por Git para proteger tus credenciales.

    ```bash
    # En Windows (si usas cmd):
    copy .env.example .env
    # En macOS/Linux:
    cp .env.example .env
    ```

2.  **Editar las variables de entorno:**
    Abre el nuevo archivo `.env` con un editor de texto y rellena los valores correspondientes a tu configuración local de MySQL.

    ```ini
    # Credenciales para la conexión a la base de datos MySQL
    DB_HOST=localhost
    DB_USER=tu_usuario_mysql
    DB_PASSWORD=tu_contraseña_secreta
    DB_NAME=inventariofinal

    # Configuración de Flask
    FLASK_ENV=development # Usa 'production' en el servidor real
    ```

### 5\. Preparar la Base de Datos

1.  **Crear la base de datos:**
    Asegúrate de que la base de datos `inventariofinal` exista en tu servidor MySQL. Puedes crearla desde MySQL Workbench o con el siguiente comando:

    ```bash
    mysql -u tu_usuario_mysql -p -e "CREATE DATABASE IF NOT EXISTS inventariofinal;"
    ```

2.  **Importar datos (Opcional):**
    Si tienes un archivo de respaldo (`.sql`) y necesitas cargar datos de prueba, puedes importarlo así:

    ```bash
    mysql -u tu_usuario_mysql -p inventariofinal < /ruta/hacia/tu/backup.sql
    ```

### 6\. ¡Ejecutar la Aplicación\!

Con tu entorno virtual activado y el archivo `.env` configurado, navega al directorio de la aplicación y ejecuta el script principal:

```bash
# 1. Entrar en el directorio de la aplicación
cd Flask/app

# 2. Ejecutar el servidor de desarrollo
python main.py
```

-----

## 📂 Estructura del Proyecto (Lo escencial)

```
.
├── Flask/
│   └── app/              # Módulo principal de la aplicación Flask
│       ├── __init__.py   # Inicializa la app y carga las variables de entorno
│       ├── main.py       # Punto de entrada para ejecutar la aplicación
│       ├── db.py         # Lógica de conexión a la base de datos
│       ├── routes.py     # Define las rutas/endpoints de la aplicación
│       ├── models.py     # Define los modelos de datos (si aplica)
│       ├── static/       # Archivos estáticos (CSS, JS, imágenes)
│       └── templates/    # Plantillas HTML (con Jinja2)
├── venv/                 # Carpeta del entorno virtual (ignorada por Git)
├── .env                  # Archivo de configuración local (ignorado por Git)
├── .env.example          # Archivo de ejemplo para la configuración
├── .gitignore            # Archivos y carpetas ignorados por Git
├── requirements.txt      # Lista de dependencias de Python
└── README.md             # Esta documentación
```

-----

## 📚 Documentación Adicional

Para una visión más profunda de la arquitectura, decisiones de diseño y diagramas del sistema, por favor consulta la **[Wiki del Proyecto](https://deepwiki.com/infocardenas/inventario-junji)**.
