# app/core.py
from fastapi.middleware.cors import CORSMiddleware

def add_cors(app):
    # for local development allow frontend at default Vite ports 5173 and 5174
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
