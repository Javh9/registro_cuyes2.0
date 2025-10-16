from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from db.connection import get_db_connection
from datetime import datetime
import os
import json

# ✅ PRIMERO definir app
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'db', 'cuyes.db')

# =============================================================================
# RUTAS PRINCIPALES (PÁGINAS)
# =============================================================================

@app.route('/')
def index():
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    return render_template('dashboard.html', fecha_actual=fecha_actual)

@app.route('/dashboard')
def dashboard():
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
    from models.galpon import Galpon
    galpon_model = Galpon()
    galpones = galpon_model.obtener_todos()
    return render_template('destetes.html', galpones=galpones)

@app.route('/mortalidad_lactancia')
def mortalidad_lactancia():
    from models.galpon import Galpon
    from models.mortalidad_lactancia import MortalidadLactancia
    
    galpon_model = Galpon()
    mortalidad_model = MortalidadLactancia()
    
    galpones = galpon_model.obtener_todos()
    causas = mortalidad_model.obtener_causas_mortalidad()
    
    return render_template('mortalidad_lactancia.html', 
                         galpones=galpones, 
                         causas=causas)

@app.route('/ventas')
def ventas():
    return render_template('ventas.html')

@app.route('/galpones')
def galpones():
    from models.galpon import Galpon
    galpon_model = Galpon()
    galpones = galpon_model.obtener_todos()
    return render_template('galpones.html', galpones=galpones)

@app.route('/inventario')
def inventario():
    return render_template('inventario.html')

@app.route('/balance')
def balance():
    return render_template('balance.html')

@app.route('/predicciones')
def predicciones():
    return render_template('predicciones.html')

# =============================================================================
# RUTAS DE REGISTRO (FORMULARIOS)
# =============================================================================

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

@app.route('/registrar_mortalidad_lactancia', methods=['POST'])
def registrar_mortalidad_lactancia():
    try:
        from models.mortalidad_lactancia import MortalidadLactancia
        mortalidad_model = MortalidadLactancia()
        
        datos = {
            'galpon_id': request.form['galpon_id'],
            'poza_id': request.form['poza_id'],
            'fecha': datetime.now().date(),
            'cantidad': int(request.form['cantidad']),
            'causa': request.form['causa'],
            'observaciones': request.form.get('observaciones', '')
        }
        
        mortalidad_id = mortalidad_model.registrar(datos)
        if mortalidad_id:
            flash('Mortalidad registrada exitosamente!', 'success')
            return redirect(url_for('mortalidad_lactancia'))
        else:
            flash('Error al registrar la mortalidad', 'error')
            return redirect(url_for('mortalidad_lactancia'))
            
    except Exception as e:
        print(f"Error registrando mortalidad: {e}")
        flash('Error al registrar la mortalidad', 'error')
        return redirect(url_for('mortalidad_lactancia'))

@app.route('/registrar_destete_pozas', methods=['POST'])
def registrar_destete_pozas():
    try:
        from models.destete import Destete
        destete_model = Destete()
        
        galpon_id = request.form['galpon_id']
        destetes_data = json.loads(request.form['destetes_data'])
        
        # Registrar cada poza individualmente
        for poza_data in destetes_data:
            datos = {
                'galpon_id': galpon_id,
                'poza_origen_id': poza_data['poza_id'],
                'fecha_destete': datetime.now().date(),
                'machos_destetados': poza_data['machos'],
                'hembras_destetadas': poza_data['hembras'],
                'reemplazo_machos': int(request.form.get('reemplazo_machos', 0)),
                'reemplazo_hembras': int(request.form.get('reemplazo_hembras', 0)),
                'engorde_machos': int(request.form.get('engorde_machos', 0)),
                'engorde_hembras': int(request.form.get('engorde_hembras', 0)),
                'venta_directa_machos': int(request.form.get('venta_directa_machos', 0)),
                'venta_directa_hembras': int(request.form.get('venta_directa_hembras', 0)),
                'observaciones': request.form.get('observaciones', '')
            }
            
            destete_id = destete_model.registrar(datos)
            if not destete_id:
                flash('Error al registrar algunos destetes', 'error')
                return redirect(url_for('destetes'))
        
        flash('Destete registrado exitosamente!', 'success')
        return redirect(url_for('destetes'))
            
    except Exception as e:
        print(f"Error registrando destete por pozas: {e}")
        flash('Error al registrar el destete', 'error')
        return redirect(url_for('destetes'))

