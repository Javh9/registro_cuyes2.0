def obtener_por_galpon(self, galpon_id):
    """Obtener todas las pozas de un galpón específico"""
    if not self.db:
        return []
    
    try:
        cur = self.db.cursor()
        cur.execute("SELECT id, nombre FROM pozas WHERE galpon_id = %s", (galpon_id,))
        pozas = cur.fetchall()
        cur.close()
        return pozas
    except Exception as e:
        print(f"Error obteniendo pozas por galpón: {e}")
        return []