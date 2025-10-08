import psycopg2
from psycopg2.extras import DictCursor
from config import Config

def get_db_connection():
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn

def get_db_dict_cursor(conn):
    return conn.cursor(cursor_factory=DictCursor)
