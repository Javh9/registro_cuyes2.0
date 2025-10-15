from db.connection import get_db_connection

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
    
    def obtener_ventas_recientes(self):
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
                LIMIT 20
            """)
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