@app.route('/registrar_gasto', methods=['POST'])
def registrar_gasto():
    try:
        from models.gasto import Gasto
        gasto_model = Gasto()
        
        datos = {
            'fecha': request.form['fecha'],
            'tipo': request.form['tipo'],
            'descripcion': request.form['descripcion'],
            'monto': float(request.form['monto']),
            'proveedor': request.form.get('proveedor', ''),
            'observaciones': request.form.get('observaciones', '')
        }
        
        gasto_id = gasto_model.registrar(datos)
        if gasto_id:
            flash('Gasto registrado exitosamente!', 'success')
            return redirect(url_for('gastos'))
        else:
            flash('Error al registrar el gasto', 'error')
            return redirect(url_for('gastos'))
            
    except Exception as e:
        print(f"Error registrando gasto: {e}")
        flash('Error al registrar el gasto', 'error')
        return redirect(url_for('gastos'))

@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    try:
        from models.venta import Venta
        venta_model = Venta()
        
        datos = {
            'fecha_venta': request.form['fecha_venta'],
            'cliente': request.form['cliente'],
            'tipo_producto': request.form['tipo_producto'],
            'cantidad': int(request.form['cantidad']),
            'precio_unitario': float(request.form['precio_unitario']),
            'total': float(request.form['total']),
            'observaciones': request.form.get('observaciones', '')
        }
        
        venta_id = venta_model.registrar(datos)
        if venta_id:
            flash('Venta registrada exitosamente!', 'success')
            return redirect(url_for('ventas'))
        else:
            flash('Error al registrar la venta', 'error')
            return redirect(url_for('ventas'))
            
    except Exception as e:
        print(f"Error registrando venta: {e}")
        flash('Error al registrar la venta', 'error')
        return redirect(url_for('ventas'))

# =============================================================================
# RUTAS GALPONES Y POZAS (GESTIÓN)
# =============================================================================

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

@app.route('/editar_galpon', methods=['POST'])
def editar_galpon():
    try:
        from models.galpon import Galpon
        galpon_model = Galpon()
        
        datos = {
            'nombre': request.form['nombre'],
            'capacidad': int(request.form['capacidad']),
            'ubicacion': request.form['ubicacion'],
            'estado': request.form.get('estado', 'activo')
        }
        
        galpon_id = int(request.form['galpon_id'])
        exito = galpon_model.actualizar(galpon_id, datos)
        
        if exito:
            flash('Galpón actualizado exitosamente!', 'success')
        else:
            flash('Error al actualizar el galpón', 'error')
            
        return redirect(url_for('galpones'))
            
    except Exception as e:
        print(f"Error actualizando galpón: {e}")
        flash('Error al actualizar el galpón', 'error')
        return redirect(url_for('galpones'))

@app.route('/editar_poza', methods=['POST'])
def editar_poza():
    try:
        from models.poza import Poza
        poza_model = Poza()
        
        datos = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'capacidad': int(request.form['capacidad']),
            'galpon_id': int(request.form['galpon_id']),
            'estado': request.form.get('estado', 'activo')
        }
        
        poza_id = int(request.form['poza_id'])
        exito = poza_model.actualizar(poza_id, datos)
        
        if exito:
            flash('Poza actualizada exitosamente!', 'success')
        else:
            flash('Error al actualizar la poza', 'error')
            
        return redirect(url_for('galpones'))
            
    except Exception as e:
        print(f"Error actualizando poza: {e}")
        flash('Error al actualizar la poza', 'error')
        return redirect(url_for('galpones'))

# =============================================================================
# APIs PARA DATOS DINÁMICOS
# =============================================================================

@app.route('/api/galpones/<int:galpon_id>/pozas')
def api_pozas_por_galpon(galpon_id):
    try:
        from models.poza import Poza
        poza_model = Poza()
        pozas = poza_model.obtener_por_galpon(galpon_id)
        
        pozas_data = []
        for poza in pozas:
            pozas_data.append({
                'id': poza[0],
                'nombre': poza[1],
                'tipo': poza[2]
            })
        
        return jsonify(pozas_data)
    except Exception as e:
        print(f"Error API pozas: {e}")
        return jsonify([])

