from db.connection import get_db_connection
from datetime import datetime, timedelta

class Dashboard:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_estadisticas(self):
        """Obtener estadísticas completas para el dashboard"""
        if not self.db:
            return self._estadisticas_vacias()
        
        try:
            cur = self.db.cursor()
            
            # 1. Total animales (estimado basado en partos y destetes recientes)
            cur.execute("""
                SELECT 
                    (SELECT COALESCE(SUM(nacidos_vivos), 0) FROM partos_simplificada 
                     WHERE fecha_parto >= CURRENT_DATE - INTERVAL '6 months') +
                    (SELECT COALESCE(SUM(machos_destetados + hembras_destetadas), 0) FROM destetes_simplificada 
                     WHERE fecha_destete >= CURRENT_DATE - INTERVAL '3 months')
                as total_animales
            """)
            total_animales = cur.fetchone()[0] or 0
            
            # 2. Partos este mes
            cur.execute("""
                SELECT COUNT(*) FROM partos_simplificada 
                WHERE EXTRACT(MONTH FROM fecha_parto) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_parto) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            partos_mes = cur.fetchone()[0] or 0
            
            # 3. Mortalidad este mes
            cur.execute("""
                SELECT COALESCE(SUM(cantidad), 0) FROM mortalidad_lactancia 
                WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            mortalidad_mes = cur.fetchone()[0] or 0
            
            # 4. Destetes este mes
            cur.execute("""
                SELECT COUNT(*) FROM destetes_simplificada 
                WHERE EXTRACT(MONTH FROM fecha_destete) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_destete) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            destetes_mes = cur.fetchone()[0] or 0
            
            # 5. Ventas este mes
            cur.execute("""
                SELECT COALESCE(SUM(total), 0) FROM ventas 
                WHERE EXTRACT(MONTH FROM fecha_venta) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_venta) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            ventas_mes = float(cur.fetchone()[0] or 0)
            
            # 6. Gastos este mes
            cur.execute("""
                SELECT COALESCE(SUM(monto), 0) FROM gastos 
                WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            gastos_mes = float(cur.fetchone()[0] or 0)
            
            # 7. Últimos partos (para alertas)
            cur.execute("""
                SELECT p.fecha_parto, g.nombre, po.nombre, p.nacidos_vivos
                FROM partos_simplificada p
                JOIN galpones g ON p.galpon_id = g.id
                JOIN pozas po ON p.poza_id = po.id
                ORDER BY p.fecha_parto DESC
                LIMIT 5
            """)
            ultimos_partos = cur.fetchall()
            
            # 8. Alertas de mortalidad
            cur.execute("""
                SELECT ml.fecha, g.nombre, ml.cantidad, ml.causa
                FROM mortalidad_lactancia ml
                JOIN galpones g ON ml.galpon_id = g.id
                WHERE ml.fecha >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY ml.fecha DESC
                LIMIT 5
            """)
            alertas_mortalidad = cur.fetchall()
            
            cur.close()
            
            return {
                'total_animales': total_animales,
                'partos_mes': partos_mes,
                'mortalidad_mes': mortalidad_mes,
                'destetes_mes': destetes_mes,
                'ventas_mes': ventas_mes,
                'gastos_mes': gastos_mes,
                'balance_mes': ventas_mes - gastos_mes,
                'ultimos_partos': [
                    {
                        'fecha': parto[0].strftime('%d/%m/%Y'),
                        'galpon': parto[1],
                        'poza': parto[2],
                        'nacidos': parto[3]
                    } for parto in ultimos_partos
                ],
                'alertas_mortalidad': [
                    {
                        'fecha': alerta[0].strftime('%d/%m/%Y'),
                        'galpon': alerta[1],
                        'cantidad': alerta[2],
                        'causa': alerta[3]
                    } for alerta in alertas_mortalidad
                ]
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas dashboard: {e}")
            return self._estadisticas_vacias()
    
    def obtener_tendencias_mensuales(self):
        """Obtener datos para gráficos de tendencias"""
        if not self.db:
            return {}
        
        try:
            cur = self.db.cursor()
            
            # Partos últimos 6 meses
            cur.execute("""
                SELECT 
                    EXTRACT(YEAR FROM fecha_parto) as año,
                    EXTRACT(MONTH FROM fecha_parto) as mes,
                    COUNT(*) as total
                FROM partos_simplificada 
                WHERE fecha_parto >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY año, mes
                ORDER BY año, mes
            """)
            partos_mensuales = cur.fetchall()
            
            # Ventas últimos 6 meses
            cur.execute("""
                SELECT 
                    EXTRACT(YEAR FROM fecha_venta) as año,
                    EXTRACT(MONTH FROM fecha_venta) as mes,
                    SUM(total) as total
                FROM ventas 
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY año, mes
                ORDER BY año, mes
            """)
            ventas_mensuales = cur.fetchall()
            
            cur.close()
            
            return {
                'partos_mensuales': [
                    {'mes': f"{int(row[1])}/{int(row[0])}", 'total': row[2]} 
                    for row in partos_mensuales
                ],
                'ventas_mensuales': [
                    {'mes': f"{int(row[1])}/{int(row[0])}", 'total': float(row[2] or 0)} 
                    for row in ventas_mensuales
                ]
            }
            
        except Exception as e:
            print(f"Error obteniendo tendencias: {e}")
            return {}
    
    def _estadisticas_vacias(self):
        """Retornar estadísticas vacías en caso de error"""
        return {
            'total_animales': 0,
            'partos_mes': 0,
            'mortalidad_mes': 0,
            'destetes_mes': 0,
            'ventas_mes': 0,
            'gastos_mes': 0,
            'balance_mes': 0,
            'ultimos_partos': [],
            'alertas_mortalidad': []
        }