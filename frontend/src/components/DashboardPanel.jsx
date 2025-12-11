// components/DashboardPanel.jsx
import React from "react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";

const COLORS = ['#7c6cff', '#6fe7ff', '#ff6c9d', '#ffb84d', '#4ade80', '#a78bfa'];

function rowsToObjects(columns = [], rows = []) {
  return rows.map(r => {
    const obj = {};
    for (let i = 0; i < columns.length; i++) {
      obj[columns[i]] = r[i];
    }
    return obj;
  });
}

export default function DashboardPanel({ dashboardPlan, columns, rows }) {
  if (!dashboardPlan || !columns || !rows || rows.length === 0) {
    return <div className="small-muted">No dashboard data available.</div>;
  }

  const charts = dashboardPlan.charts || [];
  const kpis = dashboardPlan.kpis || [];
  const dataObjects = rowsToObjects(columns, rows);

  const renderChart = (chart, index) => {
    const { type, x, y, title } = chart;
    const chartData = dataObjects;

    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (type) {
      case "line":
        return (
          <div key={index} className="card" style={{ marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, marginBottom: 12 }}>{title || `Chart ${index + 1}`}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart {...commonProps}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={x} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey={y} stroke={COLORS[index % COLORS.length]} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );
      case "bar":
        return (
          <div key={index} className="card" style={{ marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, marginBottom: 12 }}>{title || `Chart ${index + 1}`}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart {...commonProps}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={x} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey={y} fill={COLORS[index % COLORS.length]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );
      case "pie":
        // For pie charts, aggregate data by x axis
        const pieData = {};
        chartData.forEach(item => {
          const key = item[x];
          const value = parseFloat(item[y]) || 0;
          pieData[key] = (pieData[key] || 0) + value;
        });
        const pieChartData = Object.entries(pieData).map(([name, value]) => ({ name, value }));
        
        return (
          <div key={index} className="card" style={{ marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, marginBottom: 12 }}>{title || `Chart ${index + 1}`}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        );
      case "area":
        return (
          <div key={index} className="card" style={{ marginBottom: 16 }}>
            <h4 style={{ marginTop: 0, marginBottom: 12 }}>{title || `Chart ${index + 1}`}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart {...commonProps}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={x} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey={y} stroke={COLORS[index % COLORS.length]} fill={COLORS[index % COLORS.length]} fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      {kpis.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 24 }}>
          {kpis.map((kpi, idx) => (
            <div key={idx} className="card" style={{ textAlign: "center", padding: 16 }}>
              <div className="small-muted" style={{ fontSize: 12, marginBottom: 8 }}>{kpi.label || `KPI ${idx + 1}`}</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--accent)" }}>
                {kpi.value !== null && kpi.value !== undefined ? kpi.value : "—"}
              </div>
              {kpi.description && (
                <div className="small-muted" style={{ fontSize: 11, marginTop: 4 }}>{kpi.description}</div>
              )}
              {kpi.trend && (
                <div style={{ fontSize: 11, marginTop: 4, color: kpi.trend === "up" ? "#4ade80" : kpi.trend === "down" ? "#ff6c9d" : "var(--muted)" }}>
                  {kpi.trend === "up" ? "↑" : kpi.trend === "down" ? "↓" : "→"} {kpi.trend}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {charts.length > 0 ? (
        <div>
          {charts.map((chart, idx) => renderChart(chart, idx))}
        </div>
      ) : (
        <div className="small-muted">No charts defined in dashboard plan.</div>
      )}
    </div>
  );
}

