from config import Config
import psycopg2

print("=== DEBUG CONEXIÓN POSTGRESQL ===")
print(f"Host: {Config.DB_HOST}")
print(f"Database: {Config.DB_NAME}") 
print(f"User: {Config.DB_USER}")
print(f"Password: {Config.DB_PASSWORD}")
print(f"Port: {Config.DB_PORT}")

try:
    print("🔍 Intentando conectar...")
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT
    )
    print("✅ CONEXIÓN EXITOSA!")
    
    # Probar consultas
    cur = conn.cursor()
    
    # Verificar tablas
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tablas = cur.fetchall()
    print(f"📊 Tablas en la base de datos: {[t[0] for t in tablas]}")
    
    # Contar galpones
    cur.execute("SELECT COUNT(*) FROM galpones")
    galpones = cur.fetchone()[0]
    print(f"🏠 Galpones: {galpones}")
    
    # Contar pozas  
    cur.execute("SELECT COUNT(*) FROM pozas")
    pozas = cur.fetchone()[0]
    print(f"🔵 Pozas: {pozas}")
    
    conn.close()
    print("🎉 TODO FUNCIONA CORRECTAMENTE!")
    
except Exception as e:
    print(f"❌ ERROR DETALLADO: {e}")
    print(f"Tipo de error: {type(e).__name__}")