# 🤖 AI-Powered NLQ Analytics Engine

A complete **Natural Language Query (NLQ) Analytics Engine** that transforms plain English queries into SQL queries, interactive dashboards, AI-generated insights, and executive reports.

## ✨ Features

- **Natural Language Processing**: Type queries in plain English
- **Multi-LLM Architecture**: Specialized AI agents for different tasks
- **SQL Generation**: Automatic PostgreSQL query generation
- **Interactive Dashboards**: Multiple chart types (Line, Bar, Pie, Area)
- **KPI Cards**: Key performance indicators
- **AI Insights**: Automated analytical insights
- **Executive Reports**: Professional HTML reports for CEOs
- **Rate Limit Handling**: Automatic retry with exponential backoff

## 🏗️ Architecture

### Multi-LLM System

1. **Router Agent** - Intent classification (SQL, Chart, Dashboard, Insights, Report, Blog, KPI)
2. **SQL Agent** - PostgreSQL query generation (strict schema adherence)
3. **Dashboard Agent** - Chart and KPI planning
4. **Insight Agent** - Analytical insights generation
5. **Narrative Agent** - Report/blog writing

### Tech Stack

- **Backend**: Python, FastAPI, PostgreSQL, OpenAI API
- **Frontend**: React, Vite, Recharts
- **Database**: PostgreSQL (retail schema)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- OpenAI API Key

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up environment variables** (create `.env` file):
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
SQL_MODEL=gpt-4o-mini
ROUTER_MODEL=gpt-4o-mini
DASHBOARD_MODEL=gpt-4o-mini
NARRATIVE_MODEL=gpt-4o-mini

DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```

3. **Set up database**:
```bash
# Create database
createdb your_database

# Run schema
psql your_database < schema.sql

# Seed data (optional)
python seed_db.py
```

4. **Run backend**:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Run frontend**:
```bash
npm run dev
```

3. **Access application**: http://localhost:5173

## 📝 Example Queries

- `"Show last month sales"`
- `"Create a dashboard for yesterday revenue"`
- `"Top selling products last 2 months"`
- `"Write a performance report for my CEO"`
- `"Show monthly revenue by region"`
- `"Compare sales by product category"`

## 🗄️ Database Schema

The system works with a retail database schema:

- **customers** - Customer information
- **products** - Product catalog
- **sales** - Sales transactions (time-series)
- **invoices** - Invoice records
- **returns** - Return transactions
- **regions** - Geographic regions

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `OPENAI_MODEL` - Default model (default: gpt-4o-mini)
- `SQL_MODEL` - Model for SQL generation
- `ROUTER_MODEL` - Model for intent classification
- `DASHBOARD_MODEL` - Model for dashboard planning
- `NARRATIVE_MODEL` - Model for report generation

### Rate Limiting

The system includes automatic rate limit handling with:
- Exponential backoff
- Retry-after time extraction
- Up to 5 retry attempts
- Non-blocking async execution

## 📊 API Endpoints

### POST `/api/query`

Process a natural language query.

**Request**:
```json
{
  "query": "Show last month sales"
}
```

**Response**:
```json
{
  "status": "ok",
  "message": "Query processed successfully",
  "data": {
    "intent": "dashboard",
    "sql": "SELECT ...",
    "columns": ["month", "revenue"],
    "rows": [[...], [...]],
    "dashboard_plan": {
      "charts": [...],
      "kpis": [...]
    },
    "insights": ["...", "..."],
    "report": {
      "title": "...",
      "report_html": "<div>...</div>"
    }
  }
}
```

## 🎨 Frontend Components

- **QueryBox** - Natural language input
- **ResponsePanel** - SQL, charts, and table results
- **DashboardPanel** - Multi-chart dashboard with KPIs
- **ReportPanel** - Executive report rendering

## 🔒 Security

- SQL injection protection (read-only queries)
- CORS configuration for frontend
- Environment variable management
- Rate limit handling

## 📈 Performance

- Async/await for non-blocking operations
- Thread pool execution for OpenAI API calls
- Efficient database queries with LIMIT clauses
- Optimized frontend rendering

## 🐛 Troubleshooting

### Rate Limit Errors

The system automatically handles rate limits with retries. If you see persistent errors:
- Check your OpenAI API quota
- Verify your API key is valid
- Consider upgrading your OpenAI plan

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists and schema is loaded

### Frontend Not Loading

- Verify backend is running on port 8000
- Check CORS configuration
- Verify frontend is on port 5173

## 📚 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.
