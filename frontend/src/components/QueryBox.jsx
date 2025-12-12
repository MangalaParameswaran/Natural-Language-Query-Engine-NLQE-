import React, { useState, useEffect } from "react";
import axios from "axios";

export default function QueryBox() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  // ---------- Load history ----------
  useEffect(() => {
    try {
      const raw = localStorage.getItem("queryHistory");
      if (!raw) return;

      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        setHistory(parsed);
      } else {
        setHistory([]);
      }
    } catch (e) {
      console.warn("History corrupted → clearing", e);
      localStorage.removeItem("queryHistory");
      setHistory([]);
    }
  }, []);

  // ---------- Save history ----------
  useEffect(() => {
    localStorage.setItem("queryHistory", JSON.stringify(history));
  }, [history]);

  const submit = async () => {
    setError(null);
    if (!query || query.trim().length < 3) {
      setError("Please type a longer query.");
      return;
    }

    setLoading(true);

    try {
      // Uncomment below when backend is ready
      // const r = await axios.post("http://localhost:8000/api/query", { query });
      // window.latestResponse = r.data;

      const newHistory = [{ q: query, ts: Date.now() }, ...history].slice(0, 10);
      setHistory(newHistory);

      setSuggestions([]);
      window.dispatchEvent(new CustomEvent("ai-response-updated"));
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  // ---------- Voice Input ----------
  const startListening = () => {
    if (!("webkitSpeechRecognition" in window)) {
      setError("Voice input is not supported in this browser.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setIsListening(false);
      recognition.stop();
      submit();
    };

    recognition.onerror = (event) => {
      setError("Voice input error: " + event.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  const applyExample = (ex) => setQuery(ex);

  return (
    <div>
      <div style={{ marginBottom: 8 }} className="small-muted">
        Enter natural language analytics query
      </div>

      {/* Input with suggestions */}
      <div style={{ position: "relative" }}>
        <input
          value={query}
          onChange={(e) => {
            const value = e.target.value;
            setQuery(value);

            if (value.trim().length > 0) {
              const filtered = history.filter((h) =>
                h.q.toLowerCase().includes(value.toLowerCase())
              );
              setSuggestions(filtered.slice(0, 5));
            } else {
              setSuggestions([]);
            }
          }}
          placeholder='Try: "Show monthly revenue last year by region"'
          style={{ width: "100%", padding: "8px" }}
        />

        {suggestions.length > 0 && (
          <div
            style={{
              background: "#fff",
              border: "1px solid #ddd",
              marginTop: 2,
              borderRadius: 4,
              position: "absolute",
              zIndex: 9999,
              width: "100%",
              boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              maxHeight: "200px",
              overflowY: "auto",
              padding: "4px 0",
            }}
          >
            {suggestions.map((s, i) => (
              <div
                key={i}
                style={{
                  padding: "8px 12px",
                  cursor: "pointer",
                  borderBottom: i !== suggestions.length - 1 ? "1px solid #eee" : "none",
                  backgroundColor: "#fff",
                  color: "#000", // Black text visible
                }}
                onMouseDown={() => {
                  setQuery(s.q);
                  setSuggestions([]);
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#f0f0f0"}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#fff"}
              >
                {s.q}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Buttons */}
      <div
        className="query-input"
        style={{ marginTop: 8, display: "flex", gap: "8px", flexWrap: "wrap" }}
      >
        <button
          onClick={startListening}
          disabled={isListening}
          style={{ flex: "1 1 auto", minWidth: 120 }}
        >
          {isListening ? "Listening..." : "🎤 Voice Input"}
        </button>

        <button
          onClick={submit}
          disabled={loading}
          style={{ flex: "1 1 auto", minWidth: 120 }}
        >
          {loading ? "Running..." : "Run"}
        </button>
      </div>

      {error && <div style={{ color: "#ffb4b4", marginTop: 8 }}>{error}</div>}

      {/* Examples */}
      <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
        <button onClick={() => applyExample("Show monthly revenue last year by region")}>
          Example 1
        </button>
        <button onClick={() => applyExample("Top 10 customers by profit")}>
          Example 2
        </button>
        <button onClick={() => applyExample("Compare sales vs marketing spend by quarter")}>
          Example 3
        </button>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <h3>History</h3>
          <ul style={{ marginTop: 6 }}>
            {history.map((h, i) => (
              <li key={i} className="small-muted">
                {new Date(h.ts).toLocaleTimeString()} — {h.q}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}