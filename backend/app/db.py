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
    
# def get_database_schema():
#     """
#     Returns schema in this format:

#     TABLE customers(customer_id, name, ...)
#     TABLE sales(sale_id, sale_date, ...)
#     TABLE products(product_id, ...)
#     """

#     schema_sql = """
#     SELECT 
#         'TABLE ' || table_name || '(' ||
#         STRING_AGG(column_name, ', ' ORDER BY ordinal_position) || ')' AS schema_line
#     FROM information_schema.columns
#     WHERE table_schema = 'public'
#     GROUP BY table_name
#     ORDER BY table_name;
#     """

#     result = run_sql(schema_sql)

#     if "rows" in result:
#         return "\n".join([row["schema_line"] for row in result["rows"]])

#     return ""


def get_database_schema():
    """
    Return a large but structured schema string for the LLM:
    TABLE invoice:
      - invoice_number:varchar (pk)
      - created_on:timestamp (sales date)
      ...
    """
    sql = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema='public'
    ORDER BY table_name, ordinal_position;
    """
    res = run_sql(sql)
    rows = res.get("rows", [])
    if not rows:
        return ""

    schema_map = {}
    for r in rows:
        t = r["table_name"]
        c = f"{r['column_name']}:{r['data_type']}"
        schema_map.setdefault(t, []).append(c)

    # build lines with table descriptions for better LLM understanding
    table_descriptions = {
        "sales": "Main sales transactions table - contains sale_date, quantity, unit_price, revenue. Use for sales/revenue queries.",
        "invoices": "Invoice records table - contains invoice_date, linked to sales via sale_id. Use for invoice/billing queries.",
        "products": "Product catalog - contains product_id, name, category, price. Join with sales to get product details.",
        "customers": "Customer information - contains customer_id, name, city, region_id. Join with sales to get customer details.",
        "returns": "Return/refund transactions - contains return_date, linked to sales via sale_id. Use for return/refund queries.",
        "regions": "Geographic regions - contains region_id, name. Join with customers to get regional data."
    }
    
    lines = []
    for table, cols in schema_map.items():
        desc = table_descriptions.get(table, "")
        if desc:
            lines.append(f"TABLE {table}: {desc}")
        else:
            lines.append(f"TABLE {table}:")
        for c in cols:
            lines.append(f"  - {c}")
        lines.append("")  # blank line between tables
    return "\n".join(lines)
