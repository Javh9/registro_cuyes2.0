from flask import Blueprint, request, jsonify, render_template
from models.poza import Poza

bp = Blueprint('poza', __name__)

@bp.route('/')
def listar_pozas():
    poza_model = Poza()
    pozas = poza_model.obtener_todos()
    return render_template('pozas.html', pozas=pozas)

@bp.route('/crear', methods=['POST'])
def crear_poza():
    try:
        data = request.form
        poza_model = Poza()
        poza_id = poza_model.crear(data)
        
        if poza_id:
            return jsonify({'success': True, 'id': poza_id})
        else:
            return jsonify({'success': False, 'error': 'Error creando poza'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/<int:id>', methods=['GET'])
def obtener_poza(id):
    try:
        poza_model = Poza()
        poza = poza_model.obtener_por_id(id)
        if poza:
            return jsonify(poza)
        return jsonify({'error': 'Poza no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500