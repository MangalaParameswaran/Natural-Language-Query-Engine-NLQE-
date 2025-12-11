# app/main.py

# >>> CHANGE START (imports organized)
import os
import logging
from fastapi import FastAPI
from dotenv import load_dotenv

from app.core import add_cors
from app.db import connect_db, disconnect_db
from app.api import router as api_router

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-NLE-POC - Backend")

# Centralized CORS configuration
add_cors(app)

# Clean API routing
app.include_router(api_router, prefix="/api")


# Enterprise-style startup hook
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting AI-NLE-POC Backend...")
    try:
        await connect_db()
        logger.info("✅ Database connected")
        print("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        print("❌ Database connection failed:", e)


# Enterprise-style shutdown hook
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down AI-NLE-POC Backend...")
    try:
        await disconnect_db()
        logger.info("🔌 Database connection closed")
        print("🔌 Database connection closed")
    except Exception as e:
        logger.error(f"❌ DB disconnect error: {e}")
        print("❌ DB disconnect error:", e)


@app.get("/health")
async def health():
    return {"status": "ok"}
