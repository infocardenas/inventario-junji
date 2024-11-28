from flask import Flask, render_template
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Obtener los datos (ejemplo)
total_funcionarios = 100
total_equipos = 200

# Crear el gráfico
labels = ['Funcionarios', 'Equipos']
sizes = [total_funcionarios, total_equipos]
colors = ['blue', 'orange']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

# Convertir el gráfico a imagen y almacenar en un buffer
img_buffer = io.BytesIO()
plt.savefig(img_buffer, format='png')
img_buffer.seek(0)
img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

# Renderizar la plantilla HTML con el gráfico incrustado
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', img_base64=img_base64)

if __name__ == '__main__':
    app.run(debug=True)
