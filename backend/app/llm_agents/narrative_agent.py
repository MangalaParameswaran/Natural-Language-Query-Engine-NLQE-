# narrative_agent.py
import os, json, re
from app.prompts import narrative_prompt
from app.llm_agents.openai_client import create_chat_completion_with_retry

MODEL = os.getenv("NARRATIVE_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

async def write_report(summary, insights, user_query) -> dict:
    prompt = narrative_prompt(summary, insights, user_query)
    resp = await create_chat_completion_with_retry(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.7
    )
    raw = resp.choices[0].message.content.strip()
    
    try:
        # Try to extract JSON if wrapped in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{[^{}]*"report_html"[^{}]*\}', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(0)
        
        result = json.loads(raw)
        # Ensure we have both fields
        if "report_html" not in result:
            result["report_html"] = f"<p>{raw}</p>"
        if "title" not in result:
            result["title"] = "Analytics Report"
        return result
    except Exception as e:
        # Fallback: wrap raw text in HTML
        return {
            "report_html": f"<div><h3>Executive Summary</h3><p>{raw}</p></div>",
            "title": "Analytics Report"
        }
