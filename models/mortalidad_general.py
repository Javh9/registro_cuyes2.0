from datetime import datetime
from db.connection import get_db_connection

class MortalidadGeneral:
    TIPOS_CUY = [
        'reproductor',
        'lactante', 
        'destete',
        'reemplazo',
        'engorde_destete',
        'engorde_descarte'
    ]
    
    def __init__(self, id=None, fecha=None, tipo_cuy=None, galpon_id=None, 
                 poza_id=None, cantidad=None, causa=None, observaciones=None, fecha_creacion=None):
        self.id = id
        self.fecha = fecha
        self.tipo_cuy = tipo_cuy
        self.galpon_id = galpon_id
        self.poza_id = poza_id
        self.cantidad = cantidad
        self.causa = causa
        self.observaciones = observaciones
        self.fecha_creacion = fecha_creacion
    
    def save(self):
        conn = get_db_connection()
        try:
            if self.id:
                # Actualizar registro existente
                query = """
                    UPDATE mortalidad_general 
                    SET fecha = %s, tipo_cuy = %s, galpon_id = %s, poza_id = %s, 
                        cantidad = %s, causa = %s, observaciones = %s
                    WHERE id = %s
                """
                params = (self.fecha, self.tipo_cuy, self.galpon_id, self.poza_id,
                         self.cantidad, self.causa, self.observaciones, self.id)
            else:
                # Insertar nuevo registro
                query = """
                    INSERT INTO mortalidad_general 
                    (fecha, tipo_cuy, galpon_id, poza_id, cantidad, causa, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                params = (self.fecha, self.tipo_cuy, self.galpon_id, self.poza_id,
                         self.cantidad, self.causa, self.observaciones)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if not self.id:
                self.id = cursor.fetchone()[0]
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error guardando mortalidad general: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT mg.*, g.nombre as galpon_nombre, p.nombre as poza_nombre
                FROM mortalidad_general mg
                JOIN galpones g ON mg.galpon_id = g.id
                JOIN pozas p ON mg.poza_id = p.id
                ORDER BY mg.fecha DESC
            """
            cursor.execute(query)
            
            # Convertir a lista de diccionarios para el frontend
            registros = cursor.fetchall()
            registros_list = []
            for registro in registros:
                registros_list.append({
                    'id': registro[0],
                    'fecha': registro[1].strftime('%d/%m/%Y') if registro[1] else '',
                    'tipo_cuy': registro[2],
                    'galpon_id': registro[3],
                    'poza_id': registro[4],
                    'cantidad': registro[5],
                    'causa': registro[6],
                    'observaciones': registro[7],
                    'galpon_nombre': registro[8],
                    'poza_nombre': registro[9]
                })
            
            return registros_list
            
        except Exception as e:
            print(f"Error obteniendo mortalidad general: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_id(id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM mortalidad_general WHERE id = %s"
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            
            if row:
                return MortalidadGeneral(*row)
            return None
        except Exception as e:
            print(f"Error obteniendo mortalidad por ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_tipo_and_fecha(tipo_cuy, fecha_inicio, fecha_fin):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT SUM(cantidad) as total_mortalidad
                FROM mortalidad_general 
                WHERE tipo_cuy = %s AND fecha BETWEEN %s AND %s
            """
            cursor.execute(query, (tipo_cuy, fecha_inicio, fecha_fin))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except Exception as e:
            print(f"Error obteniendo mortalidad por tipo y fecha: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
    
    def delete(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = "DELETE FROM mortalidad_general WHERE id = %s"
            cursor.execute(query, (self.id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error eliminando mortalidad: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    # MÉTODOS NUEVOS PARA COMPATIBILIDAD CON EL CONTROLADOR
    def obtener_todos(self):
        """Método de instancia para obtener todos los registros"""
        return self.get_all()

    def registrar(self, datos):
        """Método de instancia para registrar mortalidad"""
        try:
            # Crear una nueva instancia con los datos
            nueva_mortalidad = MortalidadGeneral(
                fecha=datos['fecha'],
                tipo_cuy=datos['tipo_cuy'],
                galpon_id=datos['galpon_id'],
                poza_id=datos['poza_id'],
                cantidad=datos['cantidad'],
                causa=datos['causa'],
                observaciones=datos.get('observaciones', '')
            )
            
            # Guardar en la base de datos
            if nueva_mortalidad.save():
                return nueva_mortalidad.id
            else:
                return False
                
        except Exception as e:
            print(f"Error en método registrar: {e}")
            return False

    @staticmethod
    def obtener_por_galpon(galpon_id):
        """Obtiene mortalidad por galpón"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT mg.*, g.nombre as galpon_nombre, p.nombre as poza_nombre
                FROM mortalidad_general mg
                JOIN galpones g ON mg.galpon_id = g.id
                JOIN pozas p ON mg.poza_id = p.id
                WHERE mg.galpon_id = %s
                ORDER BY mg.fecha DESC
            """
            cursor.execute(query, (galpon_id,))
            
            # Convertir a lista de diccionarios
            registros = cursor.fetchall()
            registros_list = []
            for registro in registros:
                registros_list.append({
                    'id': registro[0],
                    'fecha': registro[1].strftime('%d/%m/%Y') if registro[1] else '',
                    'tipo_cuy': registro[2],
                    'galpon_id': registro[3],
                    'poza_id': registro[4],
                    'cantidad': registro[5],
                    'causa': registro[6],
                    'observaciones': registro[7],
                    'galpon_nombre': registro[8],
                    'poza_nombre': registro[9]
                })
            
            return registros_list
            
        except Exception as e:
            print(f"Error obteniendo mortalidad por galpón: {e}")
            return []
        finally:
            cursor.close()
            conn.close()