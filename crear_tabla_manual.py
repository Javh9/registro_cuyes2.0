from db.connection import get_db_connection

def crear_tabla_mortalidad():
    print("🔧 Creando tabla mortalidad_general...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla mortalidad_general
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mortalidad_general (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL,
                tipo_cuy VARCHAR(20) NOT NULL CHECK (tipo_cuy IN ('reproductor', 'lactante', 'destete', 'reemplazo', 'engorde_destete', 'engorde_descarte')),
                galpon_id INTEGER REFERENCES galpones(id),
                poza_id INTEGER REFERENCES pozas(id),
                cantidad INTEGER NOT NULL CHECK (cantidad > 0),
                causa VARCHAR(100) NOT NULL,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Crear índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mortalidad_tipo ON mortalidad_general(tipo_cuy)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mortalidad_fecha ON mortalidad_general(fecha)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mortalidad_galpon ON mortalidad_general(galpon_id)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tabla mortalidad_general creada correctamente")
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")

if __name__ == "__main__":
    crear_tabla_mortalidad()