@app.route('/api/galpones/<int:galpon_id>/pozas_lactancia')
def api_pozas_lactancia(galpon_id):
    try:
        print(f"🔍 DEBUG API: Llegó a /api/galpones/{galpon_id}/pozas_lactancia")
        
        # Importar aquí para evitar problemas de importación circular
        from models.poza import Poza
        poza_model = Poza()
        
        print(f"🔍 DEBUG API: Instancia de Poza creada, buscando pozas...")
        pozas = poza_model.obtener_pozas_con_lactantes(galpon_id)
        
        print(f"🔍 DEBUG API: Resultado de obtener_pozas_con_lactantes: {pozAs}")
        print(f"🔍 DEBUG API: Tipo del resultado: {type(pozAs)}")
        print(f"🔍 DEBUG API: Longitud del resultado: {len(pozAs) if pozas else 0}")
        
        # Si no hay pozas reproductoras, mostrar todas las pozas del galpón para debug
        if not pozas:
            print(f"🔍 DEBUG API: No se encontraron pozas reproductoras, mostrando todas las pozas del galpón")
            pozas = poza_model.obtener_por_galpon(galpon_id)
            print(f"🔍 DEBUG API: Todas las pozas del galpón: {pozAs}")
        
        pozas_data = []
        for poza in pozas:
            poza_info = {
                'id': poza[0],
                'nombre': poza[1],
                'tipo': poza[2]
            }
            print(f"🔍 DEBUG API: Procesando poza: {poza_info}")
            pozas_data.append(poza_info)
        
        print(f"🔍 DEBUG API: Datos finales a enviar: {pozas_data}")
        return jsonify(pozas_data)
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en api_pozas_lactancia: {e}")
        import traceback
        traceback.print_exc()
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

@app.route('/api/galpones/<int:galpon_id>')
def api_obtener_galpon(galpon_id):
    try:
        from models.galpon import Galpon
        galpon_model = Galpon()
        galpon = galpon_model.obtener_por_id(galpon_id)
        
        if galpon:
            galpon_data = {
                'id': galpon[0],
                'nombre': galpon[1],
                'capacidad': galpon[2],
                'ubicacion': galpon[3],
                'estado': galpon[4]
            }
            return jsonify(galpon_data)
        else:
            return jsonify({'error': 'Galpón no encontrado'}), 404
            
    except Exception as e:
        print(f"Error API obtener galpón: {e}")
        return jsonify({'error': 'Error del servidor'}), 500

# =============================================================================
# APIs PARA DASHBOARD
# =============================================================================

@app.route('/api/dashboard/estadisticas')
def api_estadisticas_dashboard():
    try:
        from models.dashboard import Dashboard
        dashboard_model = Dashboard()
        estadisticas = dashboard_model.obtener_estadisticas()
        return jsonify(estadisticas)
    except Exception as e:
        print(f"Error API dashboard: {e}")
        return jsonify({})

@app.route('/api/dashboard/tendencias')
def api_tendencias_dashboard():
    try:
        from models.dashboard import Dashboard
        dashboard_model = Dashboard()
        tendencias = dashboard_model.obtener_tendencias_mensuales()
        return jsonify(tendencias)
    except Exception as e:
        print(f"Error API tendencias dashboard: {e}")
        return jsonify({})

@app.route('/api/metricas')
def api_metricas():
    try:
        conn = get_db_connection()
        
        # Métricas básicas (por ahora devolvemos datos de ejemplo)
        metricas = {
            'reproductores': 45,
            'lactantes': 23,
            'destete': 15,
            'engorde': 32,
            'total_animales': 115,
            'partos_mes': 8,
            'mortalidad_mes': 3,
            'gastos_mes': 1250.00
        }
        
        conn.close()
        return jsonify(metricas)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# APIs PARA MORTALIDAD LACTANCIA
# =============================================================================

