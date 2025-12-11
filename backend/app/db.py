# db.py
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ---------------------------------------------------
# Optional (for FastAPI startup)
# ---------------------------------------------------

async def connect_db():
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        conn.close()
        print("--------Connected to PostgreSQL--------")
    except Exception as e:
        print("--------DB connect failed--------", e)


async def disconnect_db():
    print("--------PostgreSQL disconnect--------")


# ---------------------------------------------------
# New standard connection helper
# ---------------------------------------------------

def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        row_factory=dict_row,   # return dict-like rows
    )


# ---------------------------------------------------
# Execute SQL safely (for your NLQ engine)
# ---------------------------------------------------


def run_sql(sql: str):
    """
    Runs SQL and returns:
    { columns: [...], rows: [...] }
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


# ---------------------------------------------------
# NEW: Dynamic schema generator for LLM
# ---------------------------------------------------
    
def get_database_schema():
    """
    Returns schema in this format:

    TABLE customers(customer_id, name, ...)
    TABLE sales(sale_id, sale_date, ...)
    TABLE products(product_id, ...)
    """

    schema_sql = """
    SELECT 
        'TABLE ' || table_name || '(' ||
        STRING_AGG(column_name, ', ' ORDER BY ordinal_position) || ')' AS schema_line
    FROM information_schema.columns
    WHERE table_schema = 'public'
    GROUP BY table_name
    ORDER BY table_name;
    """

    result = run_sql(schema_sql)

    if "rows" in result:
        return "\n".join([row["schema_line"] for row in result["rows"]])

    return ""
