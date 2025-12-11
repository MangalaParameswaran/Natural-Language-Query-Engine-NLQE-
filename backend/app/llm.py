# llm.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
from app.db import get_database_schema

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


async def parse_natural_query(query: str):
    schema = get_database_schema()

    prompt = f"""
You are an expert PostgreSQL SQL generator.

VERY IMPORTANT RULES:
- Use ONLY the tables and fields listed in the schema.
- NEVER guess or hallucinate fields.
- If something requested is NOT in the schema, answer:
  "Error: Field or table not found in database schema."
- Always return ONLY SQL inside ```sql ... ```
- Do not explain anything.

Database Schema:
{schema}

User request:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert PostgreSQL SQL generator. "
                    "Use only tables/columns in the schema."
                )
            },
            {"role": "user", "content": prompt}
        ]
    )

    raw_sql = response.choices[0].message.content.strip()

    # Extract SQL
    match = re.search(r"```sql\s*(.*?)```", raw_sql, re.DOTALL | re.IGNORECASE)
    sql_only = match.group(1).strip() if match else raw_sql

    # ⭐ FIX: return dict instead of string
    
    return {
        "sql": sql_only,
        "raw_response": raw_sql
    }