@app.route('/api/mortalidad_lactancia/registrar', methods=['POST'])
def api_registrar_mortalidad_lactancia():
    try:
        print("🔍 DEBUG: Llegó a /api/mortalidad_lactancia/registrar")
        print("🔍 DEBUG: Datos del formulario:", dict(request.form))
        
        from models.mortalidad_lactancia import MortalidadLactancia
        mortalidad_model = MortalidadLactancia()
        
        # Validar datos requeridos
        required_fields = ['galpon_id', 'poza_id', 'fecha', 'cantidad', 'causa']
        for field in required_fields:
            if not request.form.get(field):
                print(f"❌ DEBUG: Falta campo {field}")
                return jsonify({'success': False, 'error': f'Campo {field} es requerido'})
        
        datos = {
            'galpon_id': int(request.form['galpon_id']),
            'poza_id': int(request.form['poza_id']),
            'fecha': request.form['fecha'],
            'cantidad': int(request.form['cantidad']),
            'causa': request.form['causa'],
            'observaciones': request.form.get('observaciones', '')
        }
        
        print("🔍 DEBUG: Datos procesados:", datos)
        
        mortalidad_id = mortalidad_model.registrar(datos)
        if mortalidad_id:
            print("✅ DEBUG: Mortalidad registrada con ID:", mortalidad_id)
            return jsonify({
                'success': True, 
                'message': 'Mortalidad registrada exitosamente',
                'id': mortalidad_id
            })
        else:
            print("❌ DEBUG: Error al guardar en base de datos")
            return jsonify({'success': False, 'error': 'Error al guardar en base de datos'})
        
    except Exception as e:
        print("❌ DEBUG: Excepción en api_registrar_mortalidad_lactancia:", str(e))
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mortalidad_lactancia/recientes')
def api_mortalidad_recientes():
    try:
        from models.mortalidad_lactancia import MortalidadLactancia
        mortalidad_model = MortalidadLactancia()
        registros = mortalidad_model.obtener_recientes(10)
        
        registros_formateados = []
        for registro in registros:
            registros_formateados.append({
                'id': registro[0],
                'fecha': registro[1].strftime('%d/%m/%Y'),
                'cantidad': registro[2],
                'causa': registro[3],
                'observaciones': registro[4] or '-',
                'galpon_nombre': registro[5] or f'Galpón {registro[0]}',
                'poza_nombre': registro[6] or f'Poza {registro[0]}'
            })
        
        return jsonify(registros_formateados)
        
    except Exception as e:
        print(f"Error API mortalidad recientes: {e}")
        return jsonify([])

# =============================================================================
# APIs PARA DESTETES
# =============================================================================

@app.route('/api/destetes/pozas-con-crias')
def api_pozas_con_crias_destetar():
    """Obtiene pozas que tienen crías listas para destetar"""
    try:
        from models.destete import Destete
        destete_model = Destete()
        
        galpon_id = request.args.get('galpon_id', type=int)
        if not galpon_id:
            return jsonify([])
        
        pozas = destete_model.obtener_pozas_con_crias_destetar(galpon_id)
        
        pozas_data = []
        for poza in pozas:
            pozas_data.append({
                'id': poza[0],
                'nombre': poza[1],
                'tipo': poza[2],
                'partos_recientes': poza[3],
                'crias_nacidas': poza[4]
            })
        
        return jsonify(pozas_data)
        
    except Exception as e:
        print(f"Error API pozas con crías: {e}")
        return jsonify([])

@app.route('/api/destetes/recientes')
def api_destetes_recientes():
    """Obtiene destetes recientes para mostrar en el template"""
    try:
        from models.destete import Destete
        destete_model = Destete()
        destetes = destete_model.obtener_destetes_recientes(10)
        
        destetes_data = []
        for destete in destetes:
            total_destetados = destete[2] + destete[3]
            total_reemplazo = destete[4] + destete[5]
            total_engorde = destete[6] + destete[7]
            total_venta = destete[8] + destete[9]
            
            destetes_data.append({
                'id': destete[0],
                'fecha_destete': destete[1].strftime('%d/%m/%Y'),
                'machos_destetados': destete[2],
                'hembras_destetadas': destete[3],
                'total_destetados': total_destetados,
                'reemplazo_machos': destete[4],
                'reemplazo_hembras': destete[5],
                'total_reemplazo': total_reemplazo,
                'engorde_machos': destete[6],
                'engorde_hembras': destete[7],
                'total_engorde': total_engorde,
                'venta_machos': destete[8],
                'venta_hembras': destete[9],
                'total_venta': total_venta,
                'observaciones': destete[10] or '-',
                'galpon_nombre': destete[11] or f'Galpón {destete[0]}',
                'poza_origen_nombre': destete[12] or f'Poza {destete[0]}'
            })
        
        return jsonify(destetes_data)
        
    except Exception as e:
        print(f"Error API destetes recientes: {e}")
        return jsonify([])

