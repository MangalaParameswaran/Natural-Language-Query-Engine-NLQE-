import React from "react";

export default function ResponsePanel({ resp }) {
  const data = resp?.data || {};
  return (
    <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 6 }}>
      <h3>Result</h3>
      <div><strong>Message:</strong> {resp.message}</div>
      <div style={{ marginTop: 8 }}>
        <strong>Planned SQL:</strong>
        <pre style={{ background: "#f6f6f6", padding: 8, borderRadius: 4 }}>{data.sql}</pre>
      </div>

      <div style={{ marginTop: 8 }}>
        <strong>Suggested Chart:</strong> {JSON.stringify(data.chart)}
      </div>

      <div style={{ marginTop: 8 }}>
        <strong>Rows (sample):</strong>
        <pre style={{ background: "#f6f6f6", padding: 8 }}>
          {JSON.stringify(data.rows, null, 2)}
        </pre>
      </div>

      <div style={{ marginTop: 8 }}>
        <strong>Insights:</strong>
        <ul>
          {(data.insights || []).map((x, i) => <li key={i}>{x}</li>)}
        </ul>
      </div>
    </div>
  );
}
