# AI-NLE-POC (starter)

Folders:
- backend : FastAPI app
- frontend: React + Vite app

1) Start Postgres (see below)
2) Backend (Windows cmd)
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nlp_analytics
   uvicorn app.main:app --reload

3) Frontend (Windows cmd)
   cd frontend
   npm install
   npm run dev

Open: http://localhost:5173 -> frontend UI
Backend: http://127.0.0.1:8000


flowchart LR
  UI[React (Vite) UI]
  UI -->|NL Query| BackendAPI[FastAPI / API Gateway]
  BackendAPI --> LLM[OpenAI GPT (LLM)]
  BackendAPI --> Planner[Query Planner / Intent Detector]
  Planner --> DB[PostgreSQL]
  DB --> BackendAPI
  BackendAPI --> FEChart[Visualization Engine / Chart metadata]
  FEChart --> UI
  subgraph optional
    Memory[Memory Layer / Cache]
    Feedback[User Feedback Loop]
  end
  LLM --- Memory
  BackendAPI --- Feedback
