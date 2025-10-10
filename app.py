from flask import Flask, render_template, request, redirect, url_for, jsonify
from db.connection import get_db_connection
from datetime import datetime  # ✅ AGREGAR ESTA IMPORTACIÓN
import os

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

# Configuración de la base de datos
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'db', 'cuyes.db')

# Ahora sí puedes usar @app.route
@app.route('/')
def index():
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    return render_template('dashboard.html', fecha_actual=fecha_actual)

@app.route('/partos')
def partos():
    # Obtener galpones para el dropdown
    from models.galpon import Galpon
    galpon_model = Galpon()
    galpones = galpon_model.obtener_todos()
    
    return render_template('partos.html', galpones=galpones)

@app.route('/destetes')
def destetes():
    return render_template('destetes.html')

@app.route('/ventas')
def ventas():
    return render_template('ventas.html')

@app.route('/galpones')
def galpones():
    from models.galpon import Galpon
    galpon_model = Galpon()
    galpones = galpon_model.obtener_todos()
    return render_template('galpones.html', galpones=galpones)

# API para cargar pozas según galpón
@app.route('/api/galpones/<int:galpon_id>/pozas')
def api_pozas_por_galpon(galpon_id):
    from models.poza import Poza
    poza_model = Poza()
    pozas = poza_model.obtener_por_galpon(galpon_id)
    
    pozas_data = []
    for poza in pozas:
        pozas_data.append({
            'id': poza[0],
            'nombre': poza[1]
        })
    
    return jsonify(pozas_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)