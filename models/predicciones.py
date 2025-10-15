from db.connection import get_db_connection
from datetime import datetime, timedelta
import statistics

class Predicciones:
    def __init__(self):
        self.db = get_db_connection()
    
    def predecir_partos_proximos(self, dias=30):
        """Predecir partos en los próximos días basado en historial"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            
            # Obtener partos de los últimos 6 meses para calcular ciclo promedio
            cur.execute("""
                SELECT fecha_parto, galpon_id, poza_id, numero_parto
                FROM partos_simplificada 
                WHERE fecha_parto >= CURRENT_DATE - INTERVAL '6 months'
                ORDER BY fecha_parto DESC
            """)
            partos_recientes = cur.fetchall()
            
            # Calcular ciclo promedio entre partos por poza
            ciclos_pozas = {}
            for parto in partos_recientes:
                poza_id = parto[2]
                fecha_parto = parto[0]
                numero_parto = parto[3]
                
                if poza_id not in ciclos_pozas:
                    ciclos_pozas[poza_id] = []
                
                # Buscar parto anterior de la misma poza
                cur.execute("""
                    SELECT fecha_parto, numero_parto 
                    FROM partos_simplificada 
                    WHERE poza_id = %s AND fecha_parto < %s 
                    ORDER BY fecha_parto DESC 
                    LIMIT 1
                """, (poza_id, fecha_parto))
                parto_anterior = cur.fetchone()
                
                if parto_anterior:
                    dias_entre_partos = (fecha_parto - parto_anterior[0]).days
                    if 40 <= dias_entre_partos <= 90:  # Rango razonable para cuyes
                        ciclos_pozas[poza_id].append(dias_entre_partos)
            
            # Predecir próximos partos
            predicciones = []
            hoy = datetime.now().date()
            
            for poza_id, ciclos in ciclos_pozas.items():
                if len(ciclos) >= 1:  # Mínimo un ciclo para predecir
                    ciclo_promedio = statistics.mean(ciclos)
                    
                    # Obtener último parto de esta poza
                    cur.execute("""
                        SELECT fecha_parto, numero_parto, g.nombre, p.nombre
                        FROM partos_simplificada ps
                        JOIN galpones g ON ps.galpon_id = g.id
                        JOIN pozas p ON ps.poza_id = p.id
                        WHERE ps.poza_id = %s 
                        ORDER BY ps.fecha_parto DESC 
                        LIMIT 1
                    """, (poza_id,))
                    ultimo_parto = cur.fetchone()
                    
                    if ultimo_parto:
                        fecha_ultimo_parto = ultimo_parto[0]
                        siguiente_parto_estimado = fecha_ultimo_parto + timedelta(days=int(ciclo_promedio))
                        
                        # Si el parto estimado está dentro del rango de días
                        if hoy <= siguiente_parto_estimado <= hoy + timedelta(days=dias):
                            dias_faltantes = (siguiente_parto_estimado - hoy).days
                            confianza = min(90, 60 + (len(ciclos) * 10))  # Más ciclos = más confianza
                            
                            predicciones.append({
                                'poza_id': poza_id,
                                'galpon': ultimo_parto[2],
                                'poza': ultimo_parto[3],
                                'fecha_estimada': siguiente_parto_estimado.strftime('%d/%m/%Y'),
                                'dias_faltantes': dias_faltantes,
                                'numero_parto_estimado': ultimo_parto[1] + 1,
                                'ciclo_promedio': int(ciclo_promedio),
                                'confianza': confianza,
                                'historico_ciclos': len(ciclos)
                            })
            
            # Ordenar por días faltantes
            predicciones.sort(key=lambda x: x['dias_faltantes'])
            
            cur.close()
            return predicciones[:10]  # Máximo 10 predicciones
            
        except Exception as e:
            print(f"Error prediciendo partos: {e}")
            return []
    
    def predecir_ventas_mes(self):
        """Predecir ventas del mes basado en historial"""
        if not self.db:
            return {'ventas_estimadas': 0, 'confianza': 0}
        
        try:
            cur = self.db.cursor()
            
            # Obtener ventas de los últimos 6 meses
            cur.execute("""
                SELECT 
                    EXTRACT(YEAR FROM fecha_venta) as año,
                    EXTRACT(MONTH FROM fecha_venta) as mes,
                    SUM(total) as total_ventas
                FROM ventas 
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY año, mes
                ORDER BY año, mes
            """)
            ventas_mensuales = cur.fetchall()
            
            if len(ventas_mensuales) >= 2:
                # Calcular promedio de ventas mensuales
                ventas_totales = [float(venta[2]) for venta in ventas_mensuales]
                ventas_promedio = statistics.mean(ventas_totales)
                
                # Calcular tendencia
                if len(ventas_totales) >= 3:
                    ultimas_3 = ventas_totales[-3:]
                    tendencia = (ultimas_3[-1] - ultimas_3[0]) / len(ultimas_3)
                    ventas_estimadas = ventas_promedio + tendencia
                else:
                    ventas_estimadas = ventas_promedio
                    tendencia = 0
                
                # Calcular confianza basada en la consistencia de los datos
                if len(ventas_totales) >= 3:
                    desviacion = statistics.stdev(ventas_totales)
                    coef_variacion = (desviacion / ventas_promedio) if ventas_promedio > 0 else 1
                    confianza = max(50, 100 - (coef_variacion * 100))
                else:
                    confianza = 60
                
                cur.close()
                
                return {
                    'ventas_estimadas': max(0, ventas_estimadas),
                    'ventas_promedio': ventas_promedio,
                    'tendencia': tendencia,
                    'confianza': min(90, confianza),
                    'meses_historial': len(ventas_totales)
                }
            else:
                cur.close()
                return {
                    'ventas_estimadas': 0,
                    'ventas_promedio': 0,
                    'tendencia': 0,
                    'confianza': 0,
                    'meses_historial': len(ventas_mensuales)
                }
                
        except Exception as e:
            print(f"Error prediciendo ventas: {e}")
            return {'ventas_estimadas': 0, 'confianza': 0}
    
    def generar_alertas_inteligentes(self):
        """Generar alertas inteligentes basadas en patrones"""
        alertas = []
        
        try:
            cur = self.db.cursor()
            
            # 1. Alerta de mortalidad alta
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM fecha) as mes,
                    SUM(cantidad) as total_mortalidad
                FROM mortalidad_lactancia 
                WHERE fecha >= CURRENT_DATE - INTERVAL '3 months'
                GROUP BY mes
                ORDER BY mes DESC
                LIMIT 3
            """)
            mortalidad_mensual = cur.fetchall()
            
            if len(mortalidad_mensual) >= 2:
                mortalidad_reciente = mortalidad_mensual[0][1] or 0
                mortalidad_anterior = mortalidad_mensual[1][1] or 0
                
                if mortalidad_reciente > 0 and mortalidad_anterior > 0:
                    incremento = ((mortalidad_reciente - mortalidad_anterior) / mortalidad_anterior) * 100
                    if incremento > 50:  # 50% de incremento
                        alertas.append({
                            'tipo': 'mortalidad_alta',
                            'titulo': '⚠️ Incremento en Mortalidad',
                            'mensaje': f'La mortalidad aumentó un {incremento:.1f}% respecto al mes anterior',
                            'nivel': 'alto',
                            'fecha': datetime.now().strftime('%d/%m/%Y')
                        })
            
            # 2. Alerta de disminución de partos
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM fecha_parto) as mes,
                    COUNT(*) as total_partos
                FROM partos_simplificada 
                WHERE fecha_parto >= CURRENT_DATE - INTERVAL '4 months'
                GROUP BY mes
                ORDER BY mes DESC
                LIMIT 4
            """)
            partos_mensual = cur.fetchall()
            
            if len(partos_mensual) >= 3:
                partos_ultimos_3 = [p[1] for p in partos_mensual[:3]]
                if all(partos_ultimos_3) and partos_ultimos_3[0] < statistics.mean(partos_ultimos_3[1:]):
                    alertas.append({
                        'tipo': 'partos_decrecientes',
                        'titulo': '📉 Disminución en Partos',
                        'mensaje': 'Los partos han disminuido en los últimos meses',
                        'nivel': 'medio',
                        'fecha': datetime.now().strftime('%d/%m/%Y')
                    })
            
            # 3. Alerta de galpones con baja producción
            cur.execute("""
                SELECT g.nombre, COUNT(p.id) as total_partos
                FROM galpones g
                LEFT JOIN partos_simplificada p ON g.id = p.galpon_id 
                    AND p.fecha_parto >= CURRENT_DATE - INTERVAL '3 months'
                WHERE g.estado = 'activo'
                GROUP BY g.id, g.nombre
                HAVING COUNT(p.id) = 0
            """)
            galpones_sin_partos = cur.fetchall()
            
            for galpon in galpones_sin_partos:
                alertas.append({
                    'tipo': 'galpon_inactivo',
                    'titulo': '🏠 Galpón sin Partos Recientes',
                    'mensaje': f'El galpón {galpon[0]} no registra partos en los últimos 3 meses',
                    'nivel': 'bajo',
                    'fecha': datetime.now().strftime('%d/%m/%Y')
                })
            
            cur.close()
            
        except Exception as e:
            print(f"Error generando alertas: {e}")
        
        return alertas
    
    def obtener_recomendaciones(self):
        """Generar recomendaciones basadas en análisis de datos"""
        recomendaciones = []
        
        try:
            cur = self.db.cursor()
            
            # 1. Recomendación basada en estacionalidad de ventas
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM fecha_venta) as mes,
                    SUM(total) as total_ventas
                FROM ventas 
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY mes
                ORDER BY total_ventas DESC
                LIMIT 1
            """)
            mejor_mes = cur.fetchone()
            
            if mejor_mes:
                meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                recomendaciones.append({
                    'tipo': 'estacionalidad',
                    'titulo': '📈 Mejor Mes para Ventas',
                    'mensaje': f'{meses[int(mejor_mes[0])-1]} es tu mejor mes históricamente para ventas',
                    'icono': 'fas fa-chart-line'
                })
            
            # 2. Recomendación de rotación de reproductores
            cur.execute("""
                SELECT COUNT(DISTINCT poza_id) 
                FROM partos_simplificada 
                WHERE fecha_parto >= CURRENT_DATE - INTERVAL '6 months'
            """)
            pozas_activas = cur.fetchone()[0] or 0
            
            cur.execute("""
                SELECT COUNT(*) 
                FROM pozas 
                WHERE tipo = 'reproductora' AND estado = 'activo'
            """)
            total_pozas_reproductoras = cur.fetchone()[0] or 0
            
            if total_pozas_reproductoras > 0:
                porcentaje_activas = (pozas_activas / total_pozas_reproductoras) * 100
                if porcentaje_activas < 70:
                    recomendaciones.append({
                        'tipo': 'rotacion',
                        'titulo': '🔄 Rotar Reproductores',
                        'mensaje': f'Solo el {porcentaje_activas:.1f}% de tus pozas reproductoras están activas. Considera rotar animales.',
                        'icono': 'fas fa-recycle'
                    })
            
            cur.close()
            
        except Exception as e:
            print(f"Error generando recomendaciones: {e}")
        
        return recomendaciones