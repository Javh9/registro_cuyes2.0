import psycopg2
import os

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="cuyes", 
            user="postgres",
            password="1234",  # ⚠️ REEMPLAZA con tu password
            port="5432"
        )
        print("✅ Conexión a PostgreSQL exitosa")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return None