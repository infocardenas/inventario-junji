from flask import Blueprint, render_template, session
from cuentas import loguear_requerido

utils = Blueprint('utils', __name__, template_folder= 'app/templates')
@utils.route('/')
@utils.route('/dashboard')
@loguear_requerido
def dashboard():
    print(session)
    return render_template('dashboard.html', privilegio=session['privilegio'])

