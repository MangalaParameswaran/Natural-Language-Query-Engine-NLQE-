# router_agent.py
import os, json, re
import logging
from app.prompts import router_prompt
from app.llm_agents.openai_client import create_chat_completion_with_retry

logger = logging.getLogger(__name__)

MODEL = os.getenv("ROUTER_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

async def decide_intent(schema_text: str, user_query: str) -> dict:
    logger.info(f"[Router Agent] Deciding intent for query: '{user_query}'")
    logger.info(f"[Router Agent] Using model: {MODEL}")
    
    prompt = router_prompt(schema_text, user_query)
    try:
        resp = await create_chat_completion_with_retry(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        raw = resp.choices[0].message.content.strip()
        logger.info(f"[Router Agent] Received response: {len(raw)} characters")
        
        try:
            result = json.loads(raw)
            logger.info(f"[Router Agent] ✅ Intent determined: {result.get('intent', 'unknown')}")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"[Router Agent] ⚠️ JSON parse error: {e}, using fallback heuristics")
            # fallback heuristics
            q = user_query.lower()
            if any(k in q for k in ["report","write","blog"]):
                result = {"intent":"report","reason":"contains report/blog keywords"}
            elif "dashboard" in q or "kpi" in q:
                result = {"intent":"dashboard","reason":"mentions dashboard/kpi"}
            elif "insight" in q:
                result = {"intent":"insights","reason":"mentions insights"}
            elif any(k in q for k in ["sales","top","compare","trend","monthly","daily"]):
                result = {"intent":"chart","reason":"analytics-like query"}
            else:
                result = {"intent":"sql","reason":"default fallback"}
            logger.info(f"[Router Agent] Fallback intent: {result['intent']}")
            return result
    except Exception as e:
        logger.error(f"[Router Agent] ❌ Error: {e}, using fallback")
        q = user_query.lower()
        if any(k in q for k in ["report","write","blog"]):
            return {"intent":"report","reason":f"Error fallback: {str(e)}"}
        return {"intent":"chart","reason":f"Error fallback: {str(e)}"}
