"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./globals.css";

export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    
    // Reset view if asking a new question
    if (!response) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    try {
      const res = await fetch("http://localhost:8000/api/plan-trip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error("Our concierges are currently engaged. Please try again.");
      
      const data = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="bg-mesh"></div>
      
      <main className={`hero-section ${response ? 'has-results' : ''}`}>
        <div className="brand-badge">The Luxury Concierge</div>
        <h1 className="title-main">
          Curating the world's most <i>extraordinary</i> escapes.
        </h1>

        <form onSubmit={handleSubmit} className="search-glass">
          <input
            type="text"
            className="search-input"
            placeholder="E.g., A private villa in Tuscany for wine tasting..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            spellCheck="false"
          />
          <button type="submit" className="btn-generate" disabled={loading || !query.trim()}>
            {loading ? <span className="loader"></span> : "Curate My Trip"}
          </button>
        </form>

        {error && <div style={{ color: "var(--gold-accent)", marginTop: "2rem", fontStyle: "italic" }}>{error}</div>}
      </main>

      {response && (
        <div className="results-container">
          <div className="editorial-card">
            <div className="prose">
              <ReactMarkdown>{response.parsed_requirements}</ReactMarkdown>
            </div>
          </div>

          <div className="editorial-card">
            <div className="prose">
              <ReactMarkdown>{response.hotel_options}</ReactMarkdown>
            </div>
          </div>

          <div className="editorial-card" style={{ borderTop: "2px solid var(--gold-accent)" }}>
            <div className="prose">
              <ReactMarkdown>{response.final_itinerary}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