@app.route('/api/destetes/estadisticas')
def api_estadisticas_destete():
    """Obtiene estadísticas de destetes para el dashboard"""
    try:
        from models.destete import Destete
        destete_model = Destete()
        estadisticas = destete_model.obtener_estadisticas_destete()
        return jsonify(estadisticas)
    except Exception as e:
        print(f"Error API estadísticas destete: {e}")
        return jsonify({})

# =============================================================================
# APIs PARA GASTOS
# =============================================================================

@app.route('/api/gastos/resumen-mensual')
def api_gastos_resumen_mensual():
    try:
        from models.gasto import Gasto
        gasto_model = Gasto()
        resumen = gasto_model.obtener_resumen_mensual()
        return jsonify(resumen)
    except Exception as e:
        print(f"Error API resumen gastos: {e}")
        return jsonify({})

@app.route('/api/gastos/recientes')
def api_gastos_recientes():
    try:
        from models.gasto import Gasto
        gasto_model = Gasto()
        gastos = gasto_model.obtener_gastos_recientes(10)
        
        gastos_data = []
        for gasto in gastos:
            # Formatear el tipo para mostrar mejor
            tipo_labels = {
                'alimentacion': 'Alimentación',
                'medicamentos': 'Medicamentos', 
                'mantenimiento': 'Mantenimiento',
                'mano_obra': 'Mano de Obra',
                'transporte': 'Transporte',
                'otros': 'Otros'
            }
            
            gastos_data.append({
                'id': gasto[0],
                'fecha': gasto[1].strftime('%d/%m/%Y'),
                'tipo': gasto[2],
                'tipo_label': tipo_labels.get(gasto[2], gasto[2]),
                'descripcion': gasto[3],
                'monto': float(gasto[4]),
                'proveedor': gasto[5] or '-',
                'observaciones': gasto[6] or '-'
            })
        
        return jsonify(gastos_data)
    except Exception as e:
        print(f"Error API gastos recientes: {e}")
        return jsonify([])

@app.route('/api/gastos/estadisticas-anuales')
def api_gastos_estadisticas_anuales():
    """Obtiene estadísticas de gastos por mes del año actual"""
    try:
        from models.gasto import Gasto
        gasto_model = Gasto()
        año = request.args.get('año', type=int)
        estadisticas = gasto_model.obtener_estadisticas_anuales(año)
        
        # Formatear datos para gráficos
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        datos_mensuales = [0] * 12
        
        for stat in estadisticas:
            mes_index = int(stat[0]) - 1
            if 0 <= mes_index < 12:
                datos_mensuales[mes_index] = float(stat[1])
        
        return jsonify({
            'meses': meses,
            'gastos': datos_mensuales,
            'total_anual': sum(datos_mensuales)
        })
    except Exception as e:
        print(f"Error API estadísticas gastos: {e}")
        return jsonify({'meses': [], 'gastos': [], 'total_anual': 0})

# =============================================================================
# APIs PARA VENTAS
# =============================================================================

@app.route('/api/ventas/estadisticas')
def api_estadisticas_ventas():
    try:
        from models.venta import Venta
        venta_model = Venta()
        estadisticas = venta_model.obtener_estadisticas_completas()
        return jsonify(estadisticas)
    except Exception as e:
        print(f"Error API estadísticas ventas: {e}")
        return jsonify({
            'ventas_mes': 0,
            'total_ventas': 0,
            'promedio_venta': 0,
            'total_clientes': 0
        })

@app.route('/api/ventas/recientes')
def api_ventas_recientes():
    try:
        from models.venta import Venta
        venta_model = Venta()
        ventas = venta_model.obtener_ventas_recientes(10)
        
        ventas_data = []
        for venta in ventas:
            ventas_data.append({
                'id': venta[0],
                'fecha_venta': venta[1].isoformat() if hasattr(venta[1], 'isoformat') else str(venta[1]),
                'cliente': venta[2] if len(venta) > 2 else '',
                'tipo_producto': venta[3] if len(venta) > 3 else '',
                'cantidad': venta[4] if len(venta) > 4 else 0,
                'precio_unitario': float(venta[5]) if len(venta) > 5 and venta[5] else 0.0,
                'total': float(venta[6]) if len(venta) > 6 and venta[6] else 0.0,
                'observaciones': venta[7] if len(venta) > 7 else ''
            })
        
        return jsonify(ventas_data)
    except Exception as e:
        print(f"Error API ventas recientes: {e}")
        return jsonify([])

