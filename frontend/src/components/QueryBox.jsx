import React, { useState } from "react";
import axios from "axios";
import ResponsePanel from "./ResponsePanel";

export default function QueryBox() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState(null);
  const [error, setError] = useState(null);

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await axios.post("http://127.0.0.1:8000/api/query", { query });
      setResp(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setResp(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 900 }}>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          style={{ flex: 1, padding: 10, fontSize: 16 }}
          placeholder='Try: "Show monthly revenue last year by region"'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={submit} disabled={loading} style={{ padding: "10px 16px" }}>
          {loading ? "Running..." : "Run"}
        </button>
      </div>

      {error && <div style={{ marginTop: 12, color: "red" }}>{error}</div>}

      {resp && (
        <div style={{ marginTop: 16 }}>
          <ResponsePanel resp={resp} />
        </div>
      )}
    </div>
  );
}
