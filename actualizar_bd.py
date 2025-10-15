import psycopg2
import sys
import os

# Agregar el directorio actual al path para importar db.connection
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connection import get_db_connection

def actualizar_tabla_gastos():
    print("🔄 Actualizando tabla de gastos...")
    
    try:
        # Obtener conexión
        conn = get_db_connection()
        if conn:
            # Configurar autocommit para manejar errores mejor
            conn.autocommit = False
            cur = conn.cursor()
            print("✅ Conectado a la base de datos")
            
            try:
                # 1. Buscar SOLO la constraint CHECK (ignorar NOT NULL)
                print("📋 Buscando restricción CHECK...")
                cur.execute("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'gastos' 
                    AND constraint_type = 'CHECK'
                    AND constraint_name LIKE '%tipo%';
                """)
                
                check_constraint = cur.fetchone()
                
                if check_constraint:
                    constraint_name = check_constraint[0]
                    print(f"   - Encontrada restricción CHECK: {constraint_name}")
                    
                    # 2. Eliminar solo la constraint CHECK
                    print(f"   🗑️ Eliminando restricción {constraint_name}...")
                    cur.execute(f"ALTER TABLE gastos DROP CONSTRAINT {constraint_name};")
                    print(f"   ✅ Restricción {constraint_name} eliminada")
                else:
                    print("   ℹ️ No se encontró restricción CHECK específica para 'tipo'")
                
                # 3. Agregar nueva constraint con transporte
                print("   🆕 Agregando nueva restricción con 'transporte'...")
                cur.execute("""
                    ALTER TABLE gastos 
                    ADD CONSTRAINT gastos_tipo_check 
                    CHECK (tipo IN ('alimentacion', 'medicamentos', 'mantenimiento', 'mano_obra', 'transporte', 'otros'));
                """)
                print("   ✅ Nueva restricción agregada")
                
                # 4. Confirmar cambios
                conn.commit()
                print("✅ Cambios confirmados en la base de datos")
                
                # 5. Probar inserción de transporte
                print("🧪 Probando inserción de gasto de transporte...")
                try:
                    cur.execute("""
                        INSERT INTO gastos (fecha, tipo, descripcion, monto, proveedor, observaciones) 
                        VALUES (CURRENT_DATE, 'transporte', 'Prueba de transporte', 50.00, 'Test', '')
                        RETURNING id;
                    """)
                    test_id = cur.fetchone()[0]
                    print(f"   ✅ Prueba exitosa! ID del gasto: {test_id}")
                    
                    # Limpiar la prueba
                    cur.execute("DELETE FROM gastos WHERE id = %s;", (test_id,))
                    conn.commit()
                    print("   🧹 Prueba limpiada")
                    
                except Exception as e:
                    print(f"   ❌ Error en la prueba: {e}")
                    conn.rollback()
                
                print("\n🎉 ¡Base de datos actualizada correctamente!")
                print("📋 Ahora puedes registrar gastos de tipo 'transporte'")
                
            except Exception as e:
                print(f"❌ Error durante la actualización: {e}")
                conn.rollback()
                print("🔁 Revertiendo cambios...")
            
            finally:
                cur.close()
                conn.close()
                
        else:
            print("❌ No se pudo conectar a la base de datos")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

def solucion_alternativa():
    """Solución alternativa si la primera falla"""
    print("\n" + "="*50)
    print("SOLUCIÓN ALTERNATIVA")
    print("="*50)
    
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            print("🔄 Intentando solución alternativa...")
            
            # Crear tabla temporal
            print("📋 Creando tabla temporal...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS gastos_nueva (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('alimentacion', 'medicamentos', 'mantenimiento', 'mano_obra', 'transporte', 'otros')),
                    descripcion VARCHAR(200) NOT NULL,
                    monto DECIMAL(10,2) NOT NULL,
                    proveedor VARCHAR(100),
                    observaciones TEXT,
                    fecha_creacion TIMESTAMP DEFAULT NOW()
                );
            """)
            print("✅ Tabla temporal creada")
            
            # Copiar datos si la tabla original existe
            try:
                cur.execute("SELECT COUNT(*) FROM gastos;")
                count = cur.fetchone()[0]
                print(f"📊 Copiando {count} registros...")
                
                cur.execute("""
                    INSERT INTO gastos_nueva (id, fecha, tipo, descripcion, monto, proveedor, observaciones, fecha_creacion)
                    SELECT id, fecha, tipo, descripcion, monto, proveedor, observaciones, fecha_creacion 
                    FROM gastos;
                """)
                print("✅ Datos copiados")
                
                # Renombrar tablas
                cur.execute("ALTER TABLE gastos RENAME TO gastos_vieja;")
                cur.execute("ALTER TABLE gastos_nueva RENAME TO gastos;")
                print("✅ Tablas renombradas")
                
                conn.commit()
                print("🎉 Solución alternativa completada!")
                
            except Exception as e:
                print(f"ℹ️ No se pudieron copiar datos: {e}")
                conn.rollback()
            
            cur.close()
            conn.close()
            
    except Exception as e:
        print(f"❌ Error en solución alternativa: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("ACTUALIZADOR DE BASE DE DATOS - MÓDULO GASTOS")
    print("=" * 50)
    
    # Intentar método principal primero
    actualizar_tabla_gastos()
    
    # Preguntar si intentar solución alternativa
    print("\n¿Quieres intentar la solución alternativa? (s/n): ")
    respuesta = input().strip().lower()
    
    if respuesta == 's':
        solucion_alternativa()
    
    print("\nPresiona Enter para salir...")
    input()