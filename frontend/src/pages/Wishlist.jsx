import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { SkeletonProductCard } from "../components/Skeleton";

const Wishlist = () => {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchWishlist = async () => {
    if (!user) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const res = await API.get("/wishlist/");
      const data = res.data;
      const list = data.results !== undefined ? data.results : data;
      setItems(Array.isArray(list) ? list : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWishlist();
    const handler = () => fetchWishlist();
    window.addEventListener("wishlist:changed", handler);
    return () => window.removeEventListener("wishlist:changed", handler);
  }, [user]);

  const remove = async (id) => {
    await API.delete(`/wishlist/${id}/`);
    setItems((prev) => prev.filter((x) => x.id !== id));
    window.dispatchEvent(new Event("wishlist:changed"));
  };

  if (!user) {
    return (
      <main className="app-wrapper" style={{ maxWidth: 800, margin: "0 auto", padding: "2rem 1.5rem" }}>
        <h2>📌 My Saved Wishlist</h2>
        <p style={{ color: "var(--text-secondary)", margin: "1rem 0" }}>
          Login to save products and track prices across platforms.
        </p>
        <Link
          to="/login"
          style={{
            display: "inline-block",
            padding: "0.6rem 1.2rem",
            background: "var(--accent-cyan)",
            color: "#fff",
            borderRadius: 8,
            textDecoration: "none",
            fontWeight: 700,
          }}
        >
          Login to View Wishlist
        </Link>
      </main>
    );
  }

  return (
    <main className="app-wrapper" style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1.5rem 3rem" }}>
      <h2 style={{ marginBottom: "0.5rem" }}>📌 My Saved Wishlist — {items.length} items</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
        Products you've saved for price tracking across Amazon, Flipkart & more.
      </p>

      {loading ? (
        <div className="product-grid">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonProductCard key={i} />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "4rem 2rem",
            background: "var(--bg-secondary)",
            borderRadius: "12px",
            border: "1px dashed var(--border-color)",
          }}
        >
          <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>🛒</div>
          <h3>Your Wishlist is Empty</h3>
          <p style={{ color: "var(--text-secondary)", margin: "0.5rem 0 1.5rem" }}>
            Products you've saved for price tracking across Amazon, Flipkart & more.
          </p>
          <Link
            to="/"
            style={{
              display: "inline-block",
              padding: "0.6rem 1.2rem",
              background: "var(--accent-blue)",
              color: "#ffffff",
              textDecoration: "none",
              borderRadius: "8px",
              fontWeight: 600,
            }}
          >
            Explore Products
          </Link>
        </div>
      ) : (
        <div className="product-grid">
          {items.map((w) => {
            const p = w.product_details || w.product;
            if (!p) return null;
            return (
              <div key={w.id} className="product-card-elevated">
                <div style={{ fontSize: "0.75rem", color: "var(--accent-cyan)", fontWeight: 700 }}>
                  {p.category} • {p.brand}
                </div>
                <Link to={`/product/${p.id}`} style={{ textDecoration: "none", color: "inherit" }}>
                  <div className="image-showcase" style={{ height: 180, margin: "0.75rem 0" }}>
                    <img src={p.image_url} alt={p.title} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain" }} />
                  </div>
                  <h3 className="product-name" style={{ height: "auto", minHeight: "2.6rem" }}>
                    {p.title}
                  </h3>
                  <div style={{ fontWeight: 800, color: "var(--accent-green)", marginBottom: "0.75rem" }}>
                    ₹{p.lowest_price ? Number(p.lowest_price).toLocaleString("en-IN") : p.offers?.[0]?.current_price ? Number(p.offers[0].current_price).toLocaleString("en-IN") : "N/A"}
                  </div>
                </Link>
                <button
                  onClick={() => remove(w.id)}
                  className="btn-card-action"
                  style={{ width: "100%", borderColor: "var(--accent-rose)", color: "var(--accent-rose)" }}
                >
                  Remove
                </button>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.5rem", textAlign: "center" }}>
                  Saved {new Date(w.added_at).toLocaleDateString("en-IN")}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
};

export default Wishlist;
