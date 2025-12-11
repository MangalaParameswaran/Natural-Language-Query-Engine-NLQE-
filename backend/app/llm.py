# llm.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

# Load .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def parse_natural_query(query: str):
    """
    Convert natural language query to SQL.
    Returns SQL only.
    """

    # ⭐ IMPROVED:
    # Clean input to avoid prompt-injection
    safe_query = query.strip().replace(";", "")

    # 🔧 CHANGED: moved rules into SYSTEM block only
    system_prompt = """
You are an expert PostgreSQL SQL generator.

Use ONLY PostgreSQL syntax.

TABLE customers(customer_id, name, email, city, region_id, created_at)
TABLE regions(region_id, name)
TABLE products(product_id, sku, name, category, price)
TABLE sales(sale_id, sale_date, customer_id, product_id, quantity, unit_price, revenue)
TABLE invoices(invoice_id, invoice_date, sale_id, invoiced, amount)
TABLE returns(return_id, sale_id, return_date, qty_returned, refund_amount)

Rules:
- Use DATE_TRUNC for time grouping.
- Use correct JOINs.
- For revenue use sales.revenue.
- Return ONLY SQL inside ```sql ... ```
- No explanation.
"""

    user_prompt = f"User request: {safe_query}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_sql = response.choices[0].message.content.strip()

    # ⭐ IMPROVED: safe SQL extraction
    match = re.search(r"```sql\s*(.*?)```", raw_sql, re.DOTALL | re.IGNORECASE)
    sql_only = match.group(1).strip() if match else raw_sql

    return sql_only  # 🔧 CHANGED: return only SQL, simpler for FE
