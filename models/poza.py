from db.connection import get_db_connection

class Poza:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_por_galpon(self, galpon_id):
        """Obtener todas las pozas de un galpón específico"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id, nombre FROM pozas WHERE galpon_id = %s", (galpon_id,))
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas por galpón: {e}")
            return []
    
    def crear(self, datos):
        """Crear una nueva poza"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO pozas (nombre, tipo, capacidad, galpon_id, estado)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['nombre'],
                datos['tipo'],
                datos['capacidad'],
                datos['galpon_id'],
                datos.get('estado', 'activo')
            ))
            poza_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return poza_id
        except Exception as e:
            print(f"Error creando poza: {e}")
            self.db.rollback()
            return None
    
    def obtener_todas(self):
        """Obtener todas las pozas"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id, nombre, galpon_id FROM pozas ORDER BY galpon_id, nombre")
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo todas las pozas: {e}")
            return []