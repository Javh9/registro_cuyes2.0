from flask import Blueprint, request, jsonify, render_template
from models.mortalidad_general import MortalidadGeneral
from models.galpon import Galpon
from models.poza import Poza

bp = Blueprint('mortalidad_general', __name__)

@bp.route('/')
def mortalidad_form():
    galpon_model = Galpon()
    galpones = galpon_model.obtener_todos()
    return render_template('mortalidad_general.html', galpones=galpones)

@bp.route('/api/tipos-cuy')
def get_tipos_cuy():
    return jsonify({
        'tipos_cuy': ['reproductor', 'lactante', 'destete', 'reemplazo', 'engorde_destete', 'engorde_descarte']
    })

@bp.route('/api/pozas-por-tipo')
def get_pozas_por_tipo():
    tipo_cuy = request.args.get('tipo_cuy')
    galpon_id = request.args.get('galpon_id')
    
    if not tipo_cuy:
        return jsonify({'pozas': []})
    
    tipo_poza_map = {
        'reproductor': 'reproductora',
        'lactante': 'lactancia', 
        'destete': 'destete',
        'reemplazo': 'reemplazo',
        'engorde_destete': 'engorde',
        'engorde_descarte': 'engorde'
    }
    
    tipo_poza = tipo_poza_map.get(tipo_cuy)
    poza_model = Poza()
    pozas = poza_model.obtener_por_tipo_y_galpon(tipo_poza, galpon_id) if tipo_poza else []
    
    return jsonify({'pozas': pozas})

@bp.route('/api/registrar', methods=['POST'])
def registrar_mortalidad():
    try:
        data = request.get_json()
        
        mortalidad_model = MortalidadGeneral()
        resultado = mortalidad_model.registrar(data)
        
        if resultado:
            return jsonify({
                'success': True,
                'message': 'Mortalidad registrada correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al registrar mortalidad'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/historial')
def get_historial():
    try:
        mortalidad_model = MortalidadGeneral()
        registros = mortalidad_model.obtener_todos()
        
        return jsonify({
            'success': True,
            'data': registros
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo historial: {str(e)}'
        }), 500