# =============================================================================
# APIs PARA INVENTARIO
# =============================================================================

@app.route('/api/inventario/actual')
def api_inventario_actual():
    try:
        from models.inventario import Inventario
        inventario_model = Inventario()
        inventario = inventario_model.calcular_inventario_actual()
        return jsonify(inventario)
    except Exception as e:
        print(f"Error API inventario actual: {e}")
        return jsonify({})

@app.route('/api/inventario/movimientos')
def api_inventario_movimientos():
    try:
        from models.inventario import Inventario
        inventario_model = Inventario()
        movimientos = inventario_model.obtener_movimientos_recientes()
        return jsonify(movimientos)
    except Exception as e:
        print(f"Error API movimientos inventario: {e}")
        return jsonify([])

@app.route('/api/inventario/estadisticas')
def api_inventario_estadisticas():
    try:
        from models.inventario import Inventario
        inventario_model = Inventario()
        estadisticas = inventario_model.obtener_estadisticas_inventario()
        return jsonify(estadisticas)
    except Exception as e:
        print(f"Error API estadísticas inventario: {e}")
        return jsonify({})

# =============================================================================
# APIs PARA BALANCE
# =============================================================================

@app.route('/api/balance/mensual')
def api_balance_mensual():
    try:
        from models.balance import Balance
        balance_model = Balance()
        
        año = request.args.get('ano', type=int)
        mes = request.args.get('mes', type=int)
        
        balance = balance_model.obtener_balance_mensual(año, mes)
        return jsonify(balance)
    except Exception as e:
        print(f"Error API balance mensual: {e}")
        return jsonify({})

@app.route('/api/balance/metricas')
def api_balance_metricas():
    try:
        from models.balance import Balance
        balance_model = Balance()
        metricas = balance_model.obtener_metricas_rentabilidad()
        return jsonify(metricas)
    except Exception as e:
        print(f"Error API métricas balance: {e}")
        return jsonify({})

@app.route('/api/balance/historico')
def api_balance_historico():
    try:
        from models.balance import Balance
        balance_model = Balance()
        historico = balance_model.obtener_historico_mensual(meses=6)
        return jsonify(historico)
    except Exception as e:
        print(f"Error API histórico balance: {e}")
        return jsonify([])

# =============================================================================
# APIs PARA PREDICCIONES
# =============================================================================

@app.route('/api/predicciones/partos')
def api_predicciones_partos():
    try:
        from models.predicciones import Predicciones
        predicciones_model = Predicciones()
        partos_proximos = predicciones_model.predecir_partos_proximos(dias=30)
        return jsonify(partos_proximos)
    except Exception as e:
        print(f"Error API predicciones partos: {e}")
        return jsonify([])

@app.route('/api/predicciones/ventas')
def api_predicciones_ventas():
    try:
        from models.predicciones import Predicciones
        predicciones_model = Predicciones()
        prediccion_ventas = predicciones_model.predecir_ventas_mes()
        return jsonify(prediccion_ventas)
    except Exception as e:
        print(f"Error API predicciones ventas: {e}")
        return jsonify({})

@app.route('/api/predicciones/alertas')
def api_predicciones_alertas():
    try:
        from models.predicciones import Predicciones
        predicciones_model = Predicciones()
        alertas = predicciones_model.generar_alertas_inteligentes()
        return jsonify(alertas)
    except Exception as e:
        print(f"Error API alertas: {e}")
        return jsonify([])

@app.route('/api/predicciones/recomendaciones')
def api_predicciones_recomendaciones():
    try:
        from models.predicciones import Predicciones
        predicciones_model = Predicciones()
        recomendaciones = predicciones_model.obtener_recomendaciones()
        return jsonify(recomendaciones)
    except Exception as e:
        print(f"Error API recomendaciones: {e}")
        return jsonify([])

# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)