from db.connection import get_db_connection

class Parto:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_ultimo_parto(self, poza_id):
        """Obtener el número del último parto de una poza"""
        if not self.db:
            return 0
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT COALESCE(MAX(numero_parto), 0) 
                FROM partos_simplificada 
                WHERE poza_id = %s
            """, (poza_id,))
            ultimo_parto = cur.fetchone()[0]
            cur.close()
            return ultimo_parto
        except Exception as e:
            print(f"Error obteniendo último parto: {e}")
            return 0
    
    def registrar(self, datos):
        """Registrar un nuevo parto"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO partos_simplificada 
                (galpon_id, poza_id, fecha_parto, nacidos_vivos, muertos_nacimiento, numero_parto, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['galpon_id'],
                datos['poza_id'],
                datos['fecha_parto'],
                datos['nacidos_vivos'],
                datos['muertos_nacimiento'],
                datos['numero_parto'],
                datos['observaciones']
            ))
            parto_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return parto_id
        except Exception as e:
            print(f"Error registrando parto: {e}")
            self.db.rollback()
            return None