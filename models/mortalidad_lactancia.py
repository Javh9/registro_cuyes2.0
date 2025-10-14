from db.connection import get_db_connection

class MortalidadLactancia:
    def __init__(self):
        self.db = get_db_connection()
    
    def registrar(self, datos):
        """Registrar mortalidad en lactancia"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO mortalidad_lactancia 
                (galpon_id, poza_id, fecha, cantidad, causa, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['galpon_id'],
                datos['poza_id'],
                datos['fecha'],
                datos['cantidad'],
                datos['causa'],
                datos['observaciones']
            ))
            mortalidad_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return mortalidad_id
        except Exception as e:
            print(f"Error registrando mortalidad lactancia: {e}")
            self.db.rollback()
            return None
    
    def obtener_por_galpon(self, galpon_id):
        """Obtener mortalidad por galpón"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT ml.id, g.nombre as galpon, p.nombre as poza, 
                       ml.fecha, ml.cantidad, ml.causa, ml.observaciones
                FROM mortalidad_lactancia ml
                JOIN galpones g ON ml.galpon_id = g.id
                JOIN pozas p ON ml.poza_id = p.id
                WHERE ml.galpon_id = %s
                ORDER BY ml.fecha DESC
            """, (galpon_id,))
            registros = cur.fetchall()
            cur.close()
            return registros
        except Exception as e:
            print(f"Error obteniendo mortalidad: {e}")
            return []
    
    def obtener_total_mortalidad_mes(self):
        """Obtener total de mortalidad del mes actual"""
        if not self.db:
            return 0
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT SUM(cantidad) 
                FROM mortalidad_lactancia 
                WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            total = cur.fetchone()[0]
            cur.close()
            return total if total else 0
        except Exception as e:
            print(f"Error obteniendo total mortalidad: {e}")
            return 0