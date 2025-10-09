from flask import Blueprint, request, jsonify, render_template
from models.galpones import Galpon  # ✅ Solo este import

bp = Blueprint('galpones', __name__)

@bp.route('/')
def listar_galpones():
    try:
        galpon_model = Galpon()
        galpones = galpon_model.obtener_todos()
        return render_template('galpones.html', galpones=galpones)
    except Exception as e:
        return f"Error: {str(e)}", 500

@bp.route('/crear', methods=['POST'])
def crear_galpon():
    try:
        data = request.form
        galpon_model = Galpon()
        galpon_id = galpon_model.crear(data)
        return jsonify({'success': True, 'id': galpon_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def obtener_galpon(id):
    try:
        galpon_model = Galpon()
        galpon = galpon_model.obtener_por_id(id)
        if galpon:
            return jsonify(galpon)
        return jsonify({'error': 'Galpón no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/actualizar', methods=['PUT'])
def actualizar_galpon(id):
    try:
        data = request.json
        galpon_model = Galpon()
        galpon_model.actualizar(id, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<int:id>/eliminar', methods=['DELETE'])
def eliminar_galpon(id):
    try:
        galpon_model = Galpon()
        galpon_model.eliminar(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500