// App.jsx
import React from "react";
import QueryBox from "./components/QueryBox";
import ResponsePanel from "./components/ResponsePanel";
import "./app.css";

/*
  🔧 CHANGED: App now provides the full dashboard shell and layout.
  ⭐ IMPROVED: Header, top panels, and main rows for enterprise look.
*/

export default function App() {
  return (
    <div className="app-shell">
      <div className="header">
        <div className="brand">
          <div style={{ width: 44, height: 44, borderRadius: 8, background: "linear-gradient(90deg,#7c6cff,#6fe7ff)", display:"flex", alignItems:"center", justifyContent:"center", fontWeight:700 }}>AI</div>
          <div>
            <h1>AI Natural Language Query Engine</h1>
            <div className="small-muted">Type plain English to run analytics — SQL & chart auto-generated</div>
          </div>
        </div>

        <div className="controls">
          <button onClick={() => window.location.reload()}>Reset</button>
        </div>
      </div>

      <div className="top-row">
        <div className="card">
          <QueryBox />
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Quick Tips</h3>
          <ul className="small-muted">
            <li>Try: "Show monthly revenue last year by region"</li>
            <li>Try: "Top 10 customers by profit"</li>
            <li>Try: "Compare sales vs marketing spend by quarter"</li>
          </ul>
        </div>
      </div>

      <div className="main-row">
        <div className="card">
          <ResponsePanel />
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Insights & Reports</h3>
          <div className="insights" id="insights-panel">
            <div className="small-muted">No query run yet.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
