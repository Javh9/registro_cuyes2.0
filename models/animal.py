from db.connection import get_db_connection

class Animal:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT a.*, p.nombre as poza_nombre 
                FROM animales a 
                LEFT JOIN pozas p ON a.poza_id = p.id 
                ORDER BY a.id
            """)
            animales = cur.fetchall()
            cur.close()
            return animales
        except Exception as e:
            print(f"Error obteniendo animales: {e}")
            return []
    
    def crear(self, datos):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO animales 
                (codigo, sexo, fecha_nacimiento, estado, etapa_productiva, 
                 clasificacion, poza_id, madre_id, padre_id, peso_actual) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['codigo'],
                datos['sexo'],
                datos['fecha_nacimiento'],
                datos.get('estado', 'activo'),
                datos.get('etapa_productiva', 'destete'),
                datos.get('clasificacion'),
                datos.get('poza_id'),
                datos.get('madre_id'),
                datos.get('padre_id'),
                datos.get('peso_actual', 0)
            ))
            
            animal_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return animal_id
        except Exception as e:
            print(f"Error creando animal: {e}")
            self.db.rollback()
            return None
    
    def mover_poza(self, animal_id, nueva_poza_id, motivo):
        if not self.db:
            return False
        
        try:
            cur = self.db.cursor()
            
            # Obtener poza actual
            cur.execute("SELECT poza_id FROM animales WHERE id = %s", (animal_id,))
            resultado = cur.fetchone()
            if not resultado:
                return False
                
            poza_actual_id = resultado[0]
            
            # Actualizar poza del animal
            cur.execute("""
                UPDATE animales 
                SET poza_id = %s, fecha_actualizacion = NOW()
                WHERE id = %s
            """, (nueva_poza_id, animal_id))
            
            # Registrar movimiento
            cur.execute("""
                INSERT INTO movimientos_animales 
                (animal_id, desde_poza_id, hacia_poza_id, motivo)
                VALUES (%s, %s, %s, %s)
            """, (animal_id, poza_actual_id, nueva_poza_id, motivo))
            
            self.db.commit()
            cur.close()
            return True
            
        except Exception as e:
            print(f"Error moviendo animal: {e}")
            self.db.rollback()
            return False
    
    def obtener_por_etapa(self, etapa):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT a.*, p.nombre as poza_nombre 
                FROM animales a 
                LEFT JOIN pozas p ON a.poza_id = p.id 
                WHERE a.etapa_productiva = %s
                ORDER BY a.id
            """, (etapa,))
            animales = cur.fetchall()
            cur.close()
            return animales
        except Exception as e:
            print(f"Error obteniendo animales por etapa: {e}")
            return []