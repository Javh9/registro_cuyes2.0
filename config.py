import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-desarrollo'
    
    # Configuración de PostgreSQL - USA LA CONTRASEÑA QUE FUNCIONÓ
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'registro_cuyes'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '1234'  # ← ESTA ES IMPORTANTE
    DB_PORT = os.environ.get('DB_PORT') or '5432'