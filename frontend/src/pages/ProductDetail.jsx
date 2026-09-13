import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";
import ShareButton from "../components/ShareButton";
import { SkeletonProductDetail, SkeletonChart } from "../components/Skeleton";
import toast from "react-hot-toast";

const CHART_COLORS = {
  Amazon: "#f59e0b",
  Flipkart: "#3b82f6",
  Croma: "#06b6d4",
  "Reliance Digital": "#10b981",
  Myntra: "#ec4899",
  AJIO: "#8b5cf6",
  Meesho: "#f43f5e",
  "Tata CLiQ": "#6366f1",
};

const ProductDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [wishlisted, setWishlisted] = useState(false);
  const [wishlistId, setWishlistId] = useState(null);

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState(null);

  const [targetPrice, setTargetPrice] = useState("");
  const [alertSaving, setAlertSaving] = useState(false);
  const [hiddenStores, setHiddenStores] = useState([]);

  useEffect(() => {
    setLoading(true);
    API.get(`/products/${id}/`)
      .then((res) => {
        setProduct(res.data);
        setLoading(false);
      })
      .catch(() => {
        setError("Product not found");
        setLoading(false);
      });
  }, [id]);

  useEffect(() => {
    if (!id || !user) return;
    API.get("/wishlist/")
      .then((res) => {
        const list = res.data.results || res.data;
        const found = Array.isArray(list)
          ? list.find(
              (w) =>
                String(w.product) === String(id) ||
                w.product?.id === Number(id)
            )
          : null;
        if (found) {
          setWishlisted(true);
          setWishlistId(found.id);
        }
      })
      .catch(() => {});
  }, [id, user]);

  useEffect(() => {
    if (!id) return;
    setHistoryLoading(true);
    setHistoryError(null);
    API.get(`/products/${id}/history/`)
      .then((res) => setHistory(res.data || []))
      .catch(() => setHistoryError("No price history available yet."))
      .finally(() => setHistoryLoading(false));
  }, [id]);

  const toggleWishlist = async () => {
    if (!user) {
      toast.error("Please login to save products");
      return;
    }
    if (wishlisted && wishlistId) {
      await API.delete(`/wishlist/${wishlistId}/`);
      setWishlisted(false);
      setWishlistId(null);
      toast.success("Removed from wishlist");
    } else {
      const res = await API.post("/wishlist/", {
        product: Number(id),
      });
      setWishlisted(true);
      setWishlistId(res.data.id);
      toast.success("Added to wishlist");
    }
    window.dispatchEvent(new Event("wishlist:changed"));
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

  if (loading) {
    return <SkeletonProductDetail />;
  }

  if (error || !product) {
    return (
      <div
        className="app-wrapper"
        style={{ textAlign: "center", padding: "4rem", color: "var(--accent-rose)" }}
      >
        {error || "Product not found"}
      </div>
    );
  }

  const offers = product.offers || [];
  const bestOffer = product.best_offer || offers[0];

  const allStores = [...new Set(history.map((h) => h.store_name).filter(Boolean))];
  const visibleStores = allStores.filter((s) => !hiddenStores.includes(s));
  const visibleHistory = history.filter((h) => visibleStores.includes(h.store_name));

  const toggleStore = (s) => {
    setHiddenStores((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  };

  const chartData = visibleHistory
    .filter((h) => h.price > 0 && h.price < 10000000)
    .slice()
    .reverse()
    .reduce((acc, cur) => {
      const date = new Date(cur.recorded_at).toLocaleDateString("en-IN", {
        month: "short",
        day: "numeric",
      });
      let existing = acc.find((x) => x.date === date);
      if (!existing) {
        existing = { date };
        acc.push(existing);
      }
      existing[cur.store_name] = Number(cur.price);
      return acc;
    }, []);

  const uniqueStores = visibleStores;

  // Latest 10 records for the historical data table (newest first).
  const recentRows = visibleHistory
    .filter((h) => h.price > 0)
    .slice(0, 10);

  const sectionCard = {
    background: "var(--bg-secondary)",
    borderRadius: 12,
    border: "1px solid var(--border-color)",
    padding: "1.25rem",
  };

  const sectionTitle = {
    fontSize: "1.15rem",
    fontWeight: 800,
    marginBottom: "1rem",
    display: "flex",
    alignItems: "center",
    gap: "0.4rem",
  };

  const lowestPrice = offers.length > 0
    ? Math.min(...offers.map((o) => Number(o.current_price)))
    : 0;

  return (
    <div
      className="app-wrapper"
      style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1.5rem 3rem" }}
    >
      <Link
        to="/"
        style={{
          color: "var(--accent-cyan)",
          textDecoration: "none",
          fontSize: "0.9rem",
          marginBottom: "1rem",
          display: "inline-block",
        }}
      >
        ← Back to Home
      </Link>

      {/* ── Product Info ── */}
      <div
        style={{
          display: "flex",
          gap: "2rem",
          flexWrap: "wrap",
          marginBottom: "2rem",
          animation: "fadeIn 0.4s ease",
        }}
      >
        <div
          style={{
            flex: "0 0 300px",
            background: "var(--bg-secondary)",
            borderRadius: 16,
            padding: "1.5rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            minHeight: 280,
          }}
        >
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.title}
              style={{ maxWidth: "100%", maxHeight: 260, objectFit: "contain" }}
              onError={(e) => { e.target.style.display = "none"; }}
            />
          ) : (
            <div style={{ fontSize: "4rem", opacity: 0.2 }}>📦</div>
          )}
        </div>

        <div style={{ flex: 1, minWidth: 280 }}>
          <div
            style={{
              fontSize: "0.8rem",
              color: "var(--accent-cyan)",
              fontWeight: 700,
              marginBottom: "0.5rem",
            }}
          >
            {product.category} • {product.brand}
          </div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 800, marginBottom: "0.75rem" }}>
            {product.title}
          </h1>
          {bestOffer && (
            <div
              style={{
                fontSize: "1.8rem",
                fontWeight: 800,
                color: "var(--accent-green)",
                marginBottom: "0.75rem",
              }}
            >
              ₹{Number(bestOffer.current_price).toLocaleString("en-IN")}
              {bestOffer.original_price > bestOffer.current_price && (
                <span
                  style={{
                    fontSize: "0.9rem",
                    color: "var(--text-muted)",
                    textDecoration: "line-through",
                    marginLeft: "0.75rem",
                  }}
                >
                  ₹{Number(bestOffer.original_price).toLocaleString("en-IN")}
                </span>
              )}
              {bestOffer.discount_percent > 0 && (
                <span
                  style={{
                    fontSize: "0.85rem",
                    color: "var(--accent-green)",
                    marginLeft: "0.5rem",
                    fontWeight: 600,
                  }}
                >
                  {bestOffer.discount_percent}% off
                </span>
              )}
            </div>
          )}
          <div
            style={{
              display: "flex",
              gap: "0.75rem",
              flexWrap: "wrap",
              marginTop: "1rem",
            }}
          >
            <button
              onClick={toggleWishlist}
              style={{
                padding: "0.6rem 1.2rem",
                borderRadius: 8,
                border: "1px solid var(--border-color)",
                background: wishlisted ? "rgba(244,63,94,0.15)" : "var(--bg-card)",
                color: wishlisted ? "var(--accent-rose)" : "var(--text-primary)",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {wishlisted ? "❤️ Saved" : user ? "🤍 Save" : "🔒 Login to Save"}
            </button>
            {bestOffer?.product_url && (
              <a
                href={bestOffer.product_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  padding: "0.6rem 1.2rem",
                  borderRadius: 8,
                  background: "var(--gradient-brand)",
                  color: "#fff",
                  fontWeight: 700,
                  textDecoration: "none",
                }}
              >
                Buy at {bestOffer.store_name} →
              </a>
            )}
            <ShareButton title={product.title} price={bestOffer?.current_price} />
          </div>
        </div>
      </div>

      {/* ── Platform Comparison ── */}
      {offers.length > 0 && (
        <div style={{ marginBottom: "2rem" }}>
          <h2 style={sectionTitle}>📊 Platform Comparison</h2>
          <div style={{ ...sectionCard, padding: 0, overflow: "hidden" }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                <thead>
                  <tr
                    style={{
                      borderBottom: "2px solid var(--border-color)",
                      textAlign: "left",
                    }}
                  >
                    <th style={{ padding: "0.75rem 0.75rem" }}>Platform</th>
                    <th style={{ padding: "0.75rem 0.75rem", textAlign: "right" }}>Price</th>
                    <th style={{ padding: "0.75rem 0.75rem", textAlign: "right" }}>MRP</th>
                    <th style={{ padding: "0.75rem 0.75rem", textAlign: "right" }}>Discount</th>
                    <th style={{ padding: "0.75rem 0.75rem", textAlign: "right" }}>Rating</th>
                    <th style={{ padding: "0.75rem 0.75rem", textAlign: "center" }}>Delivery</th>
                    <th style={{ padding: "0.75rem 0.75rem" }}>Offers</th>
                    <th style={{ padding: "0.75rem 0.75rem" }}>Coupons</th>
                    <th style={{ padding: "0.75rem 0.75rem", textAlign: "center" }}>Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {offers.map((o, i) => {
                    const isBest = Number(o.current_price) === lowestPrice && offers.length > 1;
                    return (
                      <tr
                        key={o.id || i}
                        style={{
                          borderTop: "1px solid var(--border-color)",
                          background: isBest
                            ? "rgba(16,185,129,0.06)"
                            : "transparent",
                          transition: "background 0.2s ease",
                        }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.background = isBest
                            ? "rgba(16,185,129,0.12)"
                            : "var(--bg-card-hover)")
                        }
                        onMouseLeave={(e) =>
                          (e.currentTarget.style.background = isBest
                            ? "rgba(16,185,129,0.06)"
                            : "transparent")
                        }
                      >
                        <td style={{ padding: "0.75rem 0.75rem", fontWeight: 600 }}>
                          {isBest && (
                            <span
                              style={{
                                fontSize: "0.65rem",
                                background: "var(--accent-green)",
                                color: "#fff",
                                padding: "0.1rem 0.4rem",
                                borderRadius: 4,
                                marginRight: "0.4rem",
                                fontWeight: 700,
                              }}
                            >
                              BEST
                            </span>
                          )}
                          {o.store_name}
                        </td>
                        <td
                          style={{
                            padding: "0.75rem 0.75rem",
                            textAlign: "right",
                            fontWeight: 700,
                            color: isBest ? "var(--accent-green)" : "var(--text-primary)",
                          }}
                        >
                          ₹{Number(o.current_price).toLocaleString("en-IN")}
                        </td>
                        <td
                          style={{
                            padding: "0.75rem 0.75rem",
                            textAlign: "right",
                            color: "var(--text-muted)",
                            textDecoration: o.original_price > o.current_price ? "line-through" : "none",
                          }}
                        >
                          {o.original_price > o.current_price
                            ? `₹${Number(o.original_price).toLocaleString("en-IN")}`
                            : "—"}
                        </td>
                        <td
                          style={{
                            padding: "0.75rem 0.75rem",
                            textAlign: "right",
                            color: o.discount_percent > 0 ? "var(--accent-green)" : "var(--text-muted)",
                            fontWeight: o.discount_percent > 0 ? 700 : 400,
                          }}
                        >
                          {o.discount_percent > 0 ? `${o.discount_percent}%` : "—"}
                        </td>
                        <td style={{ padding: "0.75rem 0.75rem", textAlign: "right" }}>
                          {o.rating ? (
                            <span>
                              {o.rating}★
                              {o.reviews_count > 0 && (
                                <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
                                  {" "}({o.reviews_count.toLocaleString()})
                                </span>
                              )}
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td style={{ padding: "0.75rem 0.75rem", textAlign: "center" }}>
                          {o.delivery_days != null ? (
                            <span style={{ fontSize: "0.8rem" }}>
                              {o.delivery_days === 0 ? (
                                <span style={{ color: "var(--accent-green)" }}>Today</span>
                              ) : o.delivery_days === 1 ? (
                                <span style={{ color: "var(--accent-green)" }}>Tomorrow</span>
                              ) : (
                                <span>{o.delivery_days} days</span>
                              )}
                              {o.delivery_time && (
                                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                                  {o.delivery_time}
                                </div>
                              )}
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td style={{ padding: "0.75rem 0.75rem" }}>
                          {o.coupon_code ? (
                            <span
                              style={{
                                fontSize: "0.75rem",
                                padding: "0.15rem 0.5rem",
                                borderRadius: 4,
                                background: "rgba(245,158,11,0.12)",
                                color: "#f59e0b",
                                fontWeight: 600,
                                border: "1px dashed rgba(245,158,11,0.3)",
                              }}
                            >
                              {o.coupon_code}
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td style={{ padding: "0.75rem 0.75rem" }}>
                          {o.coupon_discount > 0 ? (
                            <span
                              style={{
                                fontSize: "0.75rem",
                                padding: "0.15rem 0.5rem",
                                borderRadius: 4,
                                background: "rgba(16,185,129,0.12)",
                                color: "var(--accent-green)",
                                fontWeight: 600,
                              }}
                            >
                              ₹{o.coupon_discount} off
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>
                        <td style={{ padding: "0.75rem 0.75rem", textAlign: "center" }}>
                          {o.in_stock ? (
                            <span style={{ color: "var(--accent-green)" }}>In Stock</span>
                          ) : (
                            <span style={{ color: "var(--accent-rose)" }}>Out</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── Price History ── */}
      <div style={{ marginBottom: "2rem" }}>
        <h2 style={sectionTitle}>📈 Price History</h2>
        <div style={sectionCard}>
          {historyLoading ? (
            <SkeletonChart height={260} />
          ) : historyError || history.length === 0 ? (
            <div
              style={{
                textAlign: "center",
                padding: "2rem",
                color: "var(--text-muted)",
              }}
            >
              <div style={{ fontSize: "1.8rem", marginBottom: "0.5rem", opacity: 0.4 }}>
                📊
              </div>
              <div style={{ fontSize: "0.9rem" }}>
                {historyError || "No price history yet."}
              </div>
              <div style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>
                History is tracked each time this product is analyzed.
              </div>
            </div>
          ) : (
            <>
              {/* Platform filter pills */}
              {allStores.length > 1 && (
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
                  {allStores.map((s) => {
                    const off = hiddenStores.includes(s);
                    return (
                      <button
                        key={s}
                        onClick={() => toggleStore(s)}
                        title={off ? `Show ${s}` : `Hide ${s}`}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.35rem",
                          fontSize: "0.75rem",
                          fontWeight: 700,
                          padding: "0.3rem 0.7rem",
                          borderRadius: 999,
                          cursor: "pointer",
                          border: `1px solid ${CHART_COLORS[s] || "#06b6d4"}55`,
                          background: off ? "transparent" : `${CHART_COLORS[s] || "#06b6d4"}18`,
                          color: off ? "var(--text-muted)" : "var(--text-primary)",
                          opacity: off ? 0.55 : 1,
                        }}
                      >
                        <span style={{
                          width: 8, height: 8, borderRadius: "50%",
                          background: CHART_COLORS[s] || "#06b6d4",
                          opacity: off ? 0.3 : 1,
                        }} />
                        {s} {off ? "＋" : "✓"}
                      </button>
                    );
                  })}
                  {hiddenStores.length > 0 && (
                    <button
                      onClick={() => setHiddenStores([])}
                      style={{
                        fontSize: "0.75rem", fontWeight: 700, padding: "0.3rem 0.7rem",
                        borderRadius: 999, cursor: "pointer",
                        border: "1px solid var(--border-color)", background: "var(--bg-card)",
                        color: "var(--accent-cyan)",
                      }}
                    >
                      Show all
                    </button>
                  )}
                </div>
              )}
              <div style={{ width: "100%", height: 300 }}>
                <ResponsiveContainer>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                    <XAxis
                      dataKey="date"
                      stroke="var(--text-secondary)"
                      fontSize={11}
                    />
                    <YAxis
                      stroke="var(--text-secondary)"
                      fontSize={11}
                      tickFormatter={(v) =>
                        v >= 1000 ? `₹${(v / 1000).toFixed(0)}k` : `₹${v}`
                      }
                      tickCount={6}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "var(--bg-card)",
                        borderColor: "var(--border-color)",
                        borderRadius: 10,
                        color: "var(--text-primary)",
                      }}
                      formatter={(val, name) => [
                        `₹${Number(val).toLocaleString("en-IN")}`,
                        name,
                      ]}
                    />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      iconType="circle"
                      iconSize={8}
                      wrapperStyle={{ fontSize: "0.8rem", fontWeight: 600, paddingTop: "0.5rem" }}
                    />
                    {uniqueStores.map((s) => (
                      <Line
                        key={s}
                        type="monotone"
                        dataKey={s}
                        stroke={CHART_COLORS[s] || "#06b6d4"}
                        strokeWidth={2.5}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                        connectNulls
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Historical data table */}
              {recentRows.length > 0 && (
                <div style={{ marginTop: "1.25rem" }}>
                  <div style={{ fontSize: "0.85rem", fontWeight: 800, marginBottom: "0.5rem" }}>
                    🕘 Historical data <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(latest {recentRows.length} records)</span>
                  </div>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
                      <thead>
                        <tr style={{ color: "var(--text-secondary)", borderBottom: "2px solid var(--border-color)", textAlign: "left" }}>
                          <th style={{ padding: "0.5rem" }}>Date</th>
                          <th style={{ padding: "0.5rem" }}>Platform</th>
                          <th style={{ padding: "0.5rem", textAlign: "right" }}>Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentRows.map((h, i) => (
                          <tr key={h.id || i} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                            <td style={{ padding: "0.5rem", color: "var(--text-secondary)" }}>
                              {new Date(h.recorded_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
                            </td>
                            <td style={{ padding: "0.5rem", fontWeight: 600 }}>
                              <span style={{ color: CHART_COLORS[h.store_name] || "var(--accent-cyan)" }}>●</span> {h.store_name}
                            </td>
                            <td style={{ padding: "0.5rem", textAlign: "right", fontWeight: 700 }}>
                              ₹{Number(h.price).toLocaleString("en-IN")}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* ── Set Price Alert ── */}
      <div style={{ marginBottom: "2rem" }}>
        <h2 style={sectionTitle}>🔔 Set Price Alert</h2>
        <div style={sectionCard}>
          {user ? (
            <>
              <form
                onSubmit={handleSetAlert}
                style={{
                  display: "flex",
                  gap: "0.5rem",
                  alignItems: "center",
                  flexWrap: "wrap",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    background: "var(--bg-card)",
                    border: "1px solid var(--border-color)",
                    borderRadius: 8,
                    padding: "0 0.6rem",
                  }}
                >
                  <span
                    style={{
                      color: "var(--text-muted)",
                      fontWeight: 600,
                      fontSize: "0.85rem",
                    }}
                  >
                    ₹
                  </span>
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
                    borderRadius: 8,
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
              <div
                style={{
                  marginTop: "0.5rem",
                  fontSize: "0.75rem",
                  color: "var(--text-muted)",
                }}
              >
                You'll be notified when the price drops to or below your target.
              </div>
            </>
          ) : (
            <div style={{ textAlign: "center", padding: "0.5rem 0" }}>
              <div
                style={{
                  fontSize: "0.85rem",
                  color: "var(--text-secondary)",
                  marginBottom: "0.75rem",
                }}
              >
                Want to set a price alert?
              </div>
              <Link
                to="/login"
                style={{
                  display: "inline-block",
                  padding: "0.5rem 1rem",
                  background: "var(--accent-cyan)",
                  color: "#fff",
                  borderRadius: 8,
                  textDecoration: "none",
                  fontWeight: 700,
                  fontSize: "0.85rem",
                }}
              >
                Login to Set Alert
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* ── Specifications ── */}
      {product.specifications && Object.keys(product.specifications).length > 0 && (
        <div style={{ marginBottom: "2rem" }}>
          <h2 style={sectionTitle}>📋 Specifications</h2>
          <div style={sectionCard}>
            {Object.entries(product.specifications).map(([k, v]) => (
              <div
                key={k}
                style={{
                  display: "flex",
                  padding: "0.4rem 0",
                  borderBottom: "1px solid var(--border-color)",
                }}
              >
                <span
                  style={{
                    flex: "0 0 200px",
                    color: "var(--text-secondary)",
                    fontWeight: 600,
                    fontSize: "0.85rem",
                  }}
                >
                  {k}
                </span>
                <span style={{ fontSize: "0.85rem" }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
