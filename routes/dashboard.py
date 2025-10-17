from flask import Blueprint, render_template, jsonify
from datetime import datetime
from models.parto import Parto
from models.animal import Animal
from models.mortalidad_general import MortalidadGeneral

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def dashboard():
    """Página principal del dashboard"""
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    return render_template('dashboard.html', fecha_actual=fecha_actual)

@bp.route('/api/dashboard/estadisticas')
def get_estadisticas():
    """API para obtener estadísticas del dashboard"""
    try:
        # Obtener datos básicos
        animal_model = Animal()
        parto_model = Parto()
        mortalidad_model = MortalidadGeneral()
        
        # Datos de ejemplo - ajusta según tus modelos
        total_animales = animal_model.obtener_total() if hasattr(animal_model, 'obtener_total') else 0
        partos_mes = parto_model.obtener_este_mes() if hasattr(parto_model, 'obtener_este_mes') else 0
        mortalidad_general_mes = mortalidad_model.obtener_este_mes() if hasattr(mortalidad_model, 'obtener_este_mes') else 0
        
        # Datos de ejemplo para las otras métricas
        destetes_mes = 0  # Implementar cuando tengas el modelo
        ventas_mes = 0    # Implementar cuando tengas el modelo
        gastos_mes = 0    # Implementar cuando tengas el modelo
        
        # Últimos partos
        ultimos_partos = parto_model.obtener_recientes(5) if hasattr(parto_model, 'obtener_recientes') else []
        
        # Última mortalidad general
        ultima_mortalidad_general = mortalidad_model.obtener_recientes(5) if hasattr(mortalidad_model, 'obtener_recientes') else []
        
        return jsonify({
            'success': True,
            'total_animales': total_animales,
            'partos_mes': partos_mes,
            'mortalidad_general_mes': mortalidad_general_mes,
            'destetes_mes': destetes_mes,
            'ventas_mes': ventas_mes,
            'gastos_mes': gastos_mes,
            'ultimos_partos': ultimos_partos,
            'ultima_mortalidad_general': ultima_mortalidad_general
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }), 500

@bp.route('/api/dashboard/tendencias')
def get_tendencias():
    """API para obtener datos de tendencias"""
    try:
        # Datos de ejemplo - implementar con datos reales
        partos_mensuales = [
            {'mes': 'Ene', 'total': 15},
            {'mes': 'Feb', 'total': 18},
            {'mes': 'Mar', 'total': 12},
            {'mes': 'Abr', 'total': 20}
        ]
        
        ventas_mensuales = [
            {'mes': 'Ene', 'total': 1500},
            {'mes': 'Feb', 'total': 1800},
            {'mes': 'Mar', 'total': 1200},
            {'mes': 'Abr', 'total': 2000}
        ]
        
        return jsonify({
            'success': True,
            'partos_mensuales': partos_mensuales,
            'ventas_mensuales': ventas_mensuales
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo tendencias: {str(e)}'
        }), 500