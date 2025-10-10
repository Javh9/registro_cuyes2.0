from flask import Blueprint, request, jsonify, render_template
from models.galpon import Galpon

bp = Blueprint('galpon', __name__)

@bp.route('/')
def listar_galpones():
    galpon_model = Galpon()
    galpones = galpon_model.obtener_todos()
    return render_template('galpones.html', galpones=galpones)

@bp.route('/crear', methods=['POST'])
def crear_galpon():
    try:
        data = request.form
        galpon_model = Galpon()
        galpon_id = galpon_model.crear(data)
        
        if galpon_id:
            return jsonify({'success': True, 'id': galpon_id})
        else:
            return jsonify({'success': False, 'error': 'Error creando galpón'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})