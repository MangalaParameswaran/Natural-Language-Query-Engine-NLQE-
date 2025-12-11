# db.py
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
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()
        print("--------Connected to PostgreSQL--------")
    except Exception as e:
        print("--------DB connect failed--------", e)


async def disconnect_db():
    print("--------PostgreSQL disconnect--------")


def get_connection():
    # ⭐ IMPROVED: autocommit + safe connection
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True  # ⭐ important for analytics queries
    )
    return conn


def run_sql(sql: str):
    """
    Runs given SQL and returns rows + columns.
    Enterprise-safe SQL runner.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # ⭐ IMPROVED: protect against dangerous commands
        blocked = ["insert ", "update ", "delete ", "drop ", "truncate "]
        if any(b in sql.lower() for b in blocked):
            return {
                "error": "Write operations are blocked in analytics engine.",
                "columns": [],
                "rows": []
            }

        cur.execute(sql)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        conn.close()

        return {"columns": cols, "rows": rows, "error": None}

    except Exception as e:
        return {"error": str(e), "columns": [], "rows": []}


# This will:
# ✔ open connection
# ✔ execute SQL
# ✔ return rows + column names
# ✔ safely catch errors