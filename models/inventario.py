from db.connection import get_db_connection
from datetime import datetime

class Inventario:
    def __init__(self):
        self.db = get_db_connection()
    
    def calcular_inventario_actual(self):
        """Calcular el inventario actual basado en todas las operaciones"""
        if not self.db:
            return self._inventario_vacio()
        
        try:
            cur = self.db.cursor()
            
            # 1. Reproductores (estimado basado en pozas reproductoras)
            cur.execute("""
                SELECT COUNT(*) FROM pozas WHERE tipo = 'reproductora' AND estado = 'activo'
            """)
            pozas_reproductoras = cur.fetchone()[0] or 0
            reproductores = pozas_reproductoras * 10  # Estimado: 10 animales por poza
            
            # 2. Lactantes (partos recientes - mortalidad lactancia)
            cur.execute("""
                SELECT 
                    (SELECT COALESCE(SUM(nacidos_vivos), 0) FROM partos_simplificada 
                     WHERE fecha_parto >= CURRENT_DATE - INTERVAL '21 days') -
                    (SELECT COALESCE(SUM(cantidad), 0) FROM mortalidad_lactancia 
                     WHERE fecha >= CURRENT_DATE - INTERVAL '21 days')
            """)
            lactantes = cur.fetchone()[0] or 0
            lactantes = max(0, lactantes)  # No puede ser negativo
            
            # 3. Destete (animales destetados recientemente)
            cur.execute("""
                SELECT COALESCE(SUM(machos_destetados + hembras_destetadas), 0) 
                FROM destetes_simplificada 
                WHERE fecha_destete >= CURRENT_DATE - INTERVAL '60 days'
            """)
            destete = cur.fetchone()[0] or 0
            
            # 4. Engorde por Destete
            cur.execute("""
                SELECT COALESCE(SUM(engorde_machos + engorde_hembras), 0) 
                FROM destetes_simplificada 
                WHERE fecha_destete >= CURRENT_DATE - INTERVAL '90 days'
            """)
            engorde_destete = cur.fetchone()[0] or 0
            
            # 5. Engorde por Descarte (estimado)
            engorde_descarte = engorde_destete * 0.2  # 20% del engorde por destete
            
            # 6. Reemplazo
            cur.execute("""
                SELECT COALESCE(SUM(reemplazo_machos + reemplazo_hembras), 0) 
                FROM destetes_simplificada 
                WHERE fecha_destete >= CURRENT_DATE - INTERVAL '180 days'
            """)
            reemplazo = cur.fetchone()[0] or 0
            
            # 7. Total general
            total_general = reproductores + lactantes + destete + engorde_destete + engorde_descarte + reemplazo
            
            # 8. Valor estimado del inventario (precios promedio)
            valor_estimado = (
                reproductores * 10 +      # S/ 25 por reproductor
                lactantes * 0 +           # S/ 8 por lactante
                destete * 2 +           # S/ 12 por destete
                engorde_destete * 6 +   # S/ 18 por engorde destete
                engorde_descarte * 10 +  # S/ 15 por engorde descarte
                reemplazo * 5           # S/ 20 por reemplazo
            )
            
            cur.close()
            
            return {
                'reproductores': reproductores,
                'lactantes': lactantes,
                'destete': destete,
                'engorde_destete': engorde_destete,
                'engorde_descarte': engorde_descarte,
                'reemplazo': reemplazo,
                'total_general': total_general,
                'valor_estimado': valor_estimado,
                'fecha_calculo': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            
        except Exception as e:
            print(f"Error calculando inventario: {e}")
            return self._inventario_vacio()
    
    def obtener_movimientos_recientes(self):
        """Obtener movimientos recientes del inventario"""
        if not self.db:
            return []
        
        try:
            cur = self.db.cursor()
            
            # Combinar todos los movimientos recientes
            cur.execute("""
                (SELECT 
                    'parto' as tipo,
                    fecha_parto as fecha,
                    CONCAT('Parto: ', nacidos_vivos, ' nacidos') as descripcion,
                    nacidos_vivos as cantidad,
                    NULL as valor_unitario,
                    NULL as total,
                    g.nombre as ubicacion
                FROM partos_simplificada p
                JOIN galpones g ON p.galpon_id = g.id
                WHERE fecha_parto >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY fecha_parto DESC
                LIMIT 10)
                
                UNION ALL
                
                (SELECT 
                    'destete' as tipo,
                    fecha_destete as fecha,
                    CONCAT('Destete: ', machos_destetados + hembras_destetadas, ' animales') as descripcion,
                    machos_destetados + hembras_destetadas as cantidad,
                    NULL as valor_unitario,
                    NULL as total,
                    g.nombre as ubicacion
                FROM destetes_simplificada d
                JOIN galpones g ON d.galpon_id = g.id
                WHERE fecha_destete >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY fecha_destete DESC
                LIMIT 10)
                
                UNION ALL
                
                (SELECT 
                    'mortalidad' as tipo,
                    fecha as fecha,
                    CONCAT('Mortalidad: ', cantidad, ' (', causa, ')') as descripcion,
                    -cantidad as cantidad,  -- Negativo porque reduce inventario
                    NULL as valor_unitario,
                    NULL as total,
                    g.nombre as ubicacion
                FROM mortalidad_lactancia m
                JOIN galpones g ON m.galpon_id = g.id
                WHERE fecha >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY fecha DESC
                LIMIT 10)
                
                UNION ALL
                
                (SELECT 
                    'venta' as tipo,
                    fecha_venta as fecha,
                    CONCAT('Venta: ', cantidad, ' (', tipo_producto, ')') as descripcion,
                    -cantidad as cantidad,  -- Negativo porque reduce inventario
                    precio_unitario as valor_unitario,
                    total as total,
                    cliente as ubicacion
                FROM ventas
                WHERE fecha_venta >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY fecha_venta DESC
                LIMIT 10)
                
                ORDER BY fecha DESC
                LIMIT 20
            """)
            
            movimientos = cur.fetchall()
            cur.close()
            
            return [
                {
                    'tipo': mov[0],
                    'fecha': mov[1].strftime('%d/%m/%Y') if mov[1] else '',
                    'descripcion': mov[2],
                    'cantidad': mov[3],
                    'valor_unitario': float(mov[4]) if mov[4] else None,
                    'total': float(mov[5]) if mov[5] else None,
                    'ubicacion': mov[6]
                }
                for mov in movimientos
            ]
            
        except Exception as e:
            print(f"Error obteniendo movimientos: {e}")
            return []
    
    def obtener_estadisticas_inventario(self):
        """Obtener estadísticas del inventario para gráficos"""
        if not self.db:
            return {}
        
        try:
            cur = self.db.cursor()
            
            # Distribución por categorías
            inventario = self.calcular_inventario_actual()
            
            # Evolución mensual del inventario (últimos 6 meses)
            cur.execute("""
                SELECT 
                    EXTRACT(YEAR FROM fecha_parto) as año,
                    EXTRACT(MONTH FROM fecha_parto) as mes,
                    SUM(nacidos_vivos) as nacimientos
                FROM partos_simplificada 
                WHERE fecha_parto >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY año, mes
                ORDER BY año, mes
            """)
            evolucion = cur.fetchall()
            
            cur.close()
            
            return {
                'distribucion': {
                    'labels': ['Reproductores', 'Lactantes', 'Destete', 'Engorde Destete', 'Engorde Descarte', 'Reemplazo'],
                    'data': [
                        inventario['reproductores'],
                        inventario['lactantes'],
                        inventario['destete'],
                        inventario['engorde_destete'],
                        inventario['engorde_descarte'],
                        inventario['reemplazo']
                    ],
                    'colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
                },
                'evolucion': [
                    {
                        'mes': f"{int(row[1])}/{int(row[0])}",
                        'nacimientos': row[2] or 0
                    }
                    for row in evolucion
                ]
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas inventario: {e}")
            return {}
    
    def _inventario_vacio(self):
        """Retornar inventario vacío en caso de error"""
        return {
            'reproductores': 0,
            'lactantes': 0,
            'destete': 0,
            'engorde_destete': 0,
            'engorde_descarte': 0,
            'reemplazo': 0,
            'total_general': 0,
            'valor_estimado': 0,
            'fecha_calculo': datetime.now().strftime('%d/%m/%Y %H:%M')
        }