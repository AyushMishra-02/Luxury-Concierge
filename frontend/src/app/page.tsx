"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./globals.css";

export default function Home() {
  const [sessionId, setSessionId] = useState("");
  const [query, setQuery] = useState("");
  const [refineQuery, setRefineQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // Generate a unique session ID for this browser tab
    setSessionId(Math.random().toString(36).substring(2, 15));
  }, []);

  const fetchTrip = async (userQuery: string, isRefinement = false) => {
    if (!userQuery.trim()) return;

    setLoading(true);
    setError("");
    
    // Smooth transition simulation for first search
    if (!response && !isRefinement) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    try {
      console.log("Attempting to fetch from local proxy: /api/plan-trip");
      
      const res = await fetch(`/api/plan-trip`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: userQuery,
          session_id: sessionId
        }),
      });

      if (!res.ok) throw new Error("Our concierges are currently engaged. Please try again.");
      
      const data = await res.json();
      setResponse(data);
      if (isRefinement) setRefineQuery(""); // clear refinement input
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleInitialSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTrip(query, false);
  };

  const handleRefineSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTrip(refineQuery, true);
  };

  return (
    <>
      <div className="bg-mesh"></div>
      
      <main className={`hero-section ${response ? 'has-results' : ''}`}>
        <div className="brand-badge">The Luxury Concierge</div>
        <h1 className="title-main">
          Curating the world's most <i>extraordinary</i> escapes.
        </h1>

        <form onSubmit={handleInitialSubmit} className="search-glass">
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
            {loading && !response ? <span className="loader"></span> : "Curate My Trip"}
          </button>
        </form>

        {error && !response && <div style={{ color: "var(--gold-accent)", marginTop: "2rem", fontStyle: "italic" }}>{error}</div>}
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
          
          {/* Refine Journey Bar */}
          <div className="refine-container" style={{ marginTop: "3rem" }}>
            <form onSubmit={handleRefineSubmit} className="search-glass" style={{ margin: "0 auto", border: "1px solid var(--gold-dim)" }}>
              <input
                type="text"
                className="search-input"
                placeholder="Refine your journey (e.g., 'Make it 5 days', 'Switch to a mountain chalet')..."
                value={refineQuery}
                onChange={(e) => setRefineQuery(e.target.value)}
                disabled={loading}
                spellCheck="false"
              />
              <button type="submit" className="btn-generate" disabled={loading || !refineQuery.trim()}>
                {loading ? <span className="loader"></span> : "Update"}
              </button>
            </form>
            {error && <div style={{ color: "var(--gold-accent)", marginTop: "1rem", textAlign: "center", fontStyle: "italic" }}>{error}</div>}
          </div>
        </div>
      )}
    </>
  );
}
