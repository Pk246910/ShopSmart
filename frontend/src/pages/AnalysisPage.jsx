import React, { useEffect, useState } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";
import AnalysisResult from "../components/AnalysisResult";
import PriceHistoryModal from "../components/PriceHistoryModal";
import ShareButton from "../components/ShareButton";
import toast from "react-hot-toast";
import { SkeletonAnalysisPage } from "../components/Skeleton";

const AnalysisPage = () => {
  const { id } = useParams();
  const location = useLocation();
  const { user } = useAuth();

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [wishlisted, setWishlisted] = useState(false);
  const [wishlistId, setWishlistId] = useState(null);
  const [wishlistLoading, setWishlistLoading] = useState(false);

  const [targetPrice, setTargetPrice] = useState("");
  const [alertSaving, setAlertSaving] = useState(false);


  const [showHistoryModal, setShowHistoryModal] = useState(false);

  const analysisData = analysis?.analysis_result || analysis;
  const product = analysisData?.product;

  useEffect(() => {
    if (location.state?.analysis) {
      setAnalysis(location.state.analysis);
      setLoading(false);
      return;
    }

    setLoading(true);
    API.get("/analyses/")
      .then((res) => {
        const list = res.data.results || res.data;
        const found = Array.isArray(list)
          ? list.find((a) => String(a.id) === String(id))
          : null;
        if (found) {
          setAnalysis(found);
        } else {
          setError("Analysis not found");
        }
      })
      .catch(() => setError("Failed to load analysis"))
      .finally(() => setLoading(false));
  }, [id, location.state]);

  useEffect(() => {
    if (!product?.id || !user) {
      setWishlisted(false);
      setWishlistId(null);
      return;
    }
    API.get("/wishlist/")
      .then((res) => {
        const list = res.data.results || res.data;
        const found = Array.isArray(list)
          ? list.find(
              (w) =>
                String(w.product) === String(product.id) ||
                w.product?.id === product.id
            )
          : null;
        if (found) {
          setWishlisted(true);
          setWishlistId(found.id);
        } else {
          setWishlisted(false);
          setWishlistId(null);
        }
      })
      .catch(() => {});
  }, [product?.id, user]);

  const toggleWishlist = async () => {
    if (!product?.id) return;
    if (!user) {
      toast.error("Please login to save products");
      return;
    }
    setWishlistLoading(true);
    try {
      if (wishlisted && wishlistId) {
        await API.delete(`/wishlist/${wishlistId}/`);
        setWishlisted(false);
        setWishlistId(null);
        toast.success("Removed from wishlist");
      } else {
        const res = await API.post("/wishlist/", {
          product: product.id,
        });
        setWishlisted(true);
        setWishlistId(res.data.id);
        toast.success("Added to wishlist");
      }
      window.dispatchEvent(new Event("wishlist:changed"));
    } catch {
      toast.error("Wishlist update failed");
    } finally {
      setWishlistLoading(false);
    }
  };

  const handleSetAlert = async (e) => {
    e.preventDefault();
    if (!user) {
      toast.error("Please login to set price alerts");
      return;
    }
    if (!product?.id || !targetPrice) return;
    setAlertSaving(true);
    try {
      await API.post("/users/alerts/", {
        product: product.id,
        target_price: Number(targetPrice),
      });
      toast.success(`Alert set for ₹${Number(targetPrice).toLocaleString("en-IN")}`);
      setTargetPrice("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to set alert");
    } finally {
      setAlertSaving(false);
    }
  };

  useEffect(() => {
    if (analysis) {
      const title = analysis.analysis_result?.product?.title || analysis.product?.title || "Analysis";
      document.title = `${title} — ShopSmart`;
      return () => { document.title = "ShopSmart — AI-Powered Product Comparison"; };
    }
  }, [analysis]);

  if (loading) {
    return (
      <div className="app-wrapper">
        <SkeletonAnalysisPage />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="app-wrapper" style={{ maxWidth: 1100, margin: "0 auto", padding: "4rem 1.5rem", textAlign: "center" }}>
        <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>🔍</div>
        <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent-rose)", marginBottom: "0.5rem" }}>
          {error || "Analysis not found"}
        </div>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center", marginTop: "1rem" }}>
          <button onClick={() => window.location.reload()} style={{
            padding: "0.6rem 1.2rem",
            background: "var(--gradient-brand)",
            color: "#fff",
            borderRadius: "8px",
            border: "none",
            fontWeight: 700,
            fontSize: "0.9rem",
            cursor: "pointer",
          }}>
            Try Again
          </button>
          <Link to="/" style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "0.6rem 1.2rem",
            background: "var(--bg-card)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-color)",
            borderRadius: "8px",
            textDecoration: "none",
            fontWeight: 700,
            fontSize: "0.9rem",
          }}>
            ← Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="app-wrapper" style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1.5rem 3rem" }}>
      {/* Top Bar */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "0.75rem",
        marginBottom: "1.5rem",
      }}>
        <Link
          to="/"
          style={{
            color: "var(--accent-cyan)",
            textDecoration: "none",
            fontSize: "0.9rem",
            fontWeight: 600,
          }}
        >
          ← Back to Home
        </Link>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button
            onClick={toggleWishlist}
            disabled={wishlistLoading}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              border: wishlisted
                ? "1px solid rgba(244, 63, 94, 0.4)"
                : "1px solid var(--border-color)",
              background: wishlisted
                ? "rgba(244, 63, 94, 0.12)"
                : "var(--bg-secondary)",
              color: wishlisted
                ? "var(--accent-rose)"
                : "var(--text-primary)",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: wishlistLoading ? "not-allowed" : "pointer",
              transition: "all 0.2s ease",
            }}
          >
            {wishlisted ? "♥ Saved" : "♡ Save to Wishlist"}
          </button>

          {user && (
            <button
              onClick={() => document.getElementById("alert-section")?.scrollIntoView({ behavior: "smooth", block: "center" })}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.4rem",
                padding: "0.5rem 1rem",
                borderRadius: "8px",
                border: "1px solid var(--border-color)",
                background: "var(--bg-secondary)",
                color: "var(--text-primary)",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              🔔 Set Alert
            </button>
          )}

          <button
            onClick={() => setShowHistoryModal(true)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              border: "1px solid var(--border-color)",
              background: "var(--bg-secondary)",
              color: "var(--text-primary)",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            📈 Price History
          </button>

          <ShareButton
            title={analysis.product?.title || analysis.analysis_result?.title || "Product"}
            price={analysis.analysis_result?.best_deal_price || analysis.product?.price}
          />
        </div>
      </div>

      {/* Analysis Result */}
      <AnalysisResult data={analysis.analysis_result || analysis} analysisId={id} />

      {/* Price Alert Section */}
      {user && (
        <div
          id="alert-section"
          style={{
            marginTop: "1.5rem",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border-color)",
            borderRadius: "12px",
            padding: "1.25rem",
          }}
        >
          <h4 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
            🔔 Set Price Alert
          </h4>
          <form onSubmit={handleSetAlert} style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
            <div style={{ display: "flex", alignItems: "center", background: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: "8px", padding: "0 0.6rem" }}>
              <span style={{ color: "var(--text-muted)", fontWeight: 600, fontSize: "0.85rem" }}>₹</span>
              <input
                type="number"
                placeholder="Target price"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                required
                min="1"
                style={{
                  background: "transparent",
                  border: "none",
                  outline: "none",
                  color: "var(--text-primary)",
                  fontSize: "0.9rem",
                  padding: "0.55rem 0.4rem",
                  width: 140,
                }}
              />
            </div>
            <button
              type="submit"
              disabled={alertSaving || !targetPrice}
              style={{
                padding: "0.55rem 1.2rem",
                borderRadius: "8px",
                border: "none",
                background: "var(--gradient-brand)",
                color: "#fff",
                fontWeight: 700,
                fontSize: "0.85rem",
                cursor: alertSaving ? "not-allowed" : "pointer",
                opacity: alertSaving || !targetPrice ? 0.6 : 1,
                transition: "opacity 0.2s ease",
              }}
            >
              {alertSaving ? "Setting..." : "Set Alert"}
            </button>
          </form>
          <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
            You'll be notified when the price drops to or below your target.
          </div>
        </div>
      )}

      {!user && (
        <div style={{
          marginTop: "1.5rem",
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-color)",
          borderRadius: "12px",
          padding: "1.25rem",
          textAlign: "center",
        }}>
          <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
            🔔 Want to set a price alert?
          </div>
          <Link
            to="/login"
            style={{
              display: "inline-block",
              padding: "0.5rem 1rem",
              background: "var(--accent-cyan)",
              color: "#fff",
              borderRadius: "8px",
              textDecoration: "none",
              fontWeight: 700,
              fontSize: "0.85rem",
            }}
          >
            Login to Set Alert
          </Link>
        </div>
      )}

      {/* Price History Modal */}
      {showHistoryModal && product && (
        <PriceHistoryModal
          product={product}
          onClose={() => setShowHistoryModal(false)}
        />
      )}
    </div>
  );
};

export default AnalysisPage;
