import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/registro_cuyes")
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta")
