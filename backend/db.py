# backend/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 讀取 .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "asrtghjv524")
DB_NAME = os.getenv("DB_NAME", "smart_city")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 建立 engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 測試連線
def test_conn():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            return result[0]
    except Exception as e:
        print("DB connection error:", e)
        return None
