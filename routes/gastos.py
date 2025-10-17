from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.gasto import Gasto

bp = Blueprint('gastos', __name__)

@bp.route('/')
def listar_gastos():
    """Página principal de gastos"""
    return render_template('gastos.html')

@bp.route('/api/registrar', methods=['POST'])
def registrar_gasto():
    """API para registrar nuevo gasto"""
    try:
        data = request.get_json()
        
        gasto_model = Gasto()
        resultado = gasto_model.registrar(data)
        
        if resultado:
            return jsonify({
                'success': True,
                'message': 'Gasto registrado correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al registrar gasto'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/historial')
def obtener_historial():
    """API para obtener historial de gastos"""
    try:
        gasto_model = Gasto()
        gastos = gasto_model.obtener_gastos_recientes(50)  # Últimos 50 gastos
        
        gastos_data = []
        for gasto in gastos:
            gastos_data.append({
                'id': gasto[0],
                'fecha': gasto[1].strftime('%d/%m/%Y'),
                'tipo': gasto[2],
                'descripcion': gasto[3],
                'monto': float(gasto[4]),
                'proveedor': gasto[5] or '',
                'observaciones': gasto[6] or ''
            })
        
        return jsonify({
            'success': True,
            'data': gastos_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo historial: {str(e)}'
        }), 500