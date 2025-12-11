# orchestrator.py
import logging
from app.db import get_database_schema, run_sql
from app.llm_agents.router_agent import decide_intent
from app.llm_agents.sql_agent import generate_sql
from app.llm_agents.dashboard_agent import plan_dashboard
from app.llm_agents.insight_agent import generate_insights
from app.llm_agents.narrative_agent import write_report

logger = logging.getLogger(__name__)

async def orchestrate_query(user_query: str) -> dict:
    logger.info(f"🚀 Starting orchestration for query: '{user_query}'")
    
    schema_text = get_database_schema()
    logger.info(f"📊 Schema retrieved: {len(schema_text)} characters")

    # 1. Decide intent
    logger.info("🔍 Step 1/6: Deciding intent...")
    try:
        intent_res = await decide_intent(schema_text, user_query)
        intent = intent_res.get("intent", "chart")
        logger.info(f"✅ Intent determined: {intent}")
        logger.info(f"   Router response: {intent_res}")
    except Exception as e:
        logger.error(f"❌ Error in intent detection: {e}")
        intent_res = {"intent": "chart", "reason": f"Error: {str(e)}"}
        intent = "chart"

    # 2. Generate SQL (always try)
    logger.info("💾 Step 2/6: Generating SQL...")
    try:
        sql_res = await generate_sql(schema_text, user_query)
        sql = sql_res.get("sql", "")
        logger.info(f"✅ SQL generated: {len(sql)} characters")
        logger.info(f"   SQL preview: {sql[:100]}..." if len(sql) > 100 else f"   SQL: {sql}")
    except Exception as e:
        logger.error(f"❌ Error in SQL generation: {e}")
        sql_res = {"sql": "", "explain": f"Error: {str(e)}"}
        sql = ""

    out = {"intent": intent, "router": intent_res, "sql_plan": sql_res}

    # 3. Execute SQL if present
    logger.info("🗄️ Step 3/6: Executing SQL...")
    if sql:
        try:
            db_res = run_sql(sql)
            out["rows"] = db_res.get("rows", [])
            out["columns"] = db_res.get("columns", [])
            out["sql_error"] = db_res.get("error")
            if out["sql_error"]:
                logger.warning(f"⚠️ SQL execution error: {out['sql_error']}")
            else:
                logger.info(f"✅ SQL executed successfully: {len(out['rows'])} rows returned")
        except Exception as e:
            logger.error(f"❌ Error executing SQL: {e}")
            out["rows"] = []
            out["columns"] = []
            out["sql_error"] = str(e)
    else:
        logger.warning("⚠️ No SQL to execute")
        out["rows"] = []
        out["columns"] = []
        out["sql_error"] = "No SQL generated"

    # 4. Dashboard plan
    logger.info("📈 Step 4/6: Planning dashboard...")
    try:
        out["dashboard_plan"] = await plan_dashboard(schema_text, user_query)
        logger.info(f"✅ Dashboard planned: {len(out['dashboard_plan'].get('charts', []))} charts, {len(out['dashboard_plan'].get('kpis', []))} KPIs")
    except Exception as e:
        logger.error(f"❌ Error in dashboard planning: {e}")
        out["dashboard_plan"] = {"charts": [], "kpis": []}

    # 5. Insights (use small sample) - only if we have data
    logger.info("💡 Step 5/6: Generating insights...")
    if out["rows"] and len(out["rows"]) > 0:
        try:
            sample = out["rows"][:20]
            insights_result = await generate_insights(out["columns"], sample, user_query)
            out["insights"] = insights_result.get("insights", [])
            logger.info(f"✅ Insights generated: {len(out['insights'])} insights")
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            out["insights"] = []
    else:
        logger.info("⏭️ Skipping insights (no data)")
        out["insights"] = []

    # 6. Narrative / Report
    logger.info("📝 Step 6/6: Writing report...")
    try:
        summary = sql_res.get("explain", "")
        report_result = await write_report(summary, out["insights"], user_query)
        out["report"] = {
            "report_html": report_result.get("report_html", ""),
            "title": report_result.get("title", "Analytics Report")
        }
        logger.info(f"✅ Report generated: {len(out['report']['report_html'])} characters")
    except Exception as e:
        logger.error(f"❌ Error writing report: {e}")
        out["report"] = {
            "report_html": f"<p>Error generating report: {str(e)}</p>",
            "title": "Analytics Report"
        }

    logger.info("🎉 Orchestration complete!")
    return out
