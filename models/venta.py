from db.connection import get_db_connection
from datetime import datetime

class Venta:
    def __init__(self):
        self.db = get_db_connection()
    
    def registrar(self, datos):
        """Registrar una venta"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO ventas 
                (fecha_venta, cliente, tipo_producto, cantidad, precio_unitario, total, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['fecha_venta'],
                datos['cliente'],
                datos['tipo_producto'],
                datos['cantidad'],
                datos['precio_unitario'],
                datos['total'],
                datos['observaciones']
            ))
            venta_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return venta_id
        except Exception as e:
            print(f"Error registrando venta: {e}")
            self.db.rollback()
            return None
    
    def obtener_ventas_recientes(self, limite=10):
        """Obtener ventas recientes"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, fecha_venta, cliente, tipo_producto, cantidad, 
                       precio_unitario, total, observaciones
                FROM ventas 
                ORDER BY fecha_venta DESC, id DESC
                LIMIT %s
            """, (limite,))
            ventas = cur.fetchall()
            cur.close()
            return ventas
        except Exception as e:
            print(f"Error obteniendo ventas: {e}")
            return []
    
    def obtener_total_ventas_mes(self):
        """Obtener total de ventas del mes actual"""
        if not self.db:
            return 0
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT COALESCE(SUM(total), 0) 
                FROM ventas 
                WHERE EXTRACT(MONTH FROM fecha_venta) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_venta) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            total = cur.fetchone()[0]
            cur.close()
            return float(total)
        except Exception as e:
            print(f"Error obteniendo total ventas: {e}")
            return 0.0
    
    def obtener_ventas_por_tipo(self, año, mes):
        """Obtener ventas agrupadas por tipo de producto"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT tipo_producto, SUM(cantidad) as total_cantidad, SUM(total) as total_ventas
                FROM ventas
                WHERE EXTRACT(YEAR FROM fecha_venta) = %s 
                AND EXTRACT(MONTH FROM fecha_venta) = %s
                GROUP BY tipo_producto
            """, (año, mes))
            ventas = cur.fetchall()
            cur.close()
            return ventas
        except Exception as e:
            print(f"Error obteniendo ventas por tipo: {e}")
            return []

    # AGREGAR ESTOS MÉTODOS NUEVOS:

    def obtener_estadisticas_completas(self):
        """Obtener estadísticas completas para el dashboard"""
        if not self.db:
            return {}
        
        try:
            cur = self.db.cursor()
            
            # Total ventas del mes
            cur.execute("""
                SELECT COALESCE(SUM(total), 0), COUNT(*)
                FROM ventas 
                WHERE EXTRACT(MONTH FROM fecha_venta) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_venta) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            ventas_mes = cur.fetchone()
            
            # Total general de ventas
            cur.execute("SELECT COUNT(*) FROM ventas")
            total_ventas = cur.fetchone()[0]
            
            # Clientes únicos
            cur.execute("SELECT COUNT(DISTINCT cliente) FROM ventas")
            total_clientes = cur.fetchone()[0]
            
            cur.close()
            
            ventas_mes_total = float(ventas_mes[0]) if ventas_mes[0] else 0.0
            ventas_mes_cantidad = ventas_mes[1] if ventas_mes[1] else 0
            promedio_venta = ventas_mes_total / ventas_mes_cantidad if ventas_mes_cantidad > 0 else 0.0
            
            return {
                'ventas_mes': ventas_mes_total,
                'total_ventas': total_ventas,
                'promedio_venta': promedio_venta,
                'total_clientes': total_clientes
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'ventas_mes': 0,
                'total_ventas': 0,
                'promedio_venta': 0,
                'total_clientes': 0
            }

    def obtener_mejores_clientes(self, limite=5):
        """Obtener los mejores clientes por volumen de compras"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT cliente, SUM(total) as total_compras, COUNT(*) as total_ventas
                FROM ventas
                GROUP BY cliente
                ORDER BY total_compras DESC
                LIMIT %s
            """, (limite,))
            clientes = cur.fetchall()
            cur.close()
            return clientes
        except Exception as e:
            print(f"Error obteniendo mejores clientes: {e}")
            return []

    def obtener_tendencias_mensuales(self, meses=6):
        """Obtener tendencias de ventas de los últimos meses"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT 
                    EXTRACT(YEAR FROM fecha_venta) as año,
                    EXTRACT(MONTH FROM fecha_venta) as mes,
                    SUM(total) as total_ventas,
                    COUNT(*) as cantidad_ventas
                FROM ventas
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '%s months'
                GROUP BY año, mes
                ORDER BY año, mes
            """, (meses,))
            tendencias = cur.fetchall()
            cur.close()
            return tendencias
        except Exception as e:
            print(f"Error obteniendo tendencias: {e}")
            return []