from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from models.productivos.mortalidad_lactancia import MortalidadLactancia
from models.galpon import Galpon
from models.poza import Poza

bp = Blueprint('productivos', __name__)

@bp.route('/mortalidad-lactancia')
def mortalidad_lactancia():
    try:
        galpones = Galpon.obtener_todos()
        causas = MortalidadLactancia.get_causas_mortalidad()
        today = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('mortalidad_lactancia.html', 
                             galpones=galpones, 
                             causas=causas,
                             today=today)
    except Exception as e:
        return f"Error cargando página: {e}", 500

@bp.route('/mortalidad-lactancia/registrar', methods=['POST'])
def registrar_mortalidad_lactancia():
    try:
        print("Datos recibidos:", request.form)  # Debug
        
        # Validar datos requeridos
        required_fields = ['galpon_id', 'poza_id', 'fecha', 'cantidad', 'causa']
        for field in required_fields:
            if not request.form.get(field):
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'})
        
        # Validar que la cantidad sea mayor a 0
        cantidad = int(request.form['cantidad'])
        if cantidad <= 0:
            return jsonify({'success': False, 'error': 'La cantidad debe ser mayor a 0'})
        
        # Crear registro
        mortalidad = MortalidadLactancia(
            galpon_id=int(request.form['galpon_id']),
            poza_id=int(request.form['poza_id']),
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            cantidad=cantidad,
            causa=request.form['causa'],
            observaciones=request.form.get('observaciones', '')
        )
        
        # Guardar en base de datos
        if mortalidad.guardar():
            return jsonify({
                'success': True, 
                'message': 'Mortalidad registrada exitosamente',
                'id': mortalidad.id
            })
        else:
            return jsonify({'success': False, 'error': 'Error al guardar en base de datos'})
        
    except ValueError as e:
        return jsonify({'success': False, 'error': 'Error en formato de datos: ' + str(e)})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Error del servidor: ' + str(e)})

@bp.route('/api/mortalidad-lactancia/recientes')
def api_mortalidad_recientes():
    try:
        registros = MortalidadLactancia.obtener_todos(limite=10)
        
        # Formatear datos para el frontend
        registros_formateados = []
        for registro in registros:
            # Obtener label de la causa
            causa_label = next(
                (c['label'] for c in MortalidadLactancia.get_causas_mortalidad() 
                 if c['value'] == registro.causa), 
                registro.causa
            )
            
            registros_formateados.append({
                'id': registro.id,
                'fecha': registro.fecha.strftime('%d/%m/%Y'),
                'galpon_nombre': getattr(registro, 'galpon_nombre', f'Galpón {registro.galpon_id}'),
                'poza_nombre': getattr(registro, 'poza_nombre', f'Poza {registro.poza_id}'),
                'cantidad': registro.cantidad,
                'causa': registro.causa,
                'causa_label': causa_label,
                'observaciones': registro.observaciones or '-',
                'fecha_creacion': registro.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            })
        
        return jsonify(registros_formateados)
        
    except Exception as e:
        print(f"Error en API recientes: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/galpones/<int:galpon_id>/pozas-lactancia')
def api_pozas_lactancia(galpon_id):
    """Obtiene pozas que pueden tener lactantes"""
    try:
        poza_model = Poza()
        
        # Primero intentamos obtener pozas con lactantes reales
        pozas_con_lactantes = poza_model.obtener_pozas_con_lactantes(galpon_id)
        
        if pozas_con_lactantes:
            # Si hay pozas con lactantes reales, las usamos
            pozas_data = []
            for poza in pozas_con_lactantes:
                pozas_data.append({
                    'id': poza[0],  # id
                    'nombre': poza[1],  # nombre
                    'tipo': poza[2],  # tipo
                    'tiene_lactantes_reales': True
                })
            return jsonify(pozas_data)
        else:
            # Si no hay pozas con lactantes, mostramos todas las pozas del galpón
            # que sean de tipo 'lactancia' o 'reproductora'
            todas_pozas = poza_model.obtener_por_galpon(galpon_id)
            pozas_data = []
            
            for poza in todas_pozas:
                # Filtrar solo pozas donde pueden haber lactantes
                if poza[2] in ['lactancia', 'reproductora']:  # poza[2] es el tipo
                    pozas_data.append({
                        'id': poza[0],  # id
                        'nombre': poza[1],  # nombre
                        'tipo': poza[2],  # tipo
                        'capacidad': poza[3],  # capacidad
                        'tiene_lactantes_reales': False
                    })
            
            return jsonify(pozas_data)
        
    except Exception as e:
        print(f"Error obteniendo pozas lactancia: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/galpones/<int:galpon_id>/pozas')
def api_pozas_galpon(galpon_id):
    """Obtiene todas las pozas de un galpón (para uso general)"""
    try:
        poza_model = Poza()
        pozas = poza_model.obtener_por_galpon(galpon_id)
        
        pozas_data = []
        for poza in pozas:
            pozas_data.append({
                'id': poza[0],
                'nombre': poza[1],
                'tipo': poza[2],
                'capacidad': poza[3],
                'estado': poza[4]
            })
        
        return jsonify(pozas_data)
        
    except Exception as e:
        print(f"Error obteniendo pozas: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/mortalidad-lactancia/estadisticas')
def api_estadisticas_mortalidad():
    """Estadísticas de mortalidad de los últimos 30 días"""
    try:
        fecha_inicio = (datetime.now() - timedelta(days=30)).date()
        fecha_fin = datetime.now().date()
        
        datos = MortalidadLactancia.obtener_por_rango_fechas(fecha_inicio, fecha_fin)
        
        # Procesar datos para gráficos
        fechas = [d[0].strftime('%d/%m') for d in datos]
        muertes = [d[1] for d in datos]
        
        return jsonify({
            'fechas': fechas,
            'muertes': muertes,
            'total_muertes': sum(muertes),
            'promedio_diario': sum(muertes) / len(muertes) if muertes else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta adicional para obtener detalles de una poza específica
@bp.route('/api/pozas/<int:poza_id>')
def api_poza_detalle(poza_id):
    try:
        poza_model = Poza()
        poza = poza_model.obtener_por_id(poza_id)
        
        if poza:
            return jsonify({
                'id': poza[0],
                'nombre': poza[1],
                'tipo': poza[2],
                'capacidad': poza[3],
                'galpon_id': poza[4],
                'estado': poza[5]
            })
        else:
            return jsonify({'error': 'Poza no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500