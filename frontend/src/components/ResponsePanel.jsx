// components/ResponsePanel.jsx
import React, { useEffect, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { saveAs } from "file-saver";
import Papa from "papaparse";

/*
  🔧 CHANGED: ResponsePanel no longer relies on props; reads from window.latestResponse to simplify integration.
  ⭐ IMPROVED: Auto-detects numeric column for Y axis, supports Line/Bar charts, CSV export, SQL view, and table view.
*/

function rowsToObjects(columns = [], rows = []) {
  return rows.map(r => {
    const obj = {};
    for (let i = 0; i < columns.length; i++) {
      obj[columns[i]] = r[i];
    }
    return obj;
  });
}

export default function ResponsePanel({ resp: propResp }) {
  const [resp, setResp] = useState(propResp || window.latestResponse || null);

  useEffect(() => {
    const handler = () => setResp(window.latestResponse || propResp || null);
    window.addEventListener("ai-response-updated", handler);
    return () => window.removeEventListener("ai-response-updated", handler);
  }, [propResp]);

  if (!resp) {
    return <div className="small-muted">No results yet — run a query to see charts, table, and insights.</div>;
  }

  // unified format expected from backend:
  // { status, message, data: { sql, columns:[], rows:[], sql_error, sql_explain, insights, dashboard_plan, report } }
  const data = resp.data || {};
  const dataColumns = resp.columns || data.columns || [];
  const dataRows = resp.rows || data.rows || [];
  const sql = resp.sql || data.sql || "";
  const sqlExplain = data.sql_explain || "";
  const error = resp.error || data.sql_error || null;

  const objects = rowsToObjects(dataColumns, dataRows);

  // auto pick numeric column for Y
  let xKey = dataColumns[0] || null;
  let yKey = null;
  if (dataColumns.length >= 2) {
    // find first numeric column by checking sample
    for (let i = 1; i < dataColumns.length; i++) {
      const col = dataColumns[i];
      const sample = objects.find(o => o[col] !== null && o[col] !== undefined);
      if (sample && typeof sample[col] === "number") {
        yKey = col;
        break;
      }
    }
    // fallback to second column
    if (!yKey) yKey = dataColumns[1];
  }

  const chartType = resp.chart?.type || (yKey ? "line" : "bar");

  const exportCSV = () => {
    const csv = Papa.unparse(objects);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    saveAs(blob, "ai-query-results.csv");
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div>
          <h3 style={{ margin: 0 }}>Results</h3>
          <div className="small-muted">{resp.message || ""}</div>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={exportCSV}>Export CSV</button>
          <button onClick={() => navigator.clipboard.writeText(sql)}>Copy SQL</button>
        </div>
      </div>

      {error && <div style={{ marginTop: 8, color: "#ffb4b4" }}>{error}</div>}

      <div style={{ marginTop: 12 }}>
        <strong>SQL Query</strong>
        {sqlExplain && <div className="small-muted" style={{ marginBottom: 4 }}>{sqlExplain}</div>}
        <pre style={{ background: "rgba(255,255,255,0.02)", padding: 8, borderRadius: 6, fontSize: 12, overflowX: "auto" }}>{sql || "No SQL generated"}</pre>
      </div>

      <div style={{ marginTop: 12 }}>
        <strong>Chart</strong>
        <div className="chart-area" style={{ marginTop: 8 }}>
          <ResponsiveContainer width="100%" height={300}>
            {chartType === "line" ? (
              <LineChart data={objects}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={xKey} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey={yKey} stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            ) : (
              <BarChart data={objects}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={xKey} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey={yKey} barSize={36} />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ marginTop: 12 }}>
        <strong>Table</strong>
        <div className="table-wrap" style={{ marginTop: 8 }}>
          <table className="table">
            <thead>
              <tr>
                {dataColumns.map((c,i) => <th key={i}>{c}</th>)}
              </tr>
            </thead>
            <tbody>
              {objects.map((row, rIdx) => (
                <tr key={rIdx}>
                  {dataColumns.map((c,ci) => <td key={ci}>{String(row[c] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {data.insights && data.insights.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <strong>AI Insights</strong>
          <div className="small-muted" style={{ marginTop: 6 }}>
            <ul style={{ paddingLeft: 20 }}>
              {data.insights.map((s, i) => (
                <li key={i} style={{ marginBottom: 6 }}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
