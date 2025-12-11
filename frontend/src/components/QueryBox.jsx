// components/QueryBox.jsx
import React, { useState } from "react";
import axios from "axios";

/*
  🔧 CHANGED: QueryBox now updates global window.latestResponse so ResponsePanel can read without prop drilling.
  ⭐ IMPROVED: Adds history, simple validation, and friendly UI.
*/

export default function QueryBox() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const submit = async () => {
    setError(null);
    if (!query || query.trim().length < 3) {
      setError("Please type a longer query (e.g. 'Show revenue by month').");
      return;
    }
    setLoading(true);

    try {
      const r = await axios.post("http://127.0.0.1:8000/api/query", { query });
      // 🔧 CHANGED: save response into a shared place for ResponsePanel
      window.latestResponse = r.data;
      // also update history
      setHistory(prev => [{ q: query, ts: Date.now(), resp: r.data }, ...prev].slice(0, 10));
      // update insights panel if present
      const insPanel = document.getElementById("insights-panel");
      if (insPanel) {
        insPanel.innerHTML = ""; // clear
        (r.data?.rows || []).slice(0,3).forEach((row, i) => {
          const el = document.createElement("div");
          el.style.color = "var(--muted)";
          el.style.fontSize = "13px";
          el.textContent = `${i+1}. ${r.data.columns?.[0] || "col0"}: ${row[0]}  ${r.data.columns?.[1] ? ` | ${r.data.columns[1]}: ${row[1]}` : ""}`;
          insPanel.appendChild(el);
        });
        if ((r.data?.rows || []).length === 0) {
          const el = document.createElement("div");
          el.style.color = "var(--muted)";
          el.textContent = "No rows returned.";
          insPanel.appendChild(el);
        }
      }
      // trigger manual event so ResponsePanel can refresh
      window.dispatchEvent(new CustomEvent("ai-response-updated"));
    } catch (e) {
      console.error(e);
      setError(e.response?.data?.detail || e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const applyExample = (ex) => {
    setQuery(ex);
  };

  return (
    <div>
      <div style={{ marginBottom: 8 }} className="small-muted">Enter natural language analytics query</div>
      <div className="query-input">
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder='Try: "Show monthly revenue last year by region"' />
        <button onClick={submit} disabled={loading}>{loading ? "Running..." : "Run"}</button>
      </div>
      {error && <div style={{ color: "#ffb4b4", marginTop: 8 }}>{error}</div>}

      <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
        <button onClick={() => applyExample("Show monthly revenue last year by region")}>Example 1</button>
        <button onClick={() => applyExample("Top 10 customers by profit")}>Example 2</button>
        <button onClick={() => applyExample("Compare sales vs marketing spend by quarter")}>Example 3</button>
      </div>

      {history.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <div className="small-muted">Recent</div>
          <ul style={{ marginTop: 6 }}>
            {history.map((h, i) => <li key={i} className="small-muted">{new Date(h.ts).toLocaleTimeString()} — {h.q}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
