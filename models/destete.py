from db.connection import get_db_connection

class Destete:
    def __init__(self):
        self.db = get_db_connection()
    
    def registrar(self, datos):
        """Registrar destete individual por poza"""
        if not self.db:
            return None
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO destetes_simplificada 
                (galpon_id, poza_origen_id, fecha_destete, machos_destetados, hembras_destetadas,
                 reemplazo_machos, reemplazo_hembras, engorde_machos, engorde_hembras,
                 venta_directa_machos, venta_directa_hembras, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                datos['galpon_id'],
                datos['poza_origen_id'],
                datos['fecha_destete'],
                datos.get('machos_destetados', 0),
                datos.get('hembras_destetadas', 0),
                datos.get('reemplazo_machos', 0),
                datos.get('reemplazo_hembras', 0),
                datos.get('engorde_machos', 0),
                datos.get('engorde_hembras', 0),
                datos.get('venta_directa_machos', 0),
                datos.get('venta_directa_hembras', 0),
                datos['observaciones']
            ))
            destete_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return destete_id
        except Exception as e:
            print(f"Error registrando destete: {e}")
            self.db.rollback()
            return None