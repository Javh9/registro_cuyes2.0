from db.connection import get_db_connection
from datetime import datetime

class Gasto:
    TIPOS_GASTO = ['alimentacion', 'medicamentos', 'mantenimiento', 'mano_obra', 'transporte', 'otros']
    
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

    def obtener_gastos_recientes(self, limite=10):
        """Obtiene los gastos más recientes"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, fecha, tipo, descripcion, monto, proveedor, observaciones
                FROM gastos 
                ORDER BY fecha DESC, id DESC
                LIMIT %s
            """, (limite,))
            gastos = cur.fetchall()
            cur.close()
            return gastos
        except Exception as e:
            print(f"Error obteniendo gastos recientes: {e}")
            return []

    def obtener_resumen_mensual(self):
        """Obtiene resumen de gastos del mes actual por categoría"""
        if not self.db:
            return {}
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN tipo = 'alimentacion' THEN monto ELSE 0 END), 0) as alimentacion,
                    COALESCE(SUM(CASE WHEN tipo = 'medicamentos' THEN monto ELSE 0 END), 0) as medicamentos,
                    COALESCE(SUM(CASE WHEN tipo = 'mantenimiento' THEN monto ELSE 0 END), 0) as mantenimiento,
                    COALESCE(SUM(CASE WHEN tipo = 'mano_obra' THEN monto ELSE 0 END), 0) as mano_obra,
                    COALESCE(SUM(CASE WHEN tipo = 'transporte' THEN monto ELSE 0 END), 0) as transporte,
                    COALESCE(SUM(CASE WHEN tipo = 'otros' THEN monto ELSE 0 END), 0) as otros,
                    COALESCE(SUM(monto), 0) as total
                FROM gastos 
                WHERE EXTRACT(MONTH FROM fecha) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            resultado = cur.fetchone()
            cur.close()
            
            return {
                'alimentacion': float(resultado[0]) if resultado[0] else 0.0,
                'medicamentos': float(resultado[1]) if resultado[1] else 0.0,
                'mantenimiento': float(resultado[2]) if resultado[2] else 0.0,
                'mano_obra': float(resultado[3]) if resultado[3] else 0.0,
                'transporte': float(resultado[4]) if resultado[4] else 0.0,
                'otros': float(resultado[5]) if resultado[5] else 0.0,
                'total': float(resultado[6]) if resultado[6] else 0.0
            }
        except Exception as e:
            print(f"Error obteniendo resumen mensual: {e}")
            return {}

    def obtener_estadisticas_anuales(self, año=None):
        """Obtiene estadísticas de gastos por mes del año"""
        if not self.db:
            return []
        
        try:
            año_actual = año or datetime.now().year
            cur = self.db.cursor()
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM fecha) as mes,
                    SUM(monto) as total
                FROM gastos 
                WHERE EXTRACT(YEAR FROM fecha) = %s
                GROUP BY EXTRACT(MONTH FROM fecha)
                ORDER BY mes
            """, (año_actual,))
            estadisticas = cur.fetchall()
            cur.close()
            return estadisticas
        except Exception as e:
            print(f"Error obteniendo estadísticas anuales: {e}")
            return []