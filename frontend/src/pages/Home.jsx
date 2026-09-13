import React, { useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import UrlAnalyzer from "../components/UrlAnalyzer";
import AnalysisResult from "../components/AnalysisResult";

const CATEGORIES = [
  { name: "Smartphones", icon: "📱", color: "#3b82f6" },
  { name: "Laptops", icon: "💻", color: "#8b5cf6" },
  { name: "Headphones", icon: "🎧", color: "#f43f5e" },
  { name: "Tablets", icon: "📱", color: "#06b6d4" },
  { name: "TVs", icon: "📺", color: "#10b981" },
  { name: "Footwear", icon: "👟", color: "#f59e0b" },
  { name: "Fashion", icon: "👗", color: "#ec4899" },
  { name: "Kitchen", icon: "🍳", color: "#ef4444" },
  { name: "Watches", icon: "⌚", color: "#6366f1" },
  { name: "Cameras", icon: "📷", color: "#0ea5e9" },
  { name: "Speakers", icon: "🔊", color: "#a855f7" },
  { name: "Gaming", icon: "🎮", color: "#22c55e" },
];

const Home = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleResult = useCallback((data) => {
    setLoading(false);
    if (data && data.id) {
      navigate(`/analysis/${data.id}`, { state: { analysis: data } });
    } else {
      setResult(data);
    }
  }, [navigate]);

  const handleLoading = useCallback((isLoading) => {
    setLoading(isLoading);
    if (isLoading) setResult(null);
  }, []);

  return (
    <div className="app-wrapper" style={{ padding: "0 1.5rem 4rem", maxWidth: 1100, margin: "0 auto" }}>
      {/* Hero Section */}
      <section style={{ textAlign: "center", padding: "3rem 0 2rem" }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.4rem",
          padding: "0.35rem 0.9rem",
          background: "rgba(6, 182, 212, 0.1)",
          border: "1px solid rgba(6, 182, 212, 0.25)",
          borderRadius: "999px",
          color: "var(--accent-cyan)",
          fontSize: "0.8rem",
          fontWeight: 700,
          marginBottom: "1.25rem",
          animation: "fadeInDown 0.5s ease both",
        }}>
          🤖 AI-Powered Comparison
        </div>
        <h1 style={{ fontSize: "2.75rem", fontWeight: 800, marginBottom: "0.75rem", letterSpacing: "-0.03em", animation: "fadeInDown 0.5s 0.1s ease both" }}>
          Paste. Compare.{" "}
          <span style={{ background: "var(--gradient-brand)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            Save.
          </span>
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", maxWidth: 620, margin: "0 auto 2.5rem", lineHeight: 1.6, animation: "fadeInDown 0.5s 0.2s ease both" }}>
          Paste a product URL from any supported platform. ShopSmart identifies the product,
          compares prices across <strong style={{ color: "var(--accent-cyan)" }}>8 platforms</strong>, and recommends the best deal with AI.
        </p>
      </section>

      {/* URL Analyzer */}
      <div style={{
        background: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "16px",
        padding: "1.5rem",
        boxShadow: "var(--shadow-card)",
        marginBottom: "2.5rem",
        animation: "slideUp 0.4s 0.3s ease both",
      }}>
        <UrlAnalyzer onResult={handleResult} onLoading={handleLoading} />
      </div>

      {/* Results */}
      {loading && (
        <div style={{
          textAlign: "center",
          padding: "3rem",
          color: "var(--text-secondary)",
          animation: "fadeIn 0.3s ease",
        }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem", animation: "pulse 1.5s ease-in-out infinite" }}>⏳</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "0.25rem" }}>Analyzing product...</div>
          <div style={{ fontSize: "0.88rem" }}>Comparing across platforms and calculating best deal</div>
        </div>
      )}

      {!loading && result && (
        <AnalysisResult data={result} />
      )}

      {/* Empty State */}
      {!loading && !result && (
        <>
          {/* How It Works */}
          <div style={{ marginBottom: "3rem" }}>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 800, textAlign: "center", marginBottom: "1.5rem" }}>
              How It Works
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1.25rem" }}>
              {[
                { step: "1", title: "Paste URL", desc: "Copy a product link from Amazon, Flipkart, or any supported platform", icon: "🔗", color: "#06b6d4" },
                { step: "2", title: "AI Analysis", desc: "ShopSmart identifies the product, finds matches, and compares prices", icon: "🤖", color: "#3b82f6" },
                { step: "3", title: "Best Deal", desc: "Get an explainable score, AI recommendation, and buy at the best price", icon: "🏆", color: "#10b981" },
              ].map((item, i) => (
                <div key={item.step} style={{
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border-color)",
                  borderRadius: "14px",
                  padding: "1.5rem",
                  textAlign: "center",
                  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                  cursor: "default",
                  position: "relative",
                  overflow: "hidden",
                  animation: `slideUp 0.4s ${0.4 + i * 0.1}s ease both`,
                }} onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.borderColor = item.color;
                  e.currentTarget.style.boxShadow = `0 12px 24px -8px ${item.color}30`;
                }} onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "var(--border-color)";
                  e.currentTarget.style.boxShadow = "none";
                }}>
                  <div style={{
                    width: 52,
                    height: 52,
                    borderRadius: 14,
                    background: `${item.color}15`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.5rem",
                    margin: "0 auto 0.75rem",
                    border: `1px solid ${item.color}30`,
                  }}>
                    {item.icon}
                  </div>
                  <div style={{
                    fontSize: "0.7rem",
                    color: item.color,
                    fontWeight: 700,
                    marginBottom: "0.35rem",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}>Step {item.step}</div>
                  <div style={{ fontWeight: 700, fontSize: "1rem", marginBottom: "0.35rem" }}>{item.title}</div>
                  <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>{item.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Popular Categories */}
          <div style={{ marginBottom: "3rem" }}>
            <h2 style={{ fontSize: "1.3rem", fontWeight: 800, textAlign: "center", marginBottom: "1.25rem" }}>
              Popular Categories
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: "0.6rem" }}>
              {CATEGORIES.map((cat, i) => (
                <Link key={cat.name} to={`/products?category=${encodeURIComponent(cat.name)}`} style={{ textDecoration: "none" }}>
                  <span style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.4rem",
                    padding: "0.6rem 0.85rem",
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "10px",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    color: "var(--text-secondary)",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    animation: `fadeInUp 0.3s ${0.5 + i * 0.03}s ease both`,
                  }} onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = cat.color;
                    e.currentTarget.style.color = cat.color;
                    e.currentTarget.style.background = `${cat.color}10`;
                  }} onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = "var(--border-color)";
                    e.currentTarget.style.color = "var(--text-secondary)";
                    e.currentTarget.style.background = "var(--bg-secondary)";
                  }}>
                    <span style={{ fontSize: "1rem" }}>{cat.icon}</span>
                    {cat.name}
                  </span>
                </Link>
              ))}
            </div>
          </div>

          {/* Supported Platforms */}
          <div style={{
            textAlign: "center",
            padding: "2rem",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-color)",
            borderRadius: "14px",
            animation: "fadeIn 0.5s 0.7s ease both",
          }}>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "0.75rem", fontWeight: 600 }}>
              Supported Platforms
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", justifyContent: "center" }}>
              {[
                { name: "Amazon", icon: "🛒", color: "#f59e0b" },
                { name: "Flipkart", icon: "🛍️", color: "#3b82f6" },
                { name: "Myntra", icon: "👗", color: "#ec4899" },
                { name: "AJIO", icon: "👟", color: "#8b5cf6" },
                { name: "Meesho", icon: "🏷️", color: "#f43f5e" },
                { name: "Croma", icon: "📺", color: "#06b6d4" },
                { name: "Reliance Digital", icon: "🏪", color: "#10b981" },
                { name: "Tata CLiQ", icon: "🏬", color: "#6366f1" },
              ].map((p) => (
                <span key={p.name} style={{
                  padding: "0.4rem 0.85rem",
                  background: `${p.color}10`,
                  border: `1px solid ${p.color}30`,
                  borderRadius: "8px",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  color: p.color,
                  transition: "all 0.2s ease",
                  cursor: "default",
                }} onMouseEnter={(e) => {
                  e.currentTarget.style.background = `${p.color}20`;
                  e.currentTarget.style.transform = "translateY(-2px)";
                }} onMouseLeave={(e) => {
                  e.currentTarget.style.background = `${p.color}10`;
                  e.currentTarget.style.transform = "translateY(0)";
                }}>
                  {p.icon} {p.name}
                </span>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Home;
