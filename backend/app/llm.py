from openai import OpenAI
from dotenv import load_dotenv
import os
import re  # <-- added for optional SQL extraction

# Load .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def parse_natural_query(query: str):
    """
    Convert natural language query to SQL.
    
    CHANGE:
    - Updated prompt to instruct the LLM to return ONLY SQL.
    - Added optional regex extraction from code blocks to clean output.
    """

    # Optional improvement for LLM prompt:
    # Ask the model to return only SQL inside ```sql ... ``` blocks.
    prompt = f"""
You are a SQL assistant.
Convert the following natural language request into a valid PostgreSQL query.
Return ONLY the SQL query, inside a markdown ```sql block```, without any explanations.

User request:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a SQL assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_sql = response.choices[0].message.content.strip()

    # Optional: extract SQL if it's inside a ```sql ... ``` block
    match = re.search(r"```sql\s*(.*?)```", raw_sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql_only = match.group(1).strip()
    else:
        sql_only = raw_sql  # fallback if no code block

    return {"sql": sql_only}
