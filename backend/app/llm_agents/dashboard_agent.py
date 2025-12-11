# dashboard_agent.py
import os, json, re
import logging
from app.prompts import dashboard_prompt
from app.llm_agents.openai_client import create_chat_completion_with_retry

logger = logging.getLogger(__name__)

MODEL = os.getenv("DASHBOARD_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

async def plan_dashboard(schema_text: str, user_query: str) -> dict:
    logger.info(f"[Dashboard Agent] Planning dashboard for query: '{user_query}'")
    logger.info(f"[Dashboard Agent] Using model: {MODEL}")
    
    prompt = dashboard_prompt(schema_text, user_query)
    try:
        resp = await create_chat_completion_with_retry(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0.1
        )
        raw = resp.choices[0].message.content.strip()
        logger.info(f"[Dashboard Agent] Received response: {len(raw)} characters")
        
        try:
            result = json.loads(raw)
            charts_count = len(result.get("charts", []))
            kpis_count = len(result.get("kpis", []))
            logger.info(f"[Dashboard Agent] ✅ Dashboard planned: {charts_count} charts, {kpis_count} KPIs")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"[Dashboard Agent] ⚠️ JSON parse error: {e}, attempting regex extraction...")
            m = re.search(r"\{.*\}", raw, flags=re.S)
            if m:
                try:
                    result = json.loads(m.group(0))
                    logger.info(f"[Dashboard Agent] ✅ Successfully extracted JSON via regex")
                    return result
                except Exception as e2:
                    logger.error(f"[Dashboard Agent] ❌ Regex extraction failed: {e2}")
            logger.warning(f"[Dashboard Agent] ⚠️ Returning empty dashboard plan")
            return {"charts": [], "kpis": []}
    except Exception as e:
        logger.error(f"[Dashboard Agent] ❌ Error: {e}")
        return {"charts": [], "kpis": []}
