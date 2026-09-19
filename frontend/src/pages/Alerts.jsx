import React, { useEffect, useState } from "react";
import API from "../api/axios";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";

const Alerts = () => {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlerts = async () => {
    if (!user) {
      setLoading(false);
      setError("Login required to view alerts");
      return;
    }
    try {
      const res = await API.get("/users/alerts/");
      setAlerts(Array.isArray(res.data) ? res.data : res.data.results || []);
      setError(null);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load alerts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [user]);

  const handleDelete = async (id) => {
    try {
      await API.delete(`/users/alerts/${id}/`);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      window.dispatchEvent(new Event("alert:changed"));
    } catch (e) {
      toast.error("Delete failed: " + (e.response?.data?.detail || e.message));
    }
  };

  if (!user) {
    return (
      <main className="app-wrapper" style={{ maxWidth: 800, margin: "0 auto", padding: "2rem 1.5rem" }}>
        <h2>🔔 Price Drop Alerts — 30 Day</h2>
        <p style={{ color: "var(--text-secondary)", margin: "1rem 0" }}>Login to track price drops. When product price ≤ target, alert triggers.</p>
        <Link to="/login" style={{ background: "var(--accent-cyan)", color: "#fff", padding: "0.6rem 1.2rem", borderRadius: 8, textDecoration: "none", fontWeight: 700 }}>Login</Link>
      </main>
    );
  }

  return (
    <main className="app-wrapper" style={{ maxWidth: 900, margin: "0 auto", padding: "2rem 1.5rem 3rem" }}>
      <h2 style={{ fontWeight: 800, marginBottom: "0.25rem" }}>🔔 Price Drop Alerts — 30 Day Monitor</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
        Stored in PostgreSQL `PriceAlert`. Set from ProductDetail “Set Alert” box. Triggered when <code>lowest_price ≤ target_price</code>.
      </p>

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-secondary)" }}>Loading alerts...</div>
      ) : error ? (
        <div style={{ background: "rgba(244,63,94,0.12)", padding: "1rem", borderRadius: 12, color: "var(--accent-rose)" }}>{error}</div>
      ) : alerts.length === 0 ? (
        <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: 12, padding: "1.5rem", textAlign: "center" }}>
          <h3> No active alerts </h3>
          <p style={{ color: "var(--text-secondary)", margin: "0.5rem 0 1rem" }}>Go to any Product → set target price below current lowest.</p>
          <Link to="/" style={{ background: "var(--accent-cyan)", color: "#fff", padding: "0.6rem 1.2rem", borderRadius: 8, textDecoration: "none", fontWeight: 700 }}>Browse Deals</Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {alerts.map((a) => (
            <div key={a.id} style={{ background: a.is_triggered ? "rgba(16,185,129,0.08)" : "var(--bg-secondary)", border: `1px solid ${a.is_triggered ? "rgba(16,185,129,0.3)" : "var(--border-color)"}`, borderRadius: 12, padding: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 700 }}>{a.product_title} <span style={{ color: "var(--text-secondary)", fontWeight: 400, fontSize: "0.85rem" }}>• {a.product_category}</span> {a.is_triggered && <span style={{ background: "var(--accent-green)", color: "#fff", fontSize: "0.65rem", padding: "0.15rem 0.4rem", borderRadius: 999, marginLeft: "0.4rem" }}>TRIGGERED</span>} {a.email_sent && <span style={{ background: "rgba(99,102,241,0.15)", color: "#6366f1", fontSize: "0.65rem", padding: "0.15rem 0.4rem", borderRadius: 999, marginLeft: "0.4rem" }}>EMAIL SENT</span>}</div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
                  Target: <strong style={{ color: "var(--accent-amber)" }}>₹{Number(a.target_price).toLocaleString("en-IN")}</strong> • Current lowest: <strong style={{ color: a.is_triggered ? "var(--accent-green)" : "var(--text-primary)" }}>₹{a.current_lowest ? Number(a.current_lowest).toLocaleString("en-IN") : "N/A"}</strong> • {new Date(a.created_at).toLocaleDateString("en-IN")}
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <Link to={`/product/${a.product}`} style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "0.4rem 0.8rem", borderRadius: 8, textDecoration: "none", color: "var(--text-primary)", fontWeight: 600, fontSize: "0.85rem" }}>View</Link>
                <button onClick={() => handleDelete(a.id)} style={{ background: "var(--accent-rose)", color: "#fff", border: "none", padding: "0.4rem 0.8rem", borderRadius: 8, fontWeight: 600, cursor: "pointer", fontSize: "0.85rem" }}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
};

export default Alerts;
