from flask import (
    request,
    flash,
    render_template,
    url_for,
    redirect,
    Blueprint,
    session,
    send_file,
)
from db import mysql
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill
from werkzeug.utils import secure_filename
from cuentas import loguear_requerido, administrador_requerido
from MySQLdb import IntegrityError
import os
import time



equipo = Blueprint("equipo", __name__, template_folder="app/templates")