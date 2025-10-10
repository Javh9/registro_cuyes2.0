from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from db.connection import get_db_connection
from datetime import datetime
import os

# ✅ PRIMERO definir app
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'db', 'cuyes.db')

# ✅ LUEGO las rutas existentes
@app.route('/')
def index():
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    return render_template('dashboard.html', fecha_actual=fecha_actual)

@app.route('/partos')
def partos():
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

# ✅ AHORA SÍ agregar las NUEVAS rutas API
@app.route('/api/galpones/<int:galpon_id>/pozas')
def api_pozas_por_galpon(galpon_id):
    try:
        from models.poza import Poza
        poza_model = Poza()
        pozas = poza_model.obtener_por_galpon(galpon_id)
        
        # DEBUG: Mostrar en consola qué está pasando
        print(f"🔍 DEBUG API Pozas:")
        print(f"   Galpón ID: {galpon_id}")
        print(f"   Pozas encontradas: {pozas}")
        print(f"   Tipo de datos: {type(pozas)}")
        
        pozas_data = []
        for poza in pozas:
            print(f"   Procesando poza: {poza}")  # DEBUG
            pozas_data.append({
                'id': poza[0],
                'nombre': poza[1]
            })
        
        print(f"   JSON a enviar: {pozas_data}")  # DEBUG
        return jsonify(pozas_data)
        
    except Exception as e:
        print(f"❌ Error API pozas: {e}")
        return jsonify([])
@app.route('/api/pozas/<int:poza_id>/sugerir_parto')
def api_sugerir_parto(poza_id):
    try:
        from models.parto import Parto
        parto_model = Parto()
        ultimo_parto = parto_model.obtener_ultimo_parto(poza_id)
        siguiente_parto = ultimo_parto + 1 if ultimo_parto else 1
        return jsonify({'siguiente_parto': siguiente_parto})
    except Exception as e:
        print(f"Error API sugerir parto: {e}")
        return jsonify({'siguiente_parto': 1})

@app.route('/registrar_parto', methods=['POST'])
def registrar_parto():
    try:
        from models.parto import Parto
        parto_model = Parto()
        
        datos = {
            'galpon_id': request.form['galpon_id'],
            'poza_id': request.form['poza_id'],
            'fecha_parto': datetime.now().date(),
            'nacidos_vivos': int(request.form['nacidos_vivos']),
            'muertos_nacimiento': int(request.form['muertos_nacimiento']),
            'numero_parto': int(request.form['numero_parto']),
            'observaciones': request.form.get('observaciones', '')
        }
        
        parto_id = parto_model.registrar(datos)
        if parto_id:
            flash('Parto registrado exitosamente!', 'success')
            return redirect(url_for('partos'))
        else:
            flash('Error al registrar el parto', 'error')
            return redirect(url_for('partos'))
            
    except Exception as e:
        print(f"Error registrando parto: {e}")
        flash('Error al registrar el parto', 'error')
        return redirect(url_for('partos'))

@app.route('/crear_galpon', methods=['POST'])
def crear_galpon():
    try:
        from models.galpon import Galpon
        galpon_model = Galpon()
        
        datos = {
            'nombre': request.form['nombre'],
            'capacidad': int(request.form['capacidad']),
            'ubicacion': request.form['ubicacion'],
            'estado': 'activo'
        }
        
        galpon_id = galpon_model.crear(datos)
        if galpon_id:
            flash('Galpón creado exitosamente!', 'success')
            return redirect(url_for('galpones'))
        else:
            flash('Error al crear el galpón', 'error')
            return redirect(url_for('galpones'))
            
    except Exception as e:
        print(f"Error creando galpón: {e}")
        flash('Error al crear el galpón', 'error')
        return redirect(url_for('galpones'))

@app.route('/crear_poza', methods=['POST'])
def crear_poza():
    try:
        from models.poza import Poza
        poza_model = Poza()
        
        datos = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'capacidad': int(request.form['capacidad']),
            'galpon_id': int(request.form['galpon_id']),
            'estado': 'activo'
        }
        
        poza_id = poza_model.crear(datos)
        if poza_id:
            flash('Poza creada exitosamente!', 'success')
        else:
            flash('Error al crear la poza', 'error')
            
        return redirect(url_for('galpones'))
            
    except Exception as e:
        print(f"Error creando poza: {e}")
        flash('Error al crear la poza', 'error')
        return redirect(url_for('galpones'))
# ✅ FINALMENTE el if __name__
if __name__ == '__main__':
    app.run(debug=True, port=5000)