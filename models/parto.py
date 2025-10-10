from db.connection import get_db_connection
from models.animal import Animal

class Parto:
    def __init__(self):
        self.db = get_db_connection()
    
    def obtener_todos(self):
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT p.*, a.codigo as hembra_codigo, poza.nombre as poza_nombre
                FROM partos p
                LEFT JOIN animales a ON p.hembra_id = a.id
                LEFT JOIN pozas poza ON p.poza_id = poza.id
                ORDER BY p.fecha_parto DESC
            """)
            partos = cur.fetchall()
            cur.close()
            return partos
        except Exception as e:
            print(f"Error obteniendo partos: {e}")
            return []
    
    def registrar(self, datos):
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            
            # 1. Registrar el parto
            cur.execute("""
                INSERT INTO partos 
                (hembra_id, poza_id, fecha_parto, machos_nacidos, 
                 hembras_nacidas, muertos_nacimiento, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['hembra_id'],
                datos['poza_id'],
                datos['fecha_parto'],
                datos.get('machos_nacidos', 0),
                datos.get('hembras_nacidas', 0),
                datos.get('muertos_nacimiento', 0),
                datos.get('observaciones', '')
            ))
            
            parto_id = cur.fetchone()[0]
            
            # 2. Crear automáticamente los animales nacidos
            animal_model = Animal()
            total_nacidos = datos.get('machos_nacidos', 0) + datos.get('hembras_nacidas', 0)
            
            if total_nacidos > 0:
                # Crear machos
                for i in range(datos.get('machos_nacidos', 0)):
                    codigo = f"N{parto_id}M{i+1}"
                    animal_model.crear({
                        'codigo': codigo,
                        'sexo': 'macho',
                        'fecha_nacimiento': datos['fecha_parto'],
                        'etapa_productiva': 'lactancia',
                        'poza_id': datos['poza_id'],
                        'madre_id': datos['hembra_id']
                    })
                
                # Crear hembras
                for i in range(datos.get('hembras_nacidas', 0)):
                    codigo = f"N{parto_id}H{i+1}"
                    animal_model.crear({
                        'codigo': codigo,
                        'sexo': 'hembra',
                        'fecha_nacimiento': datos['fecha_parto'],
                        'etapa_productiva': 'lactancia',
                        'poza_id': datos['poza_id'],
                        'madre_id': datos['hembra_id']
                    })
            
            self.db.commit()
            cur.close()
            return parto_id
            
        except Exception as e:
            print(f"Error registrando parto: {e}")
            self.db.rollback()
            return None