from db.connection import get_db_connection

class Galpon:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        """Obtener todos los galpones"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id, nombre, capacidad, ubicacion, estado FROM galpones ORDER BY id")
            galpones = cur.fetchall()
            cur.close()
            return galpones
        except Exception as e:
            print(f"Error obteniendo galpones: {e}")
            return []
    
    def crear(self, datos):
        """Crear un nuevo galpón"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO galpones (nombre, capacidad, ubicacion, estado)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                datos['nombre'],
                datos['capacidad'],
                datos['ubicacion'],
                datos['estado']
            ))
            galpon_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return galpon_id
        except Exception as e:
            print(f"Error creando galpón: {e}")
            self.db.rollback()
            return None