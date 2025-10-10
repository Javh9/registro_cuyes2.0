from db.connection import get_db_connection

class Galpon:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM galpones ORDER BY id")
            galpones = cur.fetchall()
            cur.close()
            return galpones
        except Exception as e:
            print(f"Error obteniendo galpones: {e}")
            return []
    
    def crear(self, datos):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO galpones (nombre, capacidad, ubicacion) 
                VALUES (%s, %s, %s) RETURNING id
            """, (datos['nombre'], datos['capacidad'], datos['ubicacion']))
            
            galpon_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return galpon_id
        except Exception as e:
            print(f"Error creando galpón: {e}")
            self.db.rollback()
            return None
    
    def obtener_por_id(self, id):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM galpones WHERE id = %s", (id,))
            galpon = cur.fetchone()
            cur.close()
            return galpon
        except Exception as e:
            print(f"Error obteniendo galpón: {e}")
            return None