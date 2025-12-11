# app/llm_agents/insight_agent.py

import json
import re
from dotenv import load_dotenv
import os
from app.prompts import insight_prompt
from app.llm_agents.openai_client import create_chat_completion_with_retry

load_dotenv()

async def generate_insights(columns, rows, user_query):
    """
    columns: ["month", "total_sales"]
    rows: [{"month": "...", "total_sales": ...}] or list of lists
    user_query: "show invoice summary of this month"
    """
    # Convert rows to list of dicts if needed
    if rows and len(rows) > 0:
        if isinstance(rows[0], (list, tuple)):
            sample_rows = []
            for row in rows[:20]:  # Limit to 20 rows
                obj = {}
                for i, col in enumerate(columns):
                    if i < len(row):
                        obj[col] = row[i]
                sample_rows.append(obj)
        else:
            sample_rows = rows[:20] if rows else []
    else:
        sample_rows = []

    prompt = insight_prompt(columns, sample_rows, user_query)

    response = await create_chat_completion_with_retry(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()

    try:
        # Try to extract JSON if wrapped in markdown
        json_match = re.search(r'\{[^{}]*"insights"[^{}]*\[[^\]]*\][^{}]*\}', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        data = json.loads(raw)
        return data
    except Exception as e:
        return {
            "insights": [
                "Unable to generate insights due to formatting error.",
                f"Error: {str(e)}"
            ]
        }
