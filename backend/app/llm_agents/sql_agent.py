# sql_agent.py
import os, json, re
import logging
from app.prompts import sql_prompt
from app.llm_agents.openai_client import create_chat_completion_with_retry

logger = logging.getLogger(__name__)

MODEL = os.getenv("SQL_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

async def generate_sql(schema_text: str, user_query: str) -> dict:
    logger.info(f"[SQL Agent] Generating SQL for query: '{user_query}'")
    logger.info(f"[SQL Agent] Using model: {MODEL}")
    
    prompt = sql_prompt(schema_text, user_query)
    logger.debug(f"[SQL Agent] Prompt length: {len(prompt)} characters")
    
    try:
        resp = await create_chat_completion_with_retry(
            model=MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        raw = resp.choices[0].message.content.strip()
        logger.info(f"[SQL Agent] Received response: {len(raw)} characters")
        logger.debug(f"[SQL Agent] Raw response preview: {raw[:200]}...")
        
        try:
            result = json.loads(raw)
            logger.info(f"[SQL Agent] ✅ Successfully parsed JSON response")
            logger.info(f"[SQL Agent] SQL length: {len(result.get('sql', ''))} characters")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"[SQL Agent] ⚠️ JSON parse error: {e}, attempting regex extraction...")
            # try to extract JSON-looking block
            m = re.search(r"\{.*\}", raw, flags=re.S)
            if m:
                try:
                    result = json.loads(m.group(0))
                    logger.info(f"[SQL Agent] ✅ Successfully extracted JSON via regex")
                    return result
                except Exception as e2:
                    logger.error(f"[SQL Agent] ❌ Regex extraction also failed: {e2}")
            logger.warning(f"[SQL Agent] ⚠️ Falling back to raw response")
            return {"sql": "", "explain": raw}
    except Exception as e:
        logger.error(f"[SQL Agent] ❌ Error in generate_sql: {type(e).__name__}: {str(e)}")
        raise
