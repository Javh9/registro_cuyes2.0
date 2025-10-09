from db.connection import get_db_connection

class Galpon:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        conn = self.db
        cur = conn.cursor()
        cur.execute("SELECT * FROM galpones ORDER BY id")
        galpones = cur.fetchall()
        cur.close()
        return galpones
    
    def crear(self, datos_galpon):
        conn = self.db
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO galpones (nombre, capacidad, ubicacion, estado, fecha_creacion)
                    VALUES (%s, %s, %s, %s, NOW())
                    RETURNING id
                """, (
                    datos_galpon['nombre'],
                    datos_galpon['capacidad'],
                    datos_galpon.get('ubicacion', ''),
                    datos_galpon.get('estado', 'activo')
                ))
                galpon_id = cur.fetchone()[0]
                conn.commit()
                return galpon_id
        except Exception as e:
            conn.rollback()
            raise e
    
    def obtener_por_id(self, id):
        conn = self.db
        cur = conn.cursor()
        cur.execute("SELECT * FROM galpones WHERE id = %s", (id,))
        galpon = cur.fetchone()
        cur.close()
        return galpon
    
    def actualizar(self, id, datos_galpon):
        conn = self.db
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE galpones 
                    SET nombre = %s, capacidad = %s, ubicacion = %s, estado = %s
                    WHERE id = %s
                """, (
                    datos_galpon['nombre'],
                    datos_galpon['capacidad'],
                    datos_galpon.get('ubicacion', ''),
                    datos_galpon.get('estado', 'activo'),
                    id
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
    
    def eliminar(self, id):
        conn = self.db
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM galpones WHERE id = %s", (id,))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e