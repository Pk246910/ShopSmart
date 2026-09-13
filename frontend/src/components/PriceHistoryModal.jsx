import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import API from "../api/axios";

const PriceHistoryModal = ({ product, onClose }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hiddenStores, setHiddenStores] = useState([]);

  useEffect(() => {
    if (!product?.id) {
      setError("No product data available for price history");
      return;
    }
    setLoading(true);
    setError(null);
    API.get(`/products/${product.id}/history/`)
      .then((res) => setHistory(res.data))
      .catch(() => setError("No price history available yet. History is tracked once products are analyzed."))
      .finally(() => setLoading(false));
  }, [product?.id]);

  if (!product) return null;

  const colors = { Amazon: "#f59e0b", Flipkart: "#3b82f6", Croma: "#06b6d4", "Reliance Digital": "#10b981", Myntra: "#ec4899", AJIO: "#8b5cf6", Meesho: "#f43f5e", "Tata CLiQ": "#6366f1" };

  const allStores = [...new Set(history.map((h) => h.store_name).filter(Boolean))];
  const visibleStores = allStores.filter((s) => !hiddenStores.includes(s));
  const visibleHistory = history.filter((h) => visibleStores.includes(h.store_name));

  const chartData = visibleHistory
    .filter((h) => h.price > 0 && h.price < 10000000)
    .slice()
    .reverse()
    .reduce((acc, cur) => {
      const date = new Date(cur.recorded_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" });
      let existing = acc.find((x) => x.date === date);
      if (!existing) {
        existing = { date };
        acc.push(existing);
      }
      existing[cur.store_name] = Number(cur.price);
      return acc;
    }, []);

  return (
    <div className="modal-overlay-backdrop" onClick={onClose}>
      <div className="modal-dialog-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 720 }}>
        <button className="modal-close-icon" onClick={onClose}>
          ✕
        </button>

        <h3 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: "0.25rem" }}>📈 Price History</h3>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "1rem" }}>{product.title}</p>

        {loading ? (
          <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-secondary)" }}>Loading price history...</div>
        ) : error ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>{error}</div>
        ) : history.length === 0 ? (
          <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📊</div>
            <div style={{ fontSize: "0.9rem" }}>No price history recorded yet.</div>
            <div style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>History is tracked each time this product is analyzed.</div>
          </div>
        ) : (
          <>
            {allStores.length > 1 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.75rem" }}>
                {allStores.map((s) => {
                  const off = hiddenStores.includes(s);
                  return (
                    <button
                      key={s}
                      onClick={() => setHiddenStores((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s])}
                      style={{
                        fontSize: "0.72rem", fontWeight: 700, padding: "0.25rem 0.6rem",
                        borderRadius: 999, cursor: "pointer",
                        border: `1px solid ${colors[s] || "#06b6d4"}55`,
                        background: off ? "transparent" : `${colors[s] || "#06b6d4"}18`,
                        color: off ? "var(--text-muted)" : "var(--text-primary)",
                        opacity: off ? 0.55 : 1,
                      }}
                    >
                      {s} {off ? "＋" : "✓"}
                    </button>
                  );
                })}
                {hiddenStores.length > 0 && (
                  <button
                    onClick={() => setHiddenStores([])}
                    style={{ fontSize: "0.72rem", fontWeight: 700, padding: "0.25rem 0.6rem", borderRadius: 999, cursor: "pointer", border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--accent-cyan)" }}
                  >
                    Show all
                  </button>
                )}
              </div>
            )}
            <div style={{ width: "100%", height: 300, marginTop: "0.5rem" }}>
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                  <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={11} />
                  <YAxis stroke="var(--text-secondary)" fontSize={11} tickFormatter={(v) => v >= 1000 ? `₹${(v / 1000).toFixed(0)}k` : `₹${v}`} tickCount={7} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "var(--bg-card)", borderColor: "var(--border-color)", borderRadius: "10px", color: "var(--text-primary)" }}
                    formatter={(val, name) => [
                      `₹${Number(val).toLocaleString("en-IN")}`,
                      name,
                    ]}
                  />
                  <Legend />
                  {visibleStores.map((s) => (
                    <Line key={s} type="monotone" dataKey={s} stroke={colors[s] || "#06b6d4"} strokeWidth={2.5} dot={{ r: 3 }} connectNulls />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {history.length > 0 && (
          <div style={{ marginTop: "0.75rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {[...new Set(history.map((h) => h.store_name))].map((s) => (
              <span key={s} style={{ fontSize: "0.75rem", fontWeight: 600, padding: "0.25rem 0.6rem", borderRadius: 6, background: `${colors[s] || "#06b6d4"}20`, color: colors[s] || "#06b6d4", border: `1px solid ${colors[s] || "#06b6d4"}40` }}>
                {s}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceHistoryModal;
