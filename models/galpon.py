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
    
    def obtener_por_id(self, galpon_id):
        """Obtener un galpón por su ID"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM galpones WHERE id = %s", (galpon_id,))
            galpon = cur.fetchone()
            cur.close()
            return galpon
        except Exception as e:
            print(f"Error obteniendo galpón: {e}")
            return None
    
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
                datos.get('estado', 'activo')
            ))
            galpon_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return galpon_id
        except Exception as e:
            print(f"Error creando galpón: {e}")
            self.db.rollback()
            return None
    
    def actualizar(self, galpon_id, datos):
        """Actualizar un galpón existente"""
        if not self.db:
            return False
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE galpones 
                SET nombre = %s, capacidad = %s, ubicacion = %s, estado = %s
                WHERE id = %s
            """, (
                datos['nombre'],
                datos['capacidad'],
                datos['ubicacion'],
                datos.get('estado', 'activo'),
                galpon_id
            ))
            self.db.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error actualizando galpón: {e}")
            self.db.rollback()
            return False
    
    def eliminar(self, galpon_id):
        """Eliminar un galpón"""
        if not self.db:
            return False
        
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM galpones WHERE id = %s", (galpon_id,))
            self.db.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error eliminando galpón: {e}")
            self.db.rollback()
            return False