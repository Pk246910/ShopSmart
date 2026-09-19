import React, { useState } from "react";
import { ClipboardPaste } from "lucide-react";
import API from "../api/axios";

const PLATFORMS = [
  { name: "Amazon", icon: "🛒", color: "#f59e0b" },
  { name: "Flipkart", icon: "🛍️", color: "#3b82f6" },
  { name: "Myntra", icon: "👗", color: "#ec4899" },
  { name: "AJIO", icon: "👟", color: "#8b5cf6" },
  { name: "Meesho", icon: "🏷️", color: "#f43f5e" },
  { name: "Croma", icon: "📺", color: "#06b6d4" },
  { name: "Reliance Digital", icon: "🏪", color: "#10b981" },
  { name: "Tata CLiQ", icon: "🏬", color: "#6366f1" },
];

const ANALYSIS_STEPS = [
  "Detecting platform...",
  "Retrieving product page...",
  "Extracting product information...",
  "Validating product data...",
  "Finding matching listings...",
  "Comparing prices across platforms...",
  "Preparing comparison...",
];

const UrlAnalyzer = ({ onResult, onLoading }) => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [step, setStep] = useState("");
  const [stepIndex, setStepIndex] = useState(0);

  const isValidUrl = (str) => {
    try {
      const u = new URL(str.startsWith("http") ? str : `https://${str}`);
      return u.protocol === "http:" || u.protocol === "https:";
    } catch {
      return false;
    }
  };

  const advanceStep = async (idx) => {
    if (idx < ANALYSIS_STEPS.length) {
      setStep(ANALYSIS_STEPS[idx]);
      setStepIndex(idx);
      await new Promise((r) => setTimeout(r, 300 + Math.random() * 200));
    }
  };

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError("Please enter a product URL");
      return;
    }
    if (!isValidUrl(url.trim())) {
      setError("Please enter a valid URL");
      return;
    }

    setLoading(true);
    setError(null);
    onLoading?.(true);

    try {
      await advanceStep(0);
      await advanceStep(1);
      await advanceStep(2);

      // Analysis does live scraping + comparison + rule-based scoring, so it
      // needs a longer budget than the global 10s axios timeout.
      const res = await API.post("/analyze-url/", { url: url.trim() }, { timeout: 120000 });

      await advanceStep(3);
      await advanceStep(4);
      await advanceStep(5);
      await advanceStep(6);

      onResult?.(res.data);
    } catch (err) {
      const data = err.response?.data;
      if (data?.supported_platforms) {
        setError(`Platform not supported. Supported: ${data.supported_platforms.join(", ")}`);
      } else {
        setError(data?.error || "Analysis failed. Please try another URL.");
      }
      onResult?.(null);
    } finally {
      setLoading(false);
      setStep("");
      setStepIndex(0);
      onLoading?.(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !loading) handleAnalyze();
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text);
        setError(null);
      }
    } catch {}
  };

  return (
    <div style={{ width: "100%" }}>
      <div style={{ display: "flex", gap: "0.75rem", alignItems: "stretch" }}>
        <div style={{ flex: 1, position: "relative" }}>
          <input
            type="url"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setError(null); }}
            onKeyDown={handleKeyDown}
            placeholder="Paste a product URL (e.g., https://www.flipkart.com/...)"
            disabled={loading}
            aria-label="Product URL"
            style={{
              width: "100%",
              padding: "0.85rem 5.5rem 0.85rem 2.8rem",
              background: "var(--bg-card)",
              border: `1px solid ${error ? "var(--accent-rose)" : "var(--border-color)"}`,
              borderRadius: "12px",
              color: "var(--text-primary)",
              fontSize: "0.95rem",
              outline: "none",
              transition: "all 0.2s ease",
            }}
          />
          <span style={{
            position: "absolute",
            left: "0.9rem",
            top: "50%",
            transform: "translateY(-50%)",
            fontSize: "1.1rem",
            opacity: 0.5,
          }}>🔗</span>
          <div style={{
            position: "absolute",
            right: "0.5rem",
            top: "50%",
            transform: "translateY(-50%)",
            display: "flex",
            gap: "0.25rem",
          }}>
            {!loading && (
              <button
                onClick={handlePaste}
                style={{
                  background: "var(--border-color)",
                  border: "none",
                  borderRadius: "6px",
                  width: 30,
                  height: 30,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  color: "var(--text-secondary)",
                  transition: "all 0.15s ease",
                }}
                title="Paste from clipboard"
                aria-label="Paste URL"
              >
                <ClipboardPaste size={14} />
              </button>
            )}
            {url && !loading && (
              <button
                onClick={() => { setUrl(""); setError(null); onResult?.(null); }}
                style={{
                  background: "var(--border-color)",
                  border: "none",
                  borderRadius: "6px",
                  width: 30,
                  height: 30,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  color: "var(--text-secondary)",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  transition: "all 0.15s ease",
                }}
                title="Clear"
                aria-label="Clear URL"
              >
                ✕
              </button>
            )}
          </div>
        </div>
        <button
          onClick={handleAnalyze}
          disabled={loading || !url.trim()}
          style={{
            padding: "0.85rem 1.75rem",
            background: loading ? "var(--text-muted)" : "var(--gradient-brand)",
            color: "#fff",
            border: "none",
            borderRadius: "12px",
            fontWeight: 700,
            fontSize: "0.95rem",
            cursor: loading ? "not-allowed" : "pointer",
            whiteSpace: "nowrap",
            transition: "all 0.2s ease",
            opacity: !url.trim() ? 0.5 : 1,
          }}
        >
          {loading ? "Analyzing..." : "🔍 Analyze Product"}
        </button>
      </div>

      {loading && step && (
        <div style={{
          marginTop: "0.75rem",
          padding: "0.75rem 1rem",
          background: "rgba(6, 182, 212, 0.1)",
          border: "1px solid rgba(6, 182, 212, 0.25)",
          borderRadius: "10px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.5rem" }}>
            <div className="spinner" />
            <span style={{ fontSize: "0.88rem", color: "var(--accent-cyan)", fontWeight: 600 }}>{step}</span>
          </div>
          <div style={{ display: "flex", gap: "4px" }}>
            {ANALYSIS_STEPS.map((_, i) => (
              <div key={i} style={{
                flex: 1,
                height: 3,
                borderRadius: 2,
                background: i <= stepIndex ? "var(--accent-cyan)" : "var(--border-color)",
                transition: "background 0.3s ease",
              }} />
            ))}
          </div>
        </div>
      )}

      {error && (
        <div style={{
          marginTop: "0.75rem",
          padding: "0.75rem 1rem",
          background: "rgba(244, 63, 94, 0.1)",
          border: "1px solid rgba(244, 63, 94, 0.25)",
          borderRadius: "10px",
          fontSize: "0.88rem",
          color: "var(--accent-rose)",
        }}>
          {error}
        </div>
      )}
    </div>
  );
};

export default UrlAnalyzer;
