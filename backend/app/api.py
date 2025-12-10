from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.llm import parse_natural_query
from app.db import run_sql

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = {}

@router.post("/query", response_model=QueryResponse)
async def run_query(req: QueryRequest):
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="query is empty")

    # STEP 1 — LLM parse
    parsed = await parse_natural_query(q)

    sql = parsed.get("sql", "SELECT 1;")

    # STEP 2 — Execute SQL
    result = run_sql(sql)

    parsed["data_rows"] = result.get("rows", [])
    parsed["data_columns"] = result.get("columns", [])
    parsed["sql_error"] = result.get("error")

    return {
        "status": "ok",
        "message": "Query processed",
        "data": parsed
    }
