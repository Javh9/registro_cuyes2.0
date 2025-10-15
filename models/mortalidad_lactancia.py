from db.connection import get_db_connection
from datetime import datetime

class MortalidadLactancia:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_causas_mortalidad(self):
        """Retorna las causas de mortalidad disponibles"""
        return [
            {'value': 'natural', 'label': 'Muerte Natural'},
            {'value': 'enfermedad', 'label': 'Enfermedad'},
            {'value': 'accidente', 'label': 'Accidente'},
            {'value': 'desconocida', 'label': 'Causa Desconocida'},
            {'value': 'otra', 'label': 'Otra'}
        ]
    
    def registrar(self, datos):
        """Registra una nueva mortalidad en lactancia"""
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
                datos.get('observaciones', '')
            ))
            mortalidad_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return mortalidad_id
        except Exception as e:
            print(f"Error registrando mortalidad lactancia: {e}")
            self.db.rollback()
            return None
    
    def obtener_recientes(self, limite=10):
        """Obtiene los registros recientes de mortalidad"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT ml.id, ml.fecha, ml.cantidad, ml.causa, ml.observaciones,
                       g.nombre as galpon_nombre, p.nombre as poza_nombre
                FROM mortalidad_lactancia ml
                LEFT JOIN galpones g ON ml.galpon_id = g.id
                LEFT JOIN pozas p ON ml.poza_id = p.id
                ORDER BY ml.fecha DESC, ml.id DESC
                LIMIT %s
            """, (limite,))
            registros = cur.fetchall()
            cur.close()
            return registros
        except Exception as e:
            print(f"Error obteniendo mortalidad reciente: {e}")
            return []
    
    def obtener_por_rango_fechas(self, fecha_inicio, fecha_fin):
        """Obtiene mortalidad por rango de fechas para estadísticas"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT fecha, SUM(cantidad) as total_muertes
                FROM mortalidad_lactancia
                WHERE fecha BETWEEN %s AND %s
                GROUP BY fecha
                ORDER BY fecha
            """, (fecha_inicio, fecha_fin))
            datos = cur.fetchall()
            cur.close()
            return datos
        except Exception as e:
            print(f"Error obteniendo mortalidad por rango: {e}")
            return []