import React, { useEffect, useState, useRef } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  LineChart, Line, Legend, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar, Cell
} from "recharts";
import API from "../api/axios";
import ShareButton from "../components/ShareButton";

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

const scoreColor = (s) => s >= 80 ? "#10b981" : s >= 60 ? "#06b6d4" : s >= 40 ? "#f59e0b" : "#f43f5e";

const DecisionReport = () => {
  const { id } = useParams();
  const location = useLocation();
  const reportRef = useRef();

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [priceHistory, setPriceHistory] = useState(null);

  const data = analysis?.analysis_result || analysis;
  const product = data?.product || {};
  const comparison = data?.comparisons || {};
  const ai = data?.ai_analysis || {};
  const listings = ai.scored_listings || comparison.listings || [];
  const bestDeal = listings[0] || null;
  const reportDate = new Date().toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });

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
          if (found.analysis_result?.product?.id) {
            return API.get(`/products/${found.analysis_result.product.id}/history/`);
          }
        } else {
          setError("Analysis not found");
        }
      })
      .then((res) => {
        if (res?.data) setPriceHistory(res.data);
      })
      .catch(() => setError("Failed to load analysis"))
      .finally(() => setLoading(false));
  }, [id, location.state]);

  useEffect(() => {
    if (data?.product?.id && !location.state?.analysis) {
      API.get(`/products/${data.product.id}/history/`)
        .then((res) => setPriceHistory(res.data))
        .catch(() => {});
    }
  }, [data?.product?.id, location.state?.analysis]);

  const handlePrint = () => window.print();

  if (loading) {
    return (
      <div className="app-wrapper" style={{ maxWidth: 1100, margin: "0 auto", padding: "4rem 1.5rem", textAlign: "center" }}>
        <div style={{ fontSize: "1.2rem", color: "var(--text-muted)" }}>Generating your decision report...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="app-wrapper" style={{ maxWidth: 1100, margin: "0 auto", padding: "4rem 1.5rem", textAlign: "center" }}>
        <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>🔍</div>
        <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent-rose)" }}>{error || "Report not found"}</div>
        <Link to="/" style={{ display: "inline-block", marginTop: "1rem", padding: "0.6rem 1.2rem", background: "var(--accent-cyan)", color: "#fff", borderRadius: "8px", textDecoration: "none", fontWeight: 700 }}>← Back to Home</Link>
      </div>
    );
  }

  const scoreData = listings.map((l) => ({ name: l.platform, score: l.score || 0 }));
  const subScoreData = bestDeal?.sub_scores
    ? Object.entries(bestDeal.sub_scores).map(([k, v]) => ({
        factor: k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        score: Math.round(v),
        fullMark: 100,
      }))
    : [];
  const priceCompareData = listings.map((l) => ({ name: l.platform, price: l.price || 0 }));
  const reviewData = listings.filter((l) => l.rating).map((l) => ({ name: l.platform, rating: l.rating, reviews: l.review_count || 0 }));
  const verdictColor = ai.deal_assessment?.toLowerCase().includes("excellent") ? "#10b981"
    : ai.deal_assessment?.toLowerCase().includes("good") ? "#06b6d4"
    : ai.deal_assessment?.toLowerCase().includes("fair") ? "#f59e0b" : "#f43f5e";

  return (
    <div className="app-wrapper" style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1.5rem 3rem" }}>
      {/* Top Controls */}
      <div className="no-print" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem", marginBottom: "1.5rem" }}>
        <Link to="/" style={{ color: "var(--accent-cyan)", textDecoration: "none", fontSize: "0.9rem", fontWeight: 600 }}>← Back to Home</Link>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={handlePrint} style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem", padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid var(--border-color)", background: "var(--bg-secondary)", color: "var(--text-primary)", fontWeight: 600, fontSize: "0.85rem", cursor: "pointer" }}>🖨️ Print Report</button>
          <ShareButton title={product.title} price={bestDeal?.price} />
        </div>
      </div>

      <div ref={reportRef}>
        {/* Report Header */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>ShopSmart Decision Report</div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 800, lineHeight: 1.3, marginBottom: "0.5rem" }}>{product.title}</h1>
          <div style={{ display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            {product.brand && <span>Brand: <strong>{product.brand}</strong></span>}
            {product.category && <span>Category: <strong>{product.category}</strong></span>}
            <span>Platforms Compared: <strong>{listings.length}</strong></span>
            <span>Generated: <strong>{reportDate}</strong></span>
          </div>
        </div>

        {/* Verdict Banner */}
        <div style={{
          background: `linear-gradient(135deg, ${verdictColor}15 0%, ${verdictColor}08 100%)`,
          border: `2px solid ${verdictColor}40`,
          borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem",
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <div style={{ fontSize: "2.5rem" }}>
                {ai.deal_assessment?.toLowerCase().includes("excellent") ? "🎯" : ai.deal_assessment?.toLowerCase().includes("good") ? "👍" : ai.deal_assessment?.toLowerCase().includes("fair") ? "⚖️" : "⚠️"}
              </div>
              <div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Overall Verdict</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 800, color: verdictColor }}>{ai.deal_assessment || "Analysis Complete"}</div>
              </div>
            </div>
            {bestDeal && (
              <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Best Deal Score</div>
                  <div style={{ fontSize: "2rem", fontWeight: 800, color: scoreColor(bestDeal.score) }}>{bestDeal.score}<span style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>/100</span></div>
                </div>
                {ai.confidence && (
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Confidence</div>
                    <div style={{ fontSize: "1rem", fontWeight: 700, color: ai.confidence.level === "high" ? "var(--accent-green)" : ai.confidence.level === "medium" ? "var(--accent-amber)" : "var(--accent-rose)" }}>{ai.confidence.label}</div>
                  </div>
                )}
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Best Price</div>
                  <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-green)" }}>₹{bestDeal.price?.toLocaleString("en-IN")}</div>
                  <div style={{ fontSize: "0.75rem", color: storeColors[bestDeal.platform] || "var(--text-primary)", fontWeight: 600 }}>{bestDeal.platform}</div>
                </div>
              </div>
            )}
          </div>
          {ai.summary && (
            <div style={{ marginTop: "1rem", fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: 1.6, borderTop: `1px solid ${verdictColor}20`, paddingTop: "0.75rem" }}>
              {ai.summary}
            </div>
          )}
        </div>

        {/* Score Breakdown */}
        {subScoreData.length > 0 && (
          <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>📊 Score Breakdown — {bestDeal.platform}</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", alignItems: "center" }}>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={subScoreData}>
                  <PolarGrid stroke="var(--border-subtle)" />
                  <PolarAngleAxis dataKey="factor" tick={{ fill: "var(--text-secondary)", fontSize: 11 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 10 }} />
                  <Radar name="Score" dataKey="score" stroke="var(--accent-cyan)" fill="var(--accent-cyan)" fillOpacity={0.25} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                {subScoreData.map(({ factor, score }) => (
                  <div key={factor} style={{ padding: "0.5rem 0.7rem", background: "var(--bg-card)", border: "1px solid var(--border-subtle)", borderRadius: "8px", fontSize: "0.78rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                      <span style={{ color: "var(--text-secondary)", fontWeight: 600 }}>{factor}</span>
                      <span style={{ fontWeight: 700, color: scoreColor(score) }}>{score}</span>
                    </div>
                    <div style={{ height: 5, background: "var(--bg-secondary)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: `${score}%`, height: "100%", background: scoreColor(score), borderRadius: 3 }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Price Comparison */}
        {priceCompareData.length > 0 && (
          <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>💰 Price Comparison</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={priceCompareData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis type="number" tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="name" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} width={110} />
                <Tooltip formatter={(v) => `₹${v.toLocaleString("en-IN")}`} contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 8 }} />
                <Bar dataKey="price" radius={[0, 6, 6, 0]}>
                  {priceCompareData.map((entry) => (
                    <Cell key={entry.name} fill={storeColors[entry.name] || "var(--accent-cyan)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {/* Price table */}
            <div style={{ marginTop: "1rem", overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
                <thead>
                  <tr style={{ color: "var(--text-muted)", borderBottom: "1px solid var(--border-color)" }}>
                    <th style={{ padding: "0.5rem", textAlign: "left" }}>Platform</th>
                    <th style={{ padding: "0.5rem", textAlign: "right" }}>Price</th>
                    <th style={{ padding: "0.5rem", textAlign: "right" }}>MRP</th>
                    <th style={{ padding: "0.5rem", textAlign: "right" }}>Savings</th>
                    <th style={{ padding: "0.5rem", textAlign: "center" }}>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {listings.map((l, i) => (
                    <tr key={i} style={{ background: i === 0 ? "rgba(16,185,129,0.06)" : "transparent", borderBottom: "1px solid var(--border-subtle)" }}>
                      <td style={{ padding: "0.5rem", fontWeight: 700 }}>
                        <span style={{ color: storeColors[l.platform] || "var(--accent-cyan)" }}>●</span> {l.platform}
                        {i === 0 && <span style={{ marginLeft: "0.4rem", padding: "0.1rem 0.35rem", background: "var(--accent-green)", color: "#fff", fontSize: "0.6rem", borderRadius: "999px", fontWeight: 700 }}>BEST</span>}
                      </td>
                      <td style={{ padding: "0.5rem", textAlign: "right", fontWeight: 700 }}>{l.price > 0 ? `₹${l.price.toLocaleString("en-IN")}` : "—"}</td>
                      <td style={{ padding: "0.5rem", textAlign: "right", color: "var(--text-muted)", textDecoration: l.mrp > l.price ? "line-through" : undefined }}>{l.mrp > 0 ? `₹${l.mrp.toLocaleString("en-IN")}` : "—"}</td>
                      <td style={{ padding: "0.5rem", textAlign: "right", color: "var(--accent-green)", fontWeight: 600 }}>{l.mrp > l.price && l.price > 0 ? `₹${(l.mrp - l.price).toLocaleString("en-IN")}` : "—"}</td>
                      <td style={{ padding: "0.5rem", textAlign: "center" }}>
                        <span style={{ padding: "0.15rem 0.4rem", background: `${scoreColor(l.score)}20`, color: scoreColor(l.score), borderRadius: "4px", fontWeight: 700, fontSize: "0.8rem" }}>{l.score}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Price History Chart */}
        {priceHistory && priceHistory.history && priceHistory.history.length > 0 && (() => {
          const grouped = {};
          priceHistory.history.forEach((h) => {
            if (!grouped[h.store_name]) grouped[h.store_name] = [];
            grouped[h.store_name].push({ date: h.recorded_at?.split("T")[0] || h.recorded_at, price: parseFloat(h.price) });
          });
          const allDates = [...new Set(priceHistory.history.map((h) => h.recorded_at?.split("T")[0]))].sort();
          const chartData = allDates.map((d) => {
            const pt = { date: d };
            Object.keys(grouped).forEach((store) => {
              const rec = grouped[store].find((r) => r.date === d);
              if (rec) pt[store] = rec.price;
            });
            return pt;
          });
          const platforms = Object.keys(grouped);
          return (
            <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>📈 Price Trend (30 Days)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                  <XAxis dataKey="date" tick={{ fill: "var(--text-muted)", fontSize: 10 }} tickFormatter={(d) => d?.slice(5)} />
                  <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} domain={["dataMin - 1000", "dataMax + 1000"]} />
                  <Tooltip contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 8 }} formatter={(v) => `₹${v.toLocaleString("en-IN")}`} />
                  <Legend />
                  {platforms.map((p) => (
                    <Line key={p} type="monotone" dataKey={p} stroke={storeColors[p] || "#999"} strokeWidth={2} dot={false} connectNulls />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          );
        })()}

        {/* AI Insights */}
        {(ai.pros?.length > 0 || ai.cons?.length > 0 || ai.savings_tip || ai.recommendation) && (
          <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>🤖 ShopSmart AI Insights</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
              {ai.pros?.length > 0 && (
                <div style={{ padding: "1rem", background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.15)", borderRadius: "10px" }}>
                  <div style={{ fontWeight: 700, color: "var(--accent-green)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>✓ Pros</div>
                  <ul style={{ fontSize: "0.82rem", color: "var(--text-secondary)", paddingLeft: "1.1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                    {ai.pros.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              )}
              {ai.cons?.length > 0 && (
                <div style={{ padding: "1rem", background: "rgba(244,63,94,0.06)", border: "1px solid rgba(244,63,94,0.15)", borderRadius: "10px" }}>
                  <div style={{ fontWeight: 700, color: "var(--accent-rose)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>✗ Cons</div>
                  <ul style={{ fontSize: "0.82rem", color: "var(--text-secondary)", paddingLeft: "1.1rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                    {ai.cons.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              {ai.savings_tip && (
                <div style={{ padding: "0.75rem 1rem", background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.2)", borderRadius: "10px", fontSize: "0.85rem", color: "var(--accent-amber)" }}>
                  💡 <strong>Tip:</strong> {ai.savings_tip}
                </div>
              )}
              {ai.recommendation && (
                <div style={{ padding: "0.75rem 1rem", background: "rgba(6,182,212,0.08)", border: "1px solid rgba(6,182,212,0.2)", borderRadius: "10px", fontSize: "0.85rem", color: "var(--text-primary)" }}>
                  🎯 <strong>Recommendation:</strong> {ai.recommendation}
                </div>
              )}
              {ai.explanation && (
                <div style={{ padding: "0.75rem 1rem", background: "rgba(99,102,241,0.06)", border: "1px solid rgba(99,102,241,0.15)", borderRadius: "10px", fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                  📋 <strong>How we scored:</strong> {ai.explanation}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recommendation Categories */}
        {ai.recommendation_categories?.length > 0 && (
          <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>🏅 Best For Each Category</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "0.75rem" }}>
              {ai.recommendation_categories.map((cat, i) => (
                <div key={i} style={{ padding: "0.8rem 1rem", background: i === 0 ? "rgba(16,185,129,0.08)" : "var(--bg-card)", border: i === 0 ? "1px solid rgba(16,185,129,0.3)" : "1px solid var(--border-subtle)", borderRadius: "10px" }}>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.03em", fontWeight: 600, marginBottom: "0.25rem" }}>{cat.category}</div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <span style={{ fontWeight: 700, color: storeColors[cat.platform] || "var(--text-primary)" }}>{cat.platform}</span>
                      <span style={{ color: "var(--text-muted)", margin: "0 0.3rem" }}>·</span>
                      <span style={{ fontWeight: 700, color: "var(--accent-green)" }}>₹{cat.price?.toLocaleString("en-IN")}</span>
                    </div>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "0.15rem 0.4rem", borderRadius: "6px", background: `${scoreColor(cat.score)}20`, color: scoreColor(cat.score) }}>{cat.score}</span>
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>{cat.reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Specifications */}
        {product.specifications && Object.keys(product.specifications).length > 0 && (
          <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: "1rem" }}>📋 Product Specifications</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "0.5rem" }}>
              {Object.entries(product.specifications).map(([key, val]) => (
                <div key={key} style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0.75rem", background: "var(--bg-card)", border: "1px solid var(--border-subtle)", borderRadius: "8px", fontSize: "0.82rem" }}>
                  <span style={{ color: "var(--text-muted)", fontWeight: 600 }}>{key}</span>
                  <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{String(val)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{ textAlign: "center", padding: "1.5rem 0", borderTop: "1px solid var(--border-color)", marginTop: "1rem" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.6 }}>
            Generated by <strong style={{ color: "var(--accent-cyan)" }}>ShopSmart</strong> AI-Powered Product Comparison Platform<br />
            Report Date: {reportDate} · Data Sources: {listings.map((l) => l.platform).join(", ")}<br />
            {ai.confidence && <>Confidence Level: {ai.confidence.label} · </>}
            Prices and availability may change. Always verify before purchasing.
          </div>
        </div>
      </div>
    </div>
  );
};

export default DecisionReport;
