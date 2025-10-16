# models/poza.py
from db.connection import get_db_connection

class Poza:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_por_galpon(self, galpon_id):
        """Obtiene todas las pozas de un galpón"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, nombre, tipo, capacidad, estado 
                FROM pozas 
                WHERE galpon_id = %s AND estado = 'activo'
                ORDER BY nombre
            """, (galpon_id,))
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas por galpón: {e}")
            return []
    
    def obtener_pozas_con_lactantes(self, galpon_id):
        """Obtiene pozas que tienen lactantes (pozAs reproductoras con crías)"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            # Buscar pozas reproductoras que tengan partos recientes
            cur.execute("""
                SELECT DISTINCT p.id, p.nombre, p.tipo
                FROM pozas p
                LEFT JOIN partos pt ON p.id = pt.poza_id
                WHERE p.galpon_id = %s 
                AND p.estado = 'activo'
                AND p.tipo IN ('reproductora', 'lactantes')
                AND (pt.fecha_parto >= DATE('now', '-30 days') OR pt.id IS NOT NULL)
                ORDER BY p.nombre
            """, (galpon_id,))
            
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas con lactantes: {e}")
            return []