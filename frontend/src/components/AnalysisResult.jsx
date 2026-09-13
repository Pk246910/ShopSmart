import React from "react";
import { useNavigate } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import ShareButton from "./ShareButton";

const storeColors = {
  Amazon: "#f59e0b",
  Flipkart: "#3b82f6",
  Croma: "#06b6d4",
  "Reliance Digital": "#10b981",
  Myntra: "#ec4899",
  AJIO: "#8b5cf6",
  Meesho: "#f43f5e",
  "Tata CLiQ": "#6366f1",
};

const AnalysisResult = ({ data, analysisId }) => {
  const navigate = useNavigate();
  if (!data) return null;

  const product = data.product || {};
  const comparison = data.comparisons || {};
  const ai = data.ai_analysis || {};
  const listings = comparison.listings || [];
  const scoredListings = ai.scored_listings || listings;

  const bestDeal = scoredListings.length > 0 ? scoredListings[0] : null;
  const cheapest = listings.find((l) => l.is_cheapest);
  const bestRated = comparison.best_rating;
  const fastest = comparison.fastest_delivery;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Product Header */}
      <div style={{
        background: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "16px",
        padding: "1.5rem",
        display: "grid",
        gridTemplateColumns: "200px 1fr",
        gap: "1.5rem",
      }}>
        <div style={{
          background: "linear-gradient(135deg, rgba(6,182,212,0.05) 0%, rgba(59,130,246,0.05) 100%)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "12px",
          padding: "1rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: 200,
        }}>
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.title}
              style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }}
              onError={(e) => { e.target.style.display = "none"; }}
            />
          ) : (
            <div style={{ fontSize: "3rem", opacity: 0.3 }}>📦</div>
          )}
        </div>

        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
            <span style={{
              padding: "0.2rem 0.6rem",
              background: storeColors[data.platform] || "var(--accent-cyan)",
              color: "#fff",
              borderRadius: "6px",
              fontSize: "0.75rem",
              fontWeight: 700,
            }}>
              {data.platform}
            </span>
            {product.data_source === "demo" && (
              <span style={{
                padding: "0.15rem 0.5rem",
                background: "rgba(99, 102, 241, 0.15)",
                color: "#6366f1",
                borderRadius: "4px",
                fontSize: "0.7rem",
                fontWeight: 600,
              }}>Demo Data</span>
            )}
            {product.data_source === "live" && (
              <span style={{
                padding: "0.15rem 0.5rem",
                background: "rgba(16, 185, 129, 0.15)",
                color: "var(--accent-green)",
                borderRadius: "4px",
                fontSize: "0.7rem",
                fontWeight: 600,
              }}>Live Data</span>
            )}
            {product.data_source === "url_extract" && (
              <span style={{
                padding: "0.15rem 0.5rem",
                background: "rgba(251, 191, 36, 0.15)",
                color: "var(--accent-amber)",
                borderRadius: "4px",
                fontSize: "0.7rem",
                fontWeight: 600,
              }}>URL Detected</span>
            )}
          </div>

          <h2 style={{ fontSize: "1.3rem", fontWeight: 800, marginBottom: "0.5rem", lineHeight: 1.3 }}>
            {product.title}
          </h2>

          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
            {product.brand && <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}><strong>Brand:</strong> {product.brand}</span>}
            {product.category && <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}><strong>Category:</strong> {product.category}</span>}
          </div>

          <div style={{ display: "flex", gap: "1.5rem", alignItems: "flex-end", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.15rem" }}>Price</div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: (product.price > 0 || bestDeal?.price > 0) ? "var(--accent-green)" : "var(--text-muted)" }}>
                {product.price > 0
                  ? `₹${product.price?.toLocaleString("en-IN")}`
                  : bestDeal?.price > 0
                    ? `₹${bestDeal.price.toLocaleString("en-IN")}`
                    : "N/A"}
              </div>
              {product.price === 0 && bestDeal?.price > 0 && (
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.15rem" }}>
                  Best price from {bestDeal.platform}
                </div>
              )}
            </div>
            {product.mrp > product.price && product.price > 0 && (
              <div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.15rem" }}>MRP</div>
                <div style={{ fontSize: "1.1rem", color: "var(--text-muted)", textDecoration: "line-through" }}>
                  ₹{product.mrp?.toLocaleString("en-IN")}
                </div>
              </div>
            )}
            {product.discount > 0 && (
              <div style={{
                padding: "0.3rem 0.7rem",
                background: "rgba(244, 63, 94, 0.15)",
                color: "var(--accent-rose)",
                borderRadius: "6px",
                fontWeight: 700,
                fontSize: "0.85rem",
              }}>
                {product.discount}% off
              </div>
            )}
            {product.rating && (
              <div style={{ fontSize: "0.9rem", color: "var(--accent-amber)" }}>
                ★ {product.rating} {product.review_count > 0 && <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>({product.review_count.toLocaleString()})</span>}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Best Deal Banner with Sub-Scores */}
      {bestDeal && (
        <div style={{
          background: "linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(6,182,212,0.08) 100%)",
          border: "2px solid rgba(16,185,129,0.3)",
          borderRadius: "16px",
          padding: "1.5rem",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "1.5rem" }}>🏆</span>
            <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--accent-green)" }}>Best Overall Deal</span>
            {ai.confidence && (
              <span style={{
                marginLeft: "0.5rem",
                padding: "0.2rem 0.6rem",
                background: ai.confidence.level === "high" ? "rgba(16,185,129,0.15)" : ai.confidence.level === "medium" ? "rgba(251,191,36,0.15)" : "rgba(244,63,94,0.15)",
                color: ai.confidence.level === "high" ? "var(--accent-green)" : ai.confidence.level === "medium" ? "var(--accent-amber)" : "var(--accent-rose)",
                borderRadius: "999px",
                fontSize: "0.7rem",
                fontWeight: 700,
              }}>
                {ai.confidence.label}
              </span>
            )}
          </div>
          <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: "1.3rem", fontWeight: 800, color: storeColors[bestDeal.platform] || "var(--text-primary)" }}>
                {bestDeal.platform}
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 800, color: bestDeal.price > 0 ? "var(--accent-green)" : "var(--text-muted)" }}>
                {bestDeal.price > 0 ? `₹${bestDeal.price?.toLocaleString("en-IN")}` : "N/A"}
              </div>
            </div>
            <div style={{
              padding: "0.6rem 1.2rem",
              background: bestDeal.score >= 75 ? "rgba(16,185,129,0.2)" : "rgba(251,191,36,0.2)",
              borderRadius: "12px",
              textAlign: "center",
            }}>
              <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Score</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 800, color: bestDeal.score >= 75 ? "var(--accent-green)" : "var(--accent-amber)" }}>
                {bestDeal.score}/100
              </div>
            </div>
            <div style={{ flex: 1, minWidth: 200 }}>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.3rem" }}>Why this is the best:</div>
              <ul style={{ fontSize: "0.85rem", color: "var(--text-primary)", paddingLeft: "1.1rem", lineHeight: 1.6 }}>
                {cheapest && cheapest.platform === bestDeal.platform && <li>Lowest price among all platforms</li>}
                {bestRated && bestRated.platform === bestDeal.platform && <li>Highest customer rating ({bestRated.rating}★)</li>}
                {fastest && fastest.platform === bestDeal.platform && <li>Fastest delivery ({fastest.days} day{fastest.days > 1 ? "s" : ""})</li>}
                {bestDeal.coupon_discount > 0 && <li>Available coupon saves ₹{bestDeal.coupon_discount.toLocaleString("en-IN")}</li>}
                {!cheapest || cheapest.platform !== bestDeal.platform ? <li>Best overall value considering price, rating, and delivery</li> : null}
              </ul>
            </div>
          </div>

          {/* Sub-Scores Breakdown */}
          {bestDeal.sub_scores && (
            <div style={{ marginTop: "1.25rem", borderTop: "1px solid rgba(16,185,129,0.2)", paddingTop: "1rem" }}>
              <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-muted)", marginBottom: "0.6rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Score Breakdown
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: "0.5rem" }}>
                {[
                  { key: "price", label: "Price Value", icon: "💰", weight: "35%" },
                  { key: "rating", label: "Product Rating", icon: "⭐", weight: "15%" },
                  { key: "review_confidence", label: "Review Confidence", icon: "📊", weight: "10%" },
                  { key: "offers", label: "Offers & Discount", icon: "🏷️", weight: "10%" },
                  { key: "delivery", label: "Delivery", icon: "🚚", weight: "10%" },
                  { key: "warranty", label: "Warranty & Returns", icon: "🛡️", weight: "10%" },
                  { key: "seller", label: "Seller Reliability", icon: "✅", weight: "5%" },
                  { key: "freshness", label: "Data Freshness", icon: "🕐", weight: "5%" },
                ].map(({ key, label, icon, weight }) => {
                  const val = bestDeal.sub_scores[key] || 0;
                  return (
                    <div key={key} style={{
                      padding: "0.5rem 0.7rem",
                      background: "var(--bg-card)",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "8px",
                      fontSize: "0.78rem",
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                        <span style={{ color: "var(--text-secondary)", fontWeight: 600 }}>{icon} {label}</span>
                        <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>({weight})</span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <div style={{ flex: 1, height: 6, background: "var(--bg-secondary)", borderRadius: 3, overflow: "hidden" }}>
                          <div style={{
                            width: `${val}%`,
                            height: "100%",
                            background: val >= 70 ? "var(--accent-green)" : val >= 40 ? "var(--accent-amber)" : "var(--accent-rose)",
                            borderRadius: 3,
                            transition: "width 0.3s ease",
                          }} />
                        </div>
                        <span style={{
                          fontWeight: 700,
                          color: val >= 70 ? "var(--accent-green)" : val >= 40 ? "var(--accent-amber)" : "var(--accent-rose)",
                          minWidth: 30,
                          textAlign: "right",
                        }}>
                          {Math.round(val)}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendation Categories */}
      {ai.recommendation_categories && ai.recommendation_categories.length > 0 && (
        <div style={{
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-color)",
          borderRadius: "16px",
          padding: "1.5rem",
        }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>
            🏅 Recommendation Categories
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "0.75rem" }}>
            {ai.recommendation_categories.map((cat, i) => (
              <div key={i} style={{
                padding: "0.8rem 1rem",
                background: i === 0 ? "rgba(16,185,129,0.08)" : "var(--bg-card)",
                border: i === 0 ? "1px solid rgba(16,185,129,0.3)" : "1px solid var(--border-subtle)",
                borderRadius: "10px",
              }}>
                <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginBottom: "0.25rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.03em" }}>
                  {cat.category}
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <span style={{ fontWeight: 700, color: storeColors[cat.platform] || "var(--text-primary)" }}>
                      {cat.platform}
                    </span>
                    <span style={{ color: "var(--text-muted)", margin: "0 0.3rem" }}>·</span>
                    <span style={{ fontWeight: 700, color: "var(--accent-green)" }}>
                      ₹{cat.price?.toLocaleString("en-IN")}
                    </span>
                  </div>
                  <span style={{
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    padding: "0.15rem 0.4rem",
                    borderRadius: "6px",
                    background: cat.score >= 75 ? "rgba(16,185,129,0.15)" : "rgba(251,191,36,0.15)",
                    color: cat.score >= 75 ? "var(--accent-green)" : "var(--accent-amber)",
                  }}>
                    {cat.score}
                  </span>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
                  {cat.reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Analysis */}
      {ai.deal_assessment && (
        <div style={{
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-color)",
          borderRadius: "16px",
          padding: "1.5rem",
        }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            🤖 ShopSmart Analysis
          </h3>

          <div style={{
            padding: "1rem",
            background: "rgba(6, 182, 212, 0.08)",
            border: "1px solid rgba(6, 182, 212, 0.2)",
            borderRadius: "12px",
            marginBottom: "1rem",
            fontSize: "0.9rem",
            lineHeight: 1.6,
            color: "var(--text-primary)",
          }}>
            {ai.summary}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
            <div>
              <div style={{ fontWeight: 700, color: "var(--accent-green)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>✓ Pros</div>
              <ul style={{ fontSize: "0.82rem", color: "var(--text-secondary)", paddingLeft: "1.1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                {ai.pros?.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>
            <div>
              <div style={{ fontWeight: 700, color: "var(--accent-rose)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>✗ Cons</div>
              <ul style={{ fontSize: "0.82rem", color: "var(--text-secondary)", paddingLeft: "1.1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                {ai.cons?.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          </div>

          <div style={{
            padding: "0.75rem 1rem",
            background: "rgba(251, 191, 36, 0.1)",
            border: "1px solid rgba(251, 191, 36, 0.3)",
            borderRadius: "10px",
            fontSize: "0.85rem",
            color: "var(--accent-amber)",
            marginBottom: "0.75rem",
          }}>
            💡 <strong>Tip:</strong> {ai.savings_tip}
          </div>

          <div style={{
            padding: "0.75rem 1rem",
            background: "var(--bg-card)",
            border: "1px solid var(--border-color)",
            borderRadius: "10px",
            fontSize: "0.85rem",
            color: "var(--text-primary)",
            fontWeight: 600,
          }}>
            💡 <strong>Recommendation:</strong> {ai.recommendation}
          </div>

          {ai.explanation && (
            <div style={{
              marginTop: "0.75rem",
              padding: "0.75rem 1rem",
              background: "rgba(99, 102, 241, 0.06)",
              border: "1px solid rgba(99, 102, 241, 0.15)",
              borderRadius: "10px",
              fontSize: "0.82rem",
              color: "var(--text-secondary)",
              lineHeight: 1.6,
            }}>
              📋 <strong>How we scored this:</strong> {ai.explanation}
            </div>
          )}
        </div>
      )}

      {/* Platform Comparison */}
      {scoredListings.length > 0 && (
        <div style={{
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-color)",
          borderRadius: "16px",
          padding: "1.5rem",
        }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>
            📊 Platform Comparison ({scoredListings.length} listings)
          </h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
              <thead>
                <tr style={{ color: "var(--text-secondary)", borderBottom: "2px solid var(--border-color)", textAlign: "left" }}>
                  <th style={{ padding: "0.75rem" }}>Platform</th>
                  <th style={{ padding: "0.75rem" }}>Price</th>
                  <th style={{ padding: "0.75rem" }}>MRP</th>
                  <th style={{ padding: "0.75rem" }}>Discount</th>
                  <th style={{ padding: "0.75rem" }}>Rating</th>
                  <th style={{ padding: "0.75rem" }}>Reviews</th>
                  <th style={{ padding: "0.75rem" }}>Delivery</th>
                  <th style={{ padding: "0.75rem" }}>Offers</th>
                  <th style={{ padding: "0.75rem" }}>Coupons</th>
                  <th style={{ padding: "0.75rem" }}>Availability</th>
                  <th style={{ padding: "0.75rem" }}>Score</th>
                  <th style={{ padding: "0.75rem" }}>Source</th>
                </tr>
              </thead>
              <tbody>
                {scoredListings.map((l, i) => (
                  <tr key={i} style={{
                    background: i === 0 ? "rgba(16, 185, 129, 0.08)" : "transparent",
                    borderBottom: "1px solid var(--border-subtle)",
                  }}>
                    <td style={{ padding: "0.75rem", fontWeight: 700 }}>
                      <span style={{ color: storeColors[l.platform] || "var(--accent-cyan)" }}>●</span> {l.platform}
                      {l.is_cheapest && <span style={{
                        marginLeft: "0.4rem",
                        padding: "0.15rem 0.4rem",
                        background: "var(--accent-green)",
                        color: "#fff",
                        fontSize: "0.65rem",
                        borderRadius: "999px",
                        fontWeight: 700,
                      }}>CHEAPEST</span>}
                      {i === 0 && !l.is_cheapest && <span style={{
                        marginLeft: "0.4rem",
                        padding: "0.15rem 0.4rem",
                        background: "var(--accent-cyan)",
                        color: "#fff",
                        fontSize: "0.65rem",
                        borderRadius: "999px",
                        fontWeight: 700,
                      }}>BEST DEAL</span>}
                    </td>
                    <td style={{ padding: "0.75rem", fontWeight: 800, color: l.is_cheapest ? "var(--accent-green)" : undefined }}>
                      {l.price > 0 ? `₹${l.price?.toLocaleString("en-IN")}` : "N/A"}
                    </td>
                    <td style={{ padding: "0.75rem", color: "var(--text-muted)", textDecoration: l.mrp > l.price ? "line-through" : undefined }}>
                      {l.mrp > 0 ? `₹${l.mrp.toLocaleString("en-IN")}` : "—"}
                    </td>
                    <td style={{ padding: "0.75rem", color: "var(--accent-green)", fontWeight: 700 }}>
                      {l.mrp > l.price && l.price > 0
                        ? `${Math.round(((l.mrp - l.price) / l.mrp) * 100)}%`
                        : "—"}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {l.rating ? <span style={{ color: "var(--accent-amber)" }}>★ {l.rating}</span> : "—"}
                    </td>
                    <td style={{ padding: "0.75rem", color: "var(--text-secondary)" }}>
                      {l.review_count > 0 ? Number(l.review_count).toLocaleString("en-IN") : "—"}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {l.delivery_days ? `${l.delivery_days} day${l.delivery_days > 1 ? "s" : ""}` : "—"}
                      {l.delivery_time && (
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{l.delivery_time}</div>
                      )}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {l.coupon_code ? (
                        <span style={{ fontSize: "0.75rem", padding: "0.15rem 0.4rem", background: "rgba(245,158,11,0.12)", color: "#f59e0b", borderRadius: "4px", fontWeight: 600, border: "1px dashed rgba(245,158,11,0.3)" }}>
                          {l.coupon_code}
                        </span>
                      ) : "—"}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {l.coupon_discount > 0 ? (
                        <span style={{ fontSize: "0.75rem", padding: "0.15rem 0.4rem", background: "rgba(16,185,129,0.12)", color: "var(--accent-green)", borderRadius: "4px", fontWeight: 600 }}>
                          ₹{Number(l.coupon_discount).toLocaleString("en-IN")} off
                        </span>
                      ) : "—"}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {l.in_stock === false || l.availability === "Out of Stock" ? (
                        <span style={{ color: "var(--accent-rose)", fontSize: "0.8rem" }}>Out</span>
                      ) : (
                        <span style={{ color: "var(--accent-green)", fontSize: "0.8rem" }}>In Stock</span>
                      )}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span style={{
                        padding: "0.2rem 0.5rem",
                        background: l.score >= 75 ? "rgba(16,185,129,0.15)" : l.score >= 50 ? "rgba(251,191,36,0.15)" : "rgba(244,63,94,0.15)",
                        color: l.score >= 75 ? "var(--accent-green)" : l.score >= 50 ? "var(--accent-amber)" : "var(--accent-rose)",
                        borderRadius: "6px",
                        fontWeight: 700,
                        fontSize: "0.85rem",
                      }}>
                        {l.score}
                      </span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span style={{
                        padding: "0.15rem 0.4rem",
                        background: l.data_source === "live" ? "rgba(16, 185, 129, 0.15)" : l.data_source === "url_extract" ? "rgba(251, 191, 36, 0.15)" : "rgba(99, 102, 241, 0.15)",
                        color: l.data_source === "live" ? "var(--accent-green)" : l.data_source === "url_extract" ? "var(--accent-amber)" : "#6366f1",
                        fontSize: "0.7rem",
                        borderRadius: "4px",
                        fontWeight: 600,
                      }}>
                        {l.data_source === "live" ? "Live" : l.data_source === "demo" ? "Demo" : l.data_source === "url_extract" ? "URL" : "DB"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Specifications */}
      {product.specifications && Object.keys(product.specifications).length > 0 && (
        <div style={{
          background: "var(--bg-secondary)",
          border: "1px solid var(--border-color)",
          borderRadius: "16px",
          padding: "1.5rem",
        }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>📋 Specifications</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
            {Object.entries(product.specifications).map(([key, val]) => (
              <div key={key} style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "0.5rem 0.75rem",
                background: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "8px",
                fontSize: "0.82rem",
              }}>
                <span style={{ color: "var(--text-muted)", fontWeight: 600 }}>{key}</span>
                <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{String(val)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center", flexWrap: "wrap" }}>
        {analysisId && (
          <button
            onClick={() => navigate(`/report/${analysisId}`, { state: { analysis: { analysis_result: data } } })}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.75rem 1.5rem",
              background: "rgba(99, 102, 241, 0.12)",
              color: "#6366f1",
              border: "1px solid rgba(99, 102, 241, 0.3)",
              borderRadius: "10px",
              fontWeight: 700,
              fontSize: "0.9rem",
              cursor: "pointer",
            }}
          >
            📄 View Full Report
          </button>
        )}
        {product.source_url && (
          <a
            href={product.source_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.75rem 1.5rem",
              background: "var(--gradient-brand)",
              color: "#fff",
              borderRadius: "10px",
              fontWeight: 700,
              textDecoration: "none",
              fontSize: "0.9rem",
            }}
          >
            View on {data.platform} ↗
          </a>
        )}
        <ShareButton title={product.title} price={data.best_deal_price} />
      </div>
    </div>
  );
};

export default AnalysisResult;
