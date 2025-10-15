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
                datos.get('observaciones', '')
            ))
            destete_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()
            return destete_id
        except Exception as e:
            print(f"Error registrando destete: {e}")
            self.db.rollback()
            return None

    def obtener_pozas_con_crias_destetar(self, galpon_id):
        """Obtiene pozas que tienen crías listas para destetar (partos recientes)"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            # Pozas con partos en los últimos 21-28 días (edad ideal destete)
            cur.execute("""
                SELECT DISTINCT p.id, p.nombre, p.tipo,
                       COUNT(DISTINCT pt.id) as partos_recientes,
                       SUM(pt.nacidos_vivos) as crias_nacidas
                FROM pozas p
                JOIN partos_simplificada pt ON p.id = pt.poza_id
                WHERE p.galpon_id = %s 
                AND pt.fecha_parto BETWEEN CURRENT_DATE - INTERVAL '28 days' 
                                    AND CURRENT_DATE - INTERVAL '21 days'
                AND p.estado = 'activo'
                GROUP BY p.id, p.nombre, p.tipo
                HAVING SUM(pt.nacidos_vivos) > 0
                ORDER BY p.nombre
            """, (galpon_id,))
            pozas = cur.fetchall()
            cur.close()
            return pozas
        except Exception as e:
            print(f"Error obteniendo pozas para destete: {e}")
            return []

    def obtener_destetes_recientes(self, limite=10):
        """Obtiene los destetes recientes"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT d.id, d.fecha_destete, d.machos_destetados, d.hembras_destetadas,
                       d.reemplazo_machos, d.reemplazo_hembras, d.engorde_machos, d.engorde_hembras,
                       d.venta_directa_machos, d.venta_directa_hembras, d.observaciones,
                       g.nombre as galpon_nombre, p.nombre as poza_origen_nombre
                FROM destetes_simplificada d
                LEFT JOIN galpones g ON d.galpon_id = g.id
                LEFT JOIN pozas p ON d.poza_origen_id = p.id
                ORDER BY d.fecha_destete DESC, d.id DESC
                LIMIT %s
            """, (limite,))
            destetes = cur.fetchall()
            cur.close()
            return destetes
        except Exception as e:
            print(f"Error obteniendo destetes recientes: {e}")
            return []

    def obtener_estadisticas_destete(self):
        """Obtiene estadísticas de destetes"""
        if not self.db:
            return {}
        
        try:
            cur = self.db.cursor()
            
            # Total destetados este mes
            cur.execute("""
                SELECT 
                    SUM(machos_destetados + hembras_destetadas) as total_destetados,
                    SUM(reemplazo_machos + reemplazo_hembras) as total_reemplazo,
                    SUM(engorde_machos + engorde_hembras) as total_engorde,
                    SUM(venta_directa_machos + venta_directa_hembras) as total_venta_directa
                FROM destetes_simplificada 
                WHERE fecha_destete >= DATE_TRUNC('month', CURRENT_DATE)
            """)
            stats = cur.fetchone()
            cur.close()
            
            return {
                'total_destetados': stats[0] or 0,
                'total_reemplazo': stats[1] or 0,
                'total_engorde': stats[2] or 0,
                'total_venta_directa': stats[3] or 0
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas destete: {e}")
            return {}