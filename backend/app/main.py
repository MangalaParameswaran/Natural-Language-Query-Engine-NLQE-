# app/main.py

# >>> CHANGE START (imports organized)
import os
from fastapi import FastAPI
from dotenv import load_dotenv

from app.core import add_cors
from app.db import connect_db, disconnect_db
from app.api import router as api_router

load_dotenv()

app = FastAPI(title="AI-NLE-POC - Backend")

# Centralized CORS configuration
add_cors(app)

# Clean API routing
app.include_router(api_router, prefix="/api")


# Enterprise-style startup hook
@app.on_event("startup")
async def startup_event():
    try:
        await connect_db()
        print("✅ Database connected")
    except Exception as e:
        print("❌ Database connection failed:", e)


# Enterprise-style shutdown hook
@app.on_event("shutdown")
async def shutdown_event():
    try:
        await disconnect_db()
        print("🔌 Database connection closed")
    except Exception as e:
        print("❌ DB disconnect error:", e)


@app.get("/health")
async def health():
    return {"status": "ok"}
