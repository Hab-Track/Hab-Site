import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = "mydb"
DB_HOST = "localhost"
DB_PORT = 5432

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
        cursor_factory=RealDictCursor
    )
    conn.autocommit = True
    print("Connected to the database")
except Exception as e:
    raise RuntimeError(f"Error while connecting to db: {e}")
