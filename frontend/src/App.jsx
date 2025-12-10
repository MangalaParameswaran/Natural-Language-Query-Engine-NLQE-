import React from "react";
import QueryBox from "./components/QueryBox";
import ResponsePanel from "./components/ResponsePanel";

export default function App() {
  return (
    <div style={{ fontFamily: "Inter, Arial, sans-serif", padding: 24 }}>
      <h2>AI-Powered Natural Language Query Engine — POC</h2>
      <QueryBox />
    </div>
  );
}
