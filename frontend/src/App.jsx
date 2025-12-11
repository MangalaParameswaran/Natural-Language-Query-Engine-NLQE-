// App.jsx
import React, { useState, useEffect } from "react";
import QueryBox from "./components/QueryBox";
import ResponsePanel from "./components/ResponsePanel";
import DashboardPanel from "./components/DashboardPanel";
import ReportPanel from "./components/ReportPanel";
import "./App.css";

/*
  🔧 CHANGED: App now provides the full dashboard shell and layout.
  ⭐ IMPROVED: Header, top panels, and main rows for enterprise look.
*/

export default function App() {
  const [response, setResponse] = useState(null);

  useEffect(() => {
    const handler = () => setResponse(window.latestResponse || null);
    window.addEventListener("ai-response-updated", handler);
    return () => window.removeEventListener("ai-response-updated", handler);
  }, []);

  const data = response?.data || {};
  const intent = data.intent || "chart";
  const dashboardPlan = data.dashboard_plan || {};
  const report = data.report || {};

  return (
    <div className="app-shell">
      <div className="header">
        <div className="brand">
          <div style={{ width: 44, height: 44, borderRadius: 8, background: "linear-gradient(90deg,#7c6cff,#6fe7ff)", display:"flex", alignItems:"center", justifyContent:"center", fontWeight:700 }}>AI</div>
          <div>
            <h1>AI Natural Language Query Engine</h1>
            <div className="small-muted">Type plain English to run analytics — SQL, charts, dashboards & reports auto-generated</div>
          </div>
        </div>

        <div className="controls">
          <button onClick={() => { window.latestResponse = null; setResponse(null); window.location.reload(); }}>Reset</button>
        </div>
      </div>

      <div className="top-row">
        <div className="card">
          <QueryBox />
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Quick Examples</h3>
          <ul className="small-muted" style={{ paddingLeft: 20 }}>
            <li>"Show last month sales"</li>
            <li>"Create a dashboard for yesterday revenue"</li>
            <li>"Top selling products last 2 months"</li>
            <li>"Write a performance report for my CEO"</li>
            <li>"Show monthly revenue by region"</li>
          </ul>
        </div>
      </div>

      {response && (
        <>
          {/* Dashboard View - Show when intent is dashboard or when dashboard_plan exists */}
          {(intent === "dashboard" || (dashboardPlan.charts && dashboardPlan.charts.length > 0)) && (
            <div className="card" style={{ marginBottom: 16 }}>
              <h3 style={{ marginTop: 0 }}>Dashboard</h3>
              <DashboardPanel
                dashboardPlan={dashboardPlan}
                columns={data.columns || []}
                rows={data.rows || []}
              />
            </div>
          )}

          {/* Main Results Row */}
          <div className="main-row">
            <div className="card">
              <ResponsePanel />
            </div>

            <div className="card">
              <h3 style={{ marginTop: 0 }}>Insights & Reports</h3>
              {data.insights && data.insights.length > 0 && (
                <div style={{ marginBottom: 20 }}>
                  <h4 style={{ fontSize: 14, marginBottom: 8 }}>AI Insights</h4>
                  <ul className="small-muted" style={{ paddingLeft: 20 }}>
                    {data.insights.map((insight, idx) => (
                      <li key={idx} style={{ marginBottom: 8 }}>{insight}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {(intent === "report" || intent === "blog" || report.report_html) && (
                <div>
                  <h4 style={{ fontSize: 14, marginBottom: 8 }}>Executive Report</h4>
                  <ReportPanel report={report} />
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {!response && (
        <div className="main-row">
          <div className="card">
            <div className="small-muted">No query run yet. Enter a natural language query above to get started.</div>
          </div>
        </div>
      )}
    </div>
  );
}
