// components/ReportPanel.jsx
import React from "react";

export default function ReportPanel({ report }) {
  if (!report || (!report.report_html && !report.title)) {
    return <div className="small-muted">No report generated yet.</div>;
  }

  const { report_html, title } = report;

  return (
    <div className="card">
      {title && <h3 style={{ marginTop: 0, marginBottom: 16 }}>{title}</h3>}
      <div
        className="report-content"
        style={{
          lineHeight: 1.6,
          color: "#e6eef8"
        }}
        dangerouslySetInnerHTML={{ __html: report_html || "" }}
      />
    </div>
  );
}

