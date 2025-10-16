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
        """Obtiene pozas que pueden tener lactantes"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            # Buscar pozas de tipo lactancia y reproductoras
            cur.execute("""
                SELECT id, nombre, tipo 
                FROM pozas 
                WHERE galpon_id = %s 
                AND estado = 'activo'
                AND tipo IN ('lactancia', 'reproductora')
                ORDER BY nombre
            """, (galpon_id,))
            
            pozas = cur.fetchall()
            
            # Si no hay resultados, mostrar todas las pozas del galpón
            if not pozas:
                pozas = self.obtener_por_galpon(galpon_id)
            
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas con lactantes: {e}")
            # Fallback a método general
            return self.obtener_por_galpon(galpon_id)