# migracion_inventario.py
import sqlite3

def crear_tabla_inventario():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_actualizacion DATE NOT NULL,
                reproductores INTEGER DEFAULT 0,
                lactantes INTEGER DEFAULT 0,
                destete INTEGER DEFAULT 0,
                reemplazo INTEGER DEFAULT 0,
                engorde_destete INTEGER DEFAULT 0,
                engorde_descarte INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar registro inicial
        from datetime import date
        cursor.execute('''
            INSERT INTO inventario (fecha_actualizacion, reproductores, lactantes, destete, reemplazo, engorde_destete, engorde_descarte)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date.today().isoformat(), 0, 0, 0, 0, 0, 0))
        
        conn.commit()
        print("✅ Tabla 'inventario' creada exitosamente con registro inicial")
        
    except Exception as e:
        print("❌ Error creando tabla inventario:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    crear_tabla_inventario()