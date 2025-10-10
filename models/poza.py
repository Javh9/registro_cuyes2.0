from db.connection import get_db_connection

class Poza:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT p.*, g.nombre as galpon_nombre 
                FROM pozas p 
                LEFT JOIN galpones g ON p.galpon_id = g.id 
                ORDER BY p.id
            """)
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas: {e}")
            return []
    
    def crear(self, datos):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO pozas (galpon_id, tipo, nombre, capacidad) 
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (
                datos['galpon_id'],
                datos['tipo'],
                datos['nombre'],
                datos['capacidad']
            ))
            
            poza_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return poza_id
        except Exception as e:
            print(f"Error creando poza: {e}")
            self.db.rollback()
            return None
    
    def obtener_por_id(self, id):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM pozas WHERE id = %s", (id,))
            poza = cur.fetchone()
            cur.close()
            return poza
        except Exception as e:
            print(f"Error obteniendo poza: {e}")
            return None
    
    def obtener_por_tipo(self, tipo):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM pozas WHERE tipo = %s", (tipo,))
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas por tipo: {e}")
            return []