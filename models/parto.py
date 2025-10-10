from db.connection import get_db_connection
from datetime import datetime

class Parto:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT p.*, g.nombre as galpon_nombre, po.nombre as poza_nombre
                FROM partos_simplificada p
                LEFT JOIN galpones g ON p.galpon_id = g.id
                LEFT JOIN pozas po ON p.poza_id = po.id
                ORDER BY p.fecha_parto DESC
            """)
            partos = cur.fetchall()
            cur.close()
            return partos
        except Exception as e:
            print(f"Error obteniendo partos: {e}")
            return []
    
    def obtener_ultimo_parto(self, poza_id):
        """Obtener el último parto de una poza para sugerir número"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT numero_parto FROM partos_simplificada 
                WHERE poza_id = %s 
                ORDER BY fecha_parto DESC 
                LIMIT 1
            """, (poza_id,))
            resultado = cur.fetchone()
            cur.close()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Error obteniendo último parto: {e}")
            return 0
    
    def registrar(self, datos):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO partos_simplificada 
                (galpon_id, poza_id, fecha_parto, nacidos_vivos, 
                 muertos_nacimiento, numero_parto, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['galpon_id'],
                datos['poza_id'], 
                datos['fecha_parto'],
                datos['nacidos_vivos'],
                datos['muertos_nacimiento'],
                datos['numero_parto'],
                datos.get('observaciones', '')
            ))
            parto_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return parto_id
        except Exception as e:
            print(f"Error registrando parto: {e}")
            self.db.rollback()
            return None