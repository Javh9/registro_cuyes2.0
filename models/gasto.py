from db.connection import get_db_connection

class Gasto:
    TIPOS_GASTO = ['alimentacion', 'medicamentos', 'mantenimiento', 'mano_obra', 'otros']
    
    def __init__(self):
        self.db = get_db_connection()
    
    def registrar(self, datos):
        """Registrar gasto"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO gastos 
                (fecha, tipo, descripcion, monto, proveedor, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['fecha'],
                datos['tipo'],
                datos['descripcion'],
                datos['monto'],
                datos['proveedor'],
                datos['observaciones']
            ))
            gasto_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return gasto_id
        except Exception as e:
            print(f"Error registrando gasto: {e}")
            self.db.rollback()
            return None
    
    def obtener_por_mes(self, año, mes):
        """Obtener gastos por mes"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT tipo, SUM(monto) as total
                FROM gastos
                WHERE EXTRACT(YEAR FROM fecha) = %s 
                AND EXTRACT(MONTH FROM fecha) = %s
                GROUP BY tipo
            """, (año, mes))
            gastos = cur.fetchall()
            cur.close()
            return gastos
        except Exception as e:
            print(f"Error obteniendo gastos: {e}")
            return []
    
    def obtener_total_mes_actual(self):
        """Obtener total de gastos del mes actual"""
        if not self.db:
            return 0
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT SUM(monto) 
                FROM gastos 
                WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            total = cur.fetchone()[0]
            cur.close()
            return total if total else 0
        except Exception as e:
            print(f"Error obteniendo total gastos: {e}")
            return 0