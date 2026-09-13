import React, { useState, useEffect, useCallback } from "react";
import { Link, useSearchParams } from "react-router-dom";
import API from "../api/axios";
import { SkeletonProductCard } from "../components/Skeleton";

const ProductCatalog = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ total: 0, page: 1, total_pages: 1 });

  const currentCategory = searchParams.get("category") || "";
  const currentSearch = searchParams.get("search") || "";
  const currentPage = parseInt(searchParams.get("page") || "1", 10);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (currentSearch) params.set("search", currentSearch);
      if (currentCategory) params.set("category", currentCategory);
      params.set("page", currentPage.toString());
      const res = await API.get(`/products/?${params.toString()}`);
      setProducts(res.data.products || []);
      setPagination({
        total: res.data.total || 0,
        page: res.data.page || 1,
        total_pages: res.data.total_pages || 1,
      });
    } catch {
      setProducts([]);
      setError("Failed to load products. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [currentSearch, currentCategory, currentPage]);

  const fetchCategories = useCallback(async () => {
    try {
      const res = await API.get("/categories/");
      setCategories(res.data || []);
    } catch {
      setCategories([]);
    }
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);
  useEffect(() => { fetchCategories(); }, [fetchCategories]);

  const updateParam = (key, value) => {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    if (key !== "page") next.set("page", "1");
    setSearchParams(next);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    updateParam("search", e.target.elements.search.value);
  };

  return (
    <div className="app-wrapper" style={{ padding: "0 1.5rem 4rem", maxWidth: 1200, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ padding: "2rem 0 1.5rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 800, marginBottom: "0.5rem" }}>
          Product Catalog
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          Browse {pagination.total} products across {categories.length} categories
        </p>
      </div>

      {/* Search + Filters */}
      <div style={{
        display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap",
        alignItems: "center",
      }}>
        <form onSubmit={handleSearch} style={{ flex: 1, minWidth: 200, display: "flex", gap: "0.5rem" }}>
          <input
            name="search"
            defaultValue={currentSearch}
            placeholder="Search products, brands..."
            style={{
              flex: 1, padding: "0.65rem 1rem", borderRadius: "10px",
              border: "1px solid var(--border-color)", background: "var(--bg-card)",
              color: "var(--text-primary)", fontSize: "0.9rem", outline: "none",
            }}
          />
          <button type="submit" style={{
            padding: "0.65rem 1.25rem", borderRadius: "10px", border: "none",
            background: "var(--accent-cyan)", color: "#fff", fontWeight: 700,
            fontSize: "0.85rem", cursor: "pointer",
          }}>Search</button>
        </form>
        {currentSearch && (
          <button onClick={() => updateParam("search", "")} style={{
            padding: "0.5rem 0.85rem", borderRadius: "8px",
            border: "1px solid var(--border-color)", background: "var(--bg-card)",
            color: "var(--text-secondary)", fontSize: "0.82rem", cursor: "pointer",
          }}>
            Clear search
          </button>
        )}
      </div>

      {/* Category chips */}
      {categories.length > 0 && (
        <div style={{
          display: "flex", gap: "0.5rem", marginBottom: "2rem", flexWrap: "wrap",
        }}>
          <button onClick={() => updateParam("category", "")} style={{
            padding: "0.45rem 1rem", borderRadius: "999px", border: "1px solid",
            borderColor: !currentCategory ? "var(--accent-cyan)" : "var(--border-color)",
            background: !currentCategory ? "var(--accent-cyan)" : "var(--bg-card)",
            color: !currentCategory ? "#fff" : "var(--text-secondary)",
            fontSize: "0.82rem", fontWeight: 600, cursor: "pointer",
          }}>All</button>
          {categories.map((cat) => (
            <button
              key={cat.name}
              onClick={() => updateParam("category", cat.name)}
              style={{
                padding: "0.45rem 1rem", borderRadius: "999px", border: "1px solid",
                borderColor: currentCategory === cat.name ? "var(--accent-cyan)" : "var(--border-color)",
                background: currentCategory === cat.name ? "var(--accent-cyan)" : "var(--bg-card)",
                color: currentCategory === cat.name ? "#fff" : "var(--text-secondary)",
                fontSize: "0.82rem", fontWeight: 600, cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              {cat.name} <span style={{ opacity: 0.7 }}>({cat.count})</span>
            </button>
          ))}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "1.25rem",
        }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonProductCard key={i} />
          ))}
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div style={{
          textAlign: "center", padding: "3rem 2rem",
          background: "rgba(244, 63, 94, 0.06)", border: "1px solid rgba(244, 63, 94, 0.2)",
          borderRadius: "14px", marginBottom: "1.5rem",
        }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>⚠️</div>
          <div style={{ fontSize: "1rem", fontWeight: 700, color: "var(--accent-rose)", marginBottom: "0.5rem" }}>{error}</div>
          <button onClick={fetchProducts} style={{
            padding: "0.5rem 1.2rem", borderRadius: "8px", border: "none",
            background: "var(--gradient-brand)", color: "#fff", fontWeight: 700,
            fontSize: "0.85rem", cursor: "pointer",
          }}>Try Again</button>
        </div>
      )}

      {/* Empty */}
      {!loading && !error && products.length === 0 && (
        <div style={{
          textAlign: "center", padding: "4rem 2rem",
          background: "var(--bg-secondary)", border: "1px solid var(--border-color)",
          borderRadius: "14px",
        }}>
          <div style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>📦</div>
          <div style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.35rem" }}>No products found</div>
          <div style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>
            Try a different search or category
          </div>
        </div>
      )}

      {/* Product Grid */}
      {!loading && products.length > 0 && (
        <>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(min(280px, 100%), 1fr))",
            gap: "1.25rem",
          }}>
            {products.map((p) => (
              <Link key={p.id} to={`/product/${p.id}`} style={{ textDecoration: "none" }}>
                <div style={{
                  background: "var(--bg-card)", border: "1px solid var(--border-color)",
                  borderRadius: "14px", padding: "1rem", height: "100%",
                  display: "flex", flexDirection: "column", transition: "all 0.25s ease",
                  cursor: "pointer",
                }} onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.borderColor = "rgba(6, 182, 212, 0.4)";
                  e.currentTarget.style.boxShadow = "0 12px 24px -8px rgba(0, 0, 0, 0.3)";
                }} onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "var(--border-color)";
                  e.currentTarget.style.boxShadow = "none";
                }}>
                  {p.image_url && (
                    <div style={{
                      height: 160, borderRadius: 10, overflow: "hidden",
                      background: "linear-gradient(135deg, rgba(6,182,212,0.05) 0%, rgba(59,130,246,0.05) 100%)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      marginBottom: "0.75rem",
                    }}>
                      <img src={p.image_url} alt={p.title} style={{
                        maxWidth: "100%", maxHeight: "100%", objectFit: "contain",
                      }} onError={(e) => {
                        e.target.style.display = "none";
                      }} />
                    </div>
                  )}
                  {!p.image_url && (
                    <div style={{
                      height: 160, borderRadius: 10,
                      background: "linear-gradient(135deg, rgba(6,182,212,0.05) 0%, rgba(59,130,246,0.05) 100%)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      marginBottom: "0.75rem", fontSize: "2.5rem", color: "var(--text-muted)",
                    }}>📦</div>
                  )}
                  <div style={{
                    fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase",
                    letterSpacing: "0.05em", color: "var(--accent-cyan)", marginBottom: "0.35rem",
                  }}>{p.brand || p.category}</div>
                  <div style={{
                    fontWeight: 700, fontSize: "0.95rem", lineHeight: 1.4,
                    marginBottom: "0.5rem", color: "var(--text-primary)",
                    display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
                    overflow: "hidden", height: "2.7rem",
                  }}>{p.title}</div>
                  {p.lowest_price && (
                    <div style={{ marginTop: "auto", display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
                      <span style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--accent-green)" }}>
                        ₹{Number(p.lowest_price).toLocaleString("en-IN")}
                      </span>
                      {p.platforms_available && p.platforms_available.length > 0 && (
                        <span style={{
                          fontSize: "0.7rem", color: "var(--text-muted)", fontWeight: 600,
                        }}>
                          {p.platforms_available.length} platform{p.platforms_available.length > 1 ? "s" : ""}
                        </span>
                      )}
                    </div>
                  )}
                  {!p.lowest_price && (
                    <div style={{ marginTop: "auto", fontSize: "0.82rem", color: "var(--text-muted)" }}>
                      Price unavailable
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {pagination.total_pages > 1 && (
            <div style={{
              display: "flex", justifyContent: "center", gap: "0.5rem",
              marginTop: "2rem", flexWrap: "wrap",
            }}>
              <button
                disabled={currentPage <= 1}
                onClick={() => updateParam("page", (currentPage - 1).toString())}
                style={{
                  padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid var(--border-color)",
                  background: "var(--bg-card)", color: currentPage <= 1 ? "var(--text-muted)" : "var(--text-primary)",
                  fontWeight: 600, fontSize: "0.85rem", cursor: currentPage <= 1 ? "default" : "pointer",
                }}
              >← Prev</button>
              <span style={{
                padding: "0.5rem 0.85rem", fontSize: "0.85rem", color: "var(--text-secondary)",
                fontWeight: 600,
              }}>
                Page {currentPage} of {pagination.total_pages}
              </span>
              <button
                disabled={currentPage >= pagination.total_pages}
                onClick={() => updateParam("page", (currentPage + 1).toString())}
                style={{
                  padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid var(--border-color)",
                  background: "var(--bg-card)",
                  color: currentPage >= pagination.total_pages ? "var(--text-muted)" : "var(--text-primary)",
                  fontWeight: 600, fontSize: "0.85rem",
                  cursor: currentPage >= pagination.total_pages ? "default" : "pointer",
                }}
              >Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProductCatalog;
