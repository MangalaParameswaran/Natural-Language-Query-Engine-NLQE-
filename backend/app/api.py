# app/api.py
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
        raise HTTPException(status_code=400, detail="Query field cannot be empty")

    # Step 1 — LLM natural language → SQL conversion
    parsed = await parse_natural_query(q)

    sql = parsed.get("sql", "").strip()
    if not sql:
        return {
            "status": "error",
            "message": "LLM did not return SQL",
            "data": parsed
        }

    # Step 2 — Execute SQL safely
    result = run_sql(sql)

    rows = result.get("rows", [])
    cols = result.get("columns", [])
    err = result.get("error")
    parsed["data_rows"] = rows
    parsed["data_columns"] = cols
    parsed["sql_error"] = err

    # If SQL error
    if err:
        return {
            "status": "error",
            "message": "SQL execution failed",
            "data": parsed
        }

    # No data
    if len(rows) == 0:
        return {
            "status": "ok",
            "message": "No data found",
            "data": parsed
        }

    return {
        "status": "ok",
        "message": "Query processed",
        "data": parsed
    }
