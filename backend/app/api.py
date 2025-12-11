# api.py
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.llm_agents.orchestrator import orchestrate_query

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def run_query(req: QueryRequest):
    import time
    start_time = time.time()
    q = req.query.strip()
    logger.info(f"📥 Received query request: '{q}'")
    
    if not q:
        logger.warning("❌ Empty query received")
        raise HTTPException(400, "Query cannot be empty")
    
    try:
        logger.info(f"🔄 Processing query: '{q}'")
        result = await orchestrate_query(q)
        elapsed_time = time.time() - start_time
        logger.info(f"⏱️ Query processed in {elapsed_time:.2f} seconds")
        
        # Structure response for frontend
        response = {
            "status": "ok",
            "message": "Query processed successfully",
            "data": {
                "intent": result.get("intent", "chart"),
                "sql": result.get("sql_plan", {}).get("sql", ""),
                "sql_explain": result.get("sql_plan", {}).get("explain", ""),
                "columns": result.get("columns", []),
                "rows": result.get("rows", []),
                "sql_error": result.get("sql_error"),
                "dashboard_plan": result.get("dashboard_plan", {}),
                "insights": result.get("insights", []),
                "report": result.get("report", {}),
                "router": result.get("router", {})
            }
        }
        
        logger.info(f"✅ Query processed successfully. Response size: {len(str(response))} characters")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing query '{q}': {type(e).__name__}: {str(e)}", exc_info=True)
        error_msg = f"Error processing query: {str(e)}"
        raise HTTPException(500, error_msg)
