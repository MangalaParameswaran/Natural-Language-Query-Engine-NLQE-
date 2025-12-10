import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

async def connect_db():
    print("--------Mock DB connect-------")

async def disconnect_db():
    print("-------Mock DB disconnect-------")


def get_connection():
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def run_sql(sql: str):
    """
    Runs given SQL and returns rows + columns.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        conn.close()

        return {
            "columns": cols,
            "rows": rows
        }
    except Exception as e:
        return {
            "error": str(e),
            "columns": [],
            "rows": []
        }

# This will:
# ✔ open connection
# ✔ execute SQL
# ✔ return rows + column names
# ✔ safely catch errors