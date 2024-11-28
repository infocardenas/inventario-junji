from flask import Blueprint, request, flash, render_template, redirect, url_for, g, session
from db import mysql
from cuentas import loguear_requerido, administrador_requerido

utils = Blueprint('utils', __name__, template_folder= 'app/templates')
@utils.route('/')
@utils.route('/dashboard')
@loguear_requerido
def dashboard():
    print(session)
    return render_template('dashboard.html', privilegio=session['privilegio'])

