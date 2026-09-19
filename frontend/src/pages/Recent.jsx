import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { getProductImage, handleImageError } from "../utils/images";
import toast from "react-hot-toast";

const TABS = [
  { key: "all", label: "All Recent" },
  { key: "analyzed", label: "Recently Analyzed" },
  { key: "viewed", label: "Recently Viewed" },
];

const PLATFORM_COLORS = {
  Amazon: "#f59e0b",
  Flipkart: "#3b82f6",
  Myntra: "#ec4899",
  AJIO: "#8b5cf6",
  Meesho: "#f43f5e",
  Croma: "#06b6d4",
  "Reliance Digital": "#10b981",
  "Tata CLiQ": "#6366f1",
};

const timeAgo = (dateStr) => {
  if (!dateStr) return "";
  const now = new Date();
  const then = new Date(dateStr);
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);
  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return then.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
};

const Recent = () => {
  const { user, guestId } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("all");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  const fetchRecent = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (activeTab !== "all") params.type = activeTab;
      const res = await API.get("/recent/", { params });
      setItems(res.data.results || []);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchRecent();
  }, [fetchRecent]);

  const handleView = async (item) => {
    if (item.viewed_at) {
      navigate(`/analysis/${item.id}`, { state: { analysis: item } });
      return;
    }
    try {
      await API.put(`/recent/${item.id}/viewed/`);
    } catch {
      // proceed anyway
    }
    navigate(`/analysis/${item.id}`, { state: { analysis: item } });
  };

  const handleClear = async () => {
    if (!window.confirm("Clear all recent history? This cannot be undone.")) return;
    setClearing(true);
    try {
      const res = await API.delete("/recent/clear/");
      toast.success(`Cleared ${res.data.deleted} items`);
      setItems([]);
    } catch {
      toast.error("Failed to clear history");
    } finally {
      setClearing(false);
    }
  };

  const getLowestPrice = (item) => {
    const result = item.analysis_result;
    if (!result) return null;
    const comparisons = result.comparisons;
    if (comparisons?.best_price) return comparisons.best_price;
    const product = result.product;
    if (product?.price) return product.price;
    return null;
  };

  const getOfferCount = (item) => {
    const result = item.analysis_result;
    if (!result) return 0;
    return result.comparisons?.listings?.length || 0;
  };

  const getDealScore = (item) => {
    const result = item.analysis_result;
    if (!result?.ai_analysis?.deal_score) return null;
    return result.ai_analysis.deal_score;
  };

  return (
    <div className="app-wrapper" style={{ padding: "0 1.5rem 4rem", maxWidth: 1100, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ padding: "2rem 0 1rem", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: 800, marginBottom: "0.35rem" }}>
            Recent
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            {!user ? "Your recent product analyses" : `Your recent analyses — ${items.length} items`}
          </p>
        </div>
        {items.length > 0 && (
          <button
            onClick={handleClear}
            disabled={clearing}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              border: "1px solid rgba(244, 63, 94, 0.3)",
              background: "rgba(244, 63, 94, 0.08)",
              color: "var(--accent-rose)",
              fontWeight: 600,
              fontSize: "0.82rem",
              cursor: clearing ? "not-allowed" : "pointer",
              transition: "all 0.2s ease",
            }}
          >
            {clearing ? "Clearing..." : "Clear History"}
          </button>
        )}
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: "0.5rem 1.1rem",
              borderRadius: "999px",
              border: "1px solid",
              borderColor: activeTab === tab.key ? "var(--accent-cyan)" : "var(--border-color)",
              background: activeTab === tab.key ? "var(--accent-cyan)" : "var(--bg-card)",
              color: activeTab === tab.key ? "#fff" : "var(--text-secondary)",
              fontSize: "0.82rem",
              fontWeight: 600,
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1rem" }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} style={{
              background: "var(--bg-secondary)",
              border: "1px solid var(--border-color)",
              borderRadius: "14px",
              padding: "1.25rem",
              animation: "pulse 1.5s ease-in-out infinite",
              minHeight: 160,
            }} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && items.length === 0 && (
        <div style={{
          textAlign: "center",
          padding: "4rem 2rem",
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-color)",
          borderRadius: "14px",
        }}>
          <div style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>🔍</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.35rem" }}>No recent analyses yet</div>
          <div style={{ fontSize: "0.88rem", color: "var(--text-secondary)", marginBottom: "1.5rem", maxWidth: 400, margin: "0 auto 1.5rem" }}>
            Paste a product URL to start comparing products across platforms.
          </div>
          <Link to="/" style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.4rem",
            padding: "0.6rem 1.5rem",
            background: "var(--gradient-brand)",
            color: "#fff",
            borderRadius: "10px",
            textDecoration: "none",
            fontWeight: 700,
            fontSize: "0.9rem",
          }}>
            Analyze a Product
          </Link>
        </div>
      )}

      {/* Items Grid */}
      {!loading && items.length > 0 && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(min(300px, 100%), 1fr))",
          gap: "1rem",
        }}>
          {items.map((item) => {
            const price = getLowestPrice(item);
            const offerCount = getOfferCount(item);
            const dealScore = getDealScore(item);
            const platformColor = PLATFORM_COLORS[item.detected_platform] || "var(--accent-cyan)";

            return (
              <div
                key={item.id}
                onClick={() => handleView(item)}
                style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border-color)",
                  borderRadius: "14px",
                  padding: "1.25rem",
                  cursor: "pointer",
                  transition: "all 0.25s ease",
                  display: "flex",
                  flexDirection: "column",
                  gap: "0.75rem",
                  position: "relative",
                  overflow: "hidden",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-3px)";
                  e.currentTarget.style.borderColor = platformColor;
                  e.currentTarget.style.boxShadow = `0 8px 20px -6px ${platformColor}25`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "var(--border-color)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                {/* Top row: image + info */}
                <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                  <div style={{
                    width: 64,
                    height: 64,
                    borderRadius: 10,
                    overflow: "hidden",
                    flexShrink: 0,
                    background: "linear-gradient(135deg, rgba(6,182,212,0.05) 0%, rgba(59,130,246,0.05) 100%)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}>
                    <img
                      src={getProductImage(item.product_image || item.analysis_result?.product?.image_url)}
                      alt={item.product_title || "Product"}
                      style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
                      onError={handleImageError}
                    />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: 700,
                      fontSize: "0.92rem",
                      lineHeight: 1.3,
                      marginBottom: "0.3rem",
                      color: "var(--text-primary)",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                    }}>
                      {item.product_title || "Product"}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexWrap: "wrap" }}>
                      <span style={{
                        fontSize: "0.7rem",
                        fontWeight: 700,
                        padding: "0.15rem 0.5rem",
                        borderRadius: "6px",
                        background: `${platformColor}15`,
                        color: platformColor,
                        border: `1px solid ${platformColor}30`,
                      }}>
                        {item.detected_platform}
                      </span>
                      {item.product_brand && (
                        <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontWeight: 600 }}>
                          {item.product_brand}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Price + Score */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.5rem" }}>
                  {price ? (
                    <span style={{ fontSize: "1.15rem", fontWeight: 800, color: "var(--accent-green)" }}>
                      ₹{Number(price).toLocaleString("en-IN")}
                    </span>
                  ) : (
                    <span style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Price unavailable</span>
                  )}
                  {dealScore !== null && (
                    <span style={{
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      padding: "0.2rem 0.55rem",
                      borderRadius: "6px",
                      background: dealScore >= 75 ? "rgba(16, 185, 129, 0.12)" : dealScore >= 50 ? "rgba(245, 158, 11, 0.12)" : "rgba(244, 63, 94, 0.12)",
                      color: dealScore >= 75 ? "#10b981" : dealScore >= 50 ? "#f59e0b" : "#f43f5e",
                    }}>
                      Score: {dealScore}
                    </span>
                  )}
                </div>

                {/* Footer */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {offerCount > 0 && (
                      <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 600 }}>
                        {offerCount} listing{offerCount > 1 ? "s" : ""}
                      </span>
                    )}
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                      {timeAgo(item.created_at)}
                    </span>
                  </div>
                  <span style={{
                    fontSize: "0.72rem",
                    fontWeight: 600,
                    color: "var(--accent-cyan)",
                  }}>
                    View Analysis →
                  </span>
                </div>

                {/* Viewed badge */}
                {item.viewed_at && (
                  <div style={{
                    position: "absolute",
                    top: 8,
                    right: 8,
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    padding: "0.15rem 0.4rem",
                    borderRadius: "4px",
                    background: "rgba(99, 102, 241, 0.1)",
                    color: "#6366f1",
                  }}>
                    Viewed
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Recent;
