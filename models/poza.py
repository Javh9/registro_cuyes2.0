from db.connection import get_db_connection

class Poza:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_por_galpon(self, galpon_id):
        """Obtener todas las pozas de un galpón"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, nombre, tipo, capacidad, estado 
                FROM pozas 
                WHERE galpon_id = %s AND estado = 'activo'
                ORDER BY nombre
            """, (galpon_id,))
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas: {e}")
            return []
    
    def obtener_pozas_con_lactantes(self, galpon_id):
        """Obtener pozas que tienen lactantes (partos recientes)"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT DISTINCT p.id, p.nombre, p.tipo
                FROM pozas p
                JOIN partos_simplificada pt ON p.id = pt.poza_id
                WHERE p.galpon_id = %s 
                AND pt.fecha_parto >= CURRENT_DATE - INTERVAL '21 days'
                AND p.estado = 'activo'
                ORDER BY p.nombre
            """, (galpon_id,))
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas con lactantes: {e}")
            return []
    
    def crear(self, datos):
        """Crear una nueva poza"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO pozas (nombre, tipo, capacidad, galpon_id, estado)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['nombre'],
                datos['tipo'],
                datos['capacidad'],
                datos['galpon_id'],
                datos.get('estado', 'activo')
            ))
            poza_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return poza_id
        except Exception as e:
            print(f"Error creando poza: {e}")
            self.db.rollback()
            return None
    
    def actualizar(self, poza_id, datos):
        """Actualizar una poza existente"""
        if not self.db:
            return False
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE pozas 
                SET nombre = %s, tipo = %s, capacidad = %s, galpon_id = %s, estado = %s
                WHERE id = %s
            """, (
                datos['nombre'],
                datos['tipo'],
                datos['capacidad'],
                datos['galpon_id'],
                datos.get('estado', 'activo'),
                poza_id
            ))
            self.db.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error actualizando poza: {e}")
            self.db.rollback()
            return False
    
    def obtener_por_id(self, poza_id):
        """Obtener una poza por su ID"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM pozas WHERE id = %s", (poza_id,))
            poza = cur.fetchone()
            cur.close()
            return poza
        except Exception as e:
            print(f"Error obteniendo poza: {e}")
            return None