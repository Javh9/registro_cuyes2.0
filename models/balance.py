from db.connection import get_db_connection
from datetime import datetime, timedelta

class Balance:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_balance_mensual(self, año=None, mes=None):
        """Obtener balance mensual completo"""
        if not año or not mes:
            # Usar mes actual por defecto
            hoy = datetime.now()
            año = hoy.year
            mes = hoy.month
        
        try:
            cur = self.db.cursor()
            
            # 1. INGRESOS - Total ventas del mes
            cur.execute("""
                SELECT COALESCE(SUM(total), 0) 
                FROM ventas 
                WHERE EXTRACT(YEAR FROM fecha_venta) = %s 
                AND EXTRACT(MONTH FROM fecha_venta) = %s
            """, (año, mes))
            total_ventas = float(cur.fetchone()[0] or 0)
            
            # 2. GASTOS - Por categoría
            cur.execute("""
                SELECT tipo, COALESCE(SUM(monto), 0) as total
                FROM gastos
                WHERE EXTRACT(YEAR FROM fecha) = %s 
                AND EXTRACT(MONTH FROM fecha) = %s
                GROUP BY tipo
                ORDER BY total DESC
            """, (año, mes))
            gastos_por_tipo = cur.fetchall()
            
            # 3. Total gastos
            total_gastos = sum(gasto[1] for gasto in gastos_por_tipo)
            
            # 4. Cálculo de resultados
            resultado = total_ventas - total_gastos
            margen_porcentaje = (resultado / total_ventas * 100) if total_ventas > 0 else 0
            
            # 5. Detalle de ventas por tipo de producto
            cur.execute("""
                SELECT tipo_producto, SUM(cantidad) as total_cantidad, SUM(total) as total_ventas
                FROM ventas
                WHERE EXTRACT(YEAR FROM fecha_venta) = %s 
                AND EXTRACT(MONTH FROM fecha_venta) = %s
                GROUP BY tipo_producto
                ORDER BY total_ventas DESC
            """, (año, mes))
            ventas_por_tipo = cur.fetchall()
            
            cur.close()
            
            return {
                'año': año,
                'mes': mes,
                'total_ventas': total_ventas,
                'total_gastos': total_gastos,
                'resultado': resultado,
                'margen_porcentaje': margen_porcentaje,
                'gastos_por_tipo': [
                    {
                        'tipo': gasto[0],
                        'total': float(gasto[1]),
                        'porcentaje': (gasto[1] / total_gastos * 100) if total_gastos > 0 else 0
                    }
                    for gasto in gastos_por_tipo
                ],
                'ventas_por_tipo': [
                    {
                        'tipo_producto': venta[0],
                        'total_cantidad': venta[1],
                        'total_ventas': float(venta[2]),
                        'porcentaje': (venta[2] / total_ventas * 100) if total_ventas > 0 else 0
                    }
                    for venta in ventas_por_tipo
                ]
            }
            
        except Exception as e:
            print(f"Error obteniendo balance mensual: {e}")
            return self._balance_vacio(año, mes)
    
    def obtener_historico_mensual(self, meses=6):
        """Obtener histórico de los últimos meses"""
        try:
            cur = self.db.cursor()
            
            historico = []
            hoy = datetime.now()
            
            for i in range(meses):
                # Calcular mes objetivo
                fecha_obj = hoy - timedelta(days=30*i)
                año = fecha_obj.year
                mes = fecha_obj.month
                
                balance = self.obtener_balance_mensual(año, mes)
                historico.append(balance)
            
            cur.close()
            return historico
            
        except Exception as e:
            print(f"Error obteniendo histórico: {e}")
            return []
    
    def obtener_metricas_rentabilidad(self):
        """Obtener métricas clave de rentabilidad"""
        try:
            cur = self.db.cursor()
            
            # Ventas últimos 12 meses
            cur.execute("""
                SELECT COALESCE(SUM(total), 0) 
                FROM ventas 
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '12 months'
            """)
            ventas_12_meses = float(cur.fetchone()[0] or 0)
            
            # Gastos últimos 12 meses
            cur.execute("""
                SELECT COALESCE(SUM(monto), 0) 
                FROM gastos 
                WHERE fecha >= CURRENT_DATE - INTERVAL '12 months'
            """)
            gastos_12_meses = float(cur.fetchone()[0] or 0)
            
            # Total animales vendidos
            cur.execute("""
                SELECT COALESCE(SUM(cantidad), 0) 
                FROM ventas 
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '12 months'
            """)
            animales_vendidos = cur.fetchone()[0] or 0
            
            # Cálculo de métricas
            resultado_12_meses = ventas_12_meses - gastos_12_meses
            margen_anual = (resultado_12_meses / ventas_12_meses * 100) if ventas_12_meses > 0 else 0
            costo_por_animal = (gastos_12_meses / animales_vendidos) if animales_vendidos > 0 else 0
            precio_promedio_venta = (ventas_12_meses / animales_vendidos) if animales_vendidos > 0 else 0
            
            cur.close()
            
            return {
                'ventas_12_meses': ventas_12_meses,
                'gastos_12_meses': gastos_12_meses,
                'resultado_12_meses': resultado_12_meses,
                'margen_anual': margen_anual,
                'animales_vendidos': animales_vendidos,
                'costo_por_animal': costo_por_animal,
                'precio_promedio_venta': precio_promedio_venta
            }
            
        except Exception as e:
            print(f"Error obteniendo métricas rentabilidad: {e}")
            return self._metricas_vacias()
    
    def _balance_vacio(self, año, mes):
        """Retornar balance vacío en caso de error"""
        return {
            'año': año,
            'mes': mes,
            'total_ventas': 0,
            'total_gastos': 0,
            'resultado': 0,
            'margen_porcentaje': 0,
            'gastos_por_tipo': [],
            'ventas_por_tipo': []
        }
    
    def _metricas_vacias(self):
        """Retornar métricas vacías en caso de error"""
        return {
            'ventas_12_meses': 0,
            'gastos_12_meses': 0,
            'resultado_12_meses': 0,
            'margen_anual': 0,
            'animales_vendidos': 0,
            'costo_por_animal': 0,
            'precio_promedio_venta': 0
        }