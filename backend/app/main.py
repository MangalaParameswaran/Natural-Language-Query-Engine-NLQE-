# app/main.py
import os
from fastapi import FastAPI
from app.db import connect_db, disconnect_db
from app.core import add_cors
from dotenv import load_dotenv
load_dotenv()

from app.api import router as api_router

app = FastAPI(title="AI-NLE-POC - Backend")

# Debug print (remove later)
print("-------Loaded OPENAI_API_KEY:-------", os.getenv("OPENAI_API_KEY"))
add_cors(app)
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # try to connect to DB (if available) but don't fail hard in POC
    try:
        await connect_db()
        print("--------Connected to database--------")
    except Exception as e:
        print("--------Database connection failed (continuing in mock mode):--------", e)

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await disconnect_db()
        print("--------Disconnected database--------")
    except Exception as e:
        print("--------DB disconnect error:--------", e)

@app.get("/health")
async def health():
    return {"status": "ok"}
