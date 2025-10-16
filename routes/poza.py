# models/poza.py
from db.connection import get_db_connection

class Poza:
    def obtener_todos(self):
        """Obtener todas las pozas"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pozas ORDER BY nombre')
            pozas = cursor.fetchall()
            conn.close()
            return pozas
        except Exception as e:
            print(f"❌ Error en Poza.obtener_todos: {e}")
            return []
    
    def obtener_por_galpon(self, galpon_id):
        """Obtener pozas por galpón"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nombre, tipo 
                FROM pozas 
                WHERE galpon_id = %s 
                ORDER BY nombre
            ''', (galpon_id,))
            pozas = cursor.fetchall()
            conn.close()
            return pozas
        except Exception as e:
            print(f"❌ Error en Poza.obtener_por_galpon: {e}")
            return []
    
    def obtener_pozas_con_lactantes(self, galpon_id):
        """Obtener pozas que pueden tener lactantes (pozas reproductoras)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, tipo 
                FROM pozas 
                WHERE galpon_id = %s AND tipo = 'reproductora'
                ORDER BY nombre
            ''', (galpon_id,))
            
            pozas = cursor.fetchall()
            conn.close()
            
            print(f"🔍 DEBUG Poza: Encontradas {len(pozas)} pozas reproductoras para galpón {galpon_id}")
            return pozas
            
        except Exception as e:
            print(f"❌ Error en Poza.obtener_pozas_con_lactantes: {e}")
            return []
    
    def obtener_por_id(self, id):
        """Obtener una poza por ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM pozas WHERE id = %s', (id,))
            poza = cursor.fetchone()
            conn.close()
            return poza
        except Exception as e:
            print(f"❌ Error en Poza.obtener_por_id: {e}")
            return None
    
    def crear(self, datos):
        """Crear una nueva poza"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pozas (nombre, tipo, capacidad, galpon_id, estado)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                datos['nombre'],
                datos['tipo'],
                int(datos['capacidad']),
                int(datos['galpon_id']),
                datos.get('estado', 'activo')
            ))
            poza_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return poza_id
        except Exception as e:
            print(f"❌ Error en Poza.crear: {e}")
            return None
    
    def actualizar(self, id, datos):
        """Actualizar una poza existente"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE pozas 
                SET nombre = %s, tipo = %s, capacidad = %s, galpon_id = %s, estado = %s
                WHERE id = %s
            ''', (
                datos['nombre'],
                datos['tipo'],
                int(datos['capacidad']),
                int(datos['galpon_id']),
                datos.get('estado', 'activo'),
                id
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error en Poza.actualizar: {e}")
            return False