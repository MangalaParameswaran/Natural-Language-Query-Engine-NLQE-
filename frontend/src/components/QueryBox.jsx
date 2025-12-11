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
  const [loadingStep, setLoadingStep] = useState("");

  const submit = async () => {
    setError(null);
    if (!query || query.trim().length < 3) {
      setError("Please type a longer query (e.g. 'Show revenue by month').");
      return;
    }
    setLoading(true);
    setLoadingStep("Sending query...");

    try {
      // Simulate progress updates
      const progressSteps = [
        "Analyzing query intent...",
        "Generating SQL query...",
        "Executing database query...",
        "Planning dashboard...",
        "Generating insights...",
        "Writing report...",
        "Finalizing results..."
      ];
      
      let stepIndex = 0;
      const progressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
          setLoadingStep(progressSteps[stepIndex]);
          stepIndex++;
        }
      }, 1000);

      const r = await axios.post("http://127.0.0.1:8000/api/query", { query });
      
      clearInterval(progressInterval);
      setLoadingStep("Processing complete!");
      
      // 🔧 CHANGED: save response into a shared place for ResponsePanel
      window.latestResponse = r.data;
      // also update history
      setHistory(prev => [{ q: query, ts: Date.now(), resp: r.data }, ...prev].slice(0, 10));
      // update insights panel if present
      const insPanel = document.getElementById("insights-panel");
      if (insPanel) {
        insPanel.innerHTML = ""; // clear
        (r.data?.data?.rows || r.data?.rows || []).slice(0,3).forEach((row, i) => {
          const el = document.createElement("div");
          el.style.color = "var(--muted)";
          el.style.fontSize = "13px";
          const data = r.data?.data || r.data;
          el.textContent = `${i+1}. ${data.columns?.[0] || "col0"}: ${row[0]}  ${data.columns?.[1] ? ` | ${data.columns[1]}: ${row[1]}` : ""}`;
          insPanel.appendChild(el);
        });
        const data = r.data?.data || r.data;
        if ((data?.rows || []).length === 0) {
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
      setLoadingStep("");
    } finally {
      setTimeout(() => {
        setLoading(false);
        setLoadingStep("");
      }, 500);
    }
  };

  const applyExample = (ex) => {
    setQuery(ex);
  };

  return (
    <div>
      <div style={{ marginBottom: 8 }} className="small-muted">Enter natural language analytics query</div>
      <div className="query-input">
        <input 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
          placeholder='Try: "Show monthly revenue last year by region"'
          disabled={loading}
          onKeyPress={(e) => e.key === 'Enter' && !loading && submit()}
        />
        <button onClick={submit} disabled={loading}>
          {loading ? "Processing..." : "Run"}
        </button>
      </div>
      {loading && loadingStep && (
        <div style={{ marginTop: 8, color: "var(--accent)", fontSize: 13 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div className="spinner" style={{ 
              width: 16, 
              height: 16, 
              border: "2px solid rgba(124,108,255,0.3)",
              borderTop: "2px solid var(--accent)",
              borderRadius: "50%",
              animation: "spin 0.8s linear infinite"
            }}></div>
            {loadingStep}
          </div>
        </div>
      )}
      {error && <div style={{ color: "#ffb4b4", marginTop: 8 }}>{error}</div>}

      <div style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={() => applyExample("Show last month sales")}>Sales</button>
        <button onClick={() => applyExample("Create a dashboard for yesterday revenue")}>Dashboard</button>
        <button onClick={() => applyExample("Top selling products last 2 months")}>Top Products</button>
        <button onClick={() => applyExample("Write a performance report for my CEO")}>Report</button>
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
