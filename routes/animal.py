from flask import Blueprint, request, jsonify, render_template
from models.animal import Animal
from models.poza import Poza

bp = Blueprint('animal', __name__)

@bp.route('/')
def listar_animales():
    animal_model = Animal()
    animales = animal_model.obtener_todos()
    return render_template('animales.html', animales=animales)

@bp.route('/crear', methods=['POST'])
def crear_animal():
    try:
        data = request.form
        animal_model = Animal()
        animal_id = animal_model.crear(data)
        
        if animal_id:
            return jsonify({'success': True, 'id': animal_id})
        else:
            return jsonify({'success': False, 'error': 'Error creando animal'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/mover', methods=['POST'])
def mover_animal():
    try:
        data = request.json
        animal_model = Animal()
        resultado = animal_model.mover_poza(
            data['animal_id'],
            data['nueva_poza_id'],
            data['motivo']
        )
        
        if resultado:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Error moviendo animal'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/por-etapa/<etapa>')
def animales_por_etapa(etapa):
    try:
        animal_model = Animal()
        animales = animal_model.obtener_por_etapa(etapa)
        return jsonify([dict(animal) for animal in animales])
    except Exception as e:
        return jsonify({'error': str(e)}), 500