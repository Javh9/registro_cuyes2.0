from flask import Blueprint, request, jsonify, render_template
from models.parto import Parto
from models.animal import Animal

bp = Blueprint('parto', __name__)

@bp.route('/')
def listar_partos():
    parto_model = Parto()
    partos = parto_model.obtener_todos()
    return render_template('partos.html', partos=partos)

@bp.route('/crear', methods=['POST'])
def crear_parto():
    try:
        data = request.form
        parto_model = Parto()
        parto_id = parto_model.registrar(data)
        
        if parto_id:
            return jsonify({'success': True, 'id': parto_id})
        else:
            return jsonify({'success': False, 'error': 'Error registrando parto'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/hembras-reproductoras')
def obtener_hembras_reproductoras():
    try:
        animal_model = Animal()
        hembras = animal_model.obtener_por_etapa('reproductor')
        # Filtrar solo hembras
        hembras_reproductoras = [h for h in hembras if h[2] == 'hembra']  # sexo en índice 2
        return jsonify([dict(hembra) for hembra in hembras_reproductoras])
    except Exception as e:
        return jsonify({'error': str(e)}), 500