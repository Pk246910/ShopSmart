import React, { useEffect, useState, useCallback } from "react";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

const TABS = [
  { key: "dashboard", label: "Dashboard", icon: "📊" },
  { key: "products", label: "Products", icon: "📦" },
  { key: "users", label: "Users", icon: "👥" },
  { key: "analyses", label: "Analyses", icon: "📋" },
  { key: "offers", label: "Offers", icon: "🛒" },
];

const Admin = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [verified, setVerified] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [adminForm, setAdminForm] = useState({ username: "", password: "" });

  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);

  const [products, setProducts] = useState([]);
  const [productsLoading, setProductsLoading] = useState(false);
  const [productsPage, setProductsPage] = useState(1);
  const [productsCount, setProductsCount] = useState(0);
  const [productsSearch, setProductsSearch] = useState("");
  const [productsSort, setProductsSort] = useState("id");
  const [expandedProduct, setExpandedProduct] = useState(null);
  const [productOffers, setProductOffers] = useState([]);

  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);

  const [analyses, setAnalyses] = useState([]);
  const [analysesLoading, setAnalysesLoading] = useState(false);

  const [offers, setOffers] = useState([]);
  const [offersLoading, setOffersLoading] = useState(false);
  const [offersPlatform, setOffersPlatform] = useState("");
  const [offersSort, setOffersSort] = useState("");
  const [platforms, setPlatforms] = useState([]);

  useEffect(() => {
    if (!user) { navigate("/login"); return; }
    API.get("/users/me/")
      .then((res) => {
        const fresh = res.data;
        if (!fresh.is_staff && !fresh.is_superuser) {
          setError("Access denied — Admin only. You are logged in as " + fresh.username);
          setLoading(false);
          return;
        }
        setVerified(true);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to verify admin credentials.");
        setLoading(false);
      });
  }, [user, navigate]);

  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const res = await API.get("/users/admin-stats/");
      setStats(res.data);
    } catch (e) {
      setStats(null);
    }
    setStatsLoading(false);
  }, []);

  const fetchProducts = useCallback(async () => {
    setProductsLoading(true);
    try {
      const params = { page: productsPage, search: productsSearch, sort: productsSort };
      const res = await API.get("/admin/products/", { params });
      const data = res.data;
      if (Array.isArray(data)) {
        setProducts(data);
        setProductsCount(data.length);
      } else {
        setProducts(data.results || []);
        setProductsCount(data.total || data.count || 0);
      }
    } catch {
      setProducts([]);
    }
    setProductsLoading(false);
  }, [productsPage, productsSearch, productsSort]);

  const fetchUsers = useCallback(async () => {
    setUsersLoading(true);
    try {
      const res = await API.get("/users/");
      const data = res.data;
      setUsers(Array.isArray(data) ? data : data.results || []);
    } catch {
      setUsers([]);
    }
    setUsersLoading(false);
  }, []);

  const fetchAnalyses = useCallback(async () => {
    setAnalysesLoading(true);
    try {
      const res = await API.get("/admin/analyses/");
      const data = res.data;
      setAnalyses(data.results || (Array.isArray(data) ? data : []));
    } catch {
      setAnalyses([]);
    }
    setAnalysesLoading(false);
  }, []);

  const fetchOffers = useCallback(async () => {
    setOffersLoading(true);
    try {
      const params = {};
      if (offersPlatform) params.platform = offersPlatform;
      if (offersSort) params.ordering = offersSort;
      const res = await API.get("/admin/offers/", { params });
      const data = res.data;
      setOffers(data.results || (Array.isArray(data) ? data : []));
    } catch {
      setOffers([]);
    }
    setOffersLoading(false);
  }, [offersPlatform, offersSort]);

  const fetchPlatforms = useCallback(async () => {
    try {
      const res = await API.get("/admin/platforms/");
      const data = res.data;
      setPlatforms(Array.isArray(data) ? data : data.results || []);
    } catch {
      setPlatforms([]);
    }
  }, []);

  useEffect(() => {
    if (!verified) return;
    if (activeTab === "dashboard") fetchStats();
    if (activeTab === "products") fetchProducts();
    if (activeTab === "users") fetchUsers();
    if (activeTab === "analyses") fetchAnalyses();
    if (activeTab === "offers") { fetchOffers(); fetchPlatforms(); }
  }, [activeTab, verified, fetchStats, fetchProducts, fetchUsers, fetchAnalyses, fetchOffers, fetchPlatforms]);

  useEffect(() => {
    if (verified && activeTab === "products") fetchProducts();
  }, [productsPage, productsSearch, productsSort, verified, activeTab, fetchProducts]);

  const handleSeed = async () => {
    try {
      await API.post("/users/admin-stats/", { action: "seed" });
      toast.success("Database seeded successfully.");
      fetchStats();
    } catch (e) {
      toast.error("Failed: " + (e.response?.data?.detail || "Error"));
    }
  };

  const handlePromote = async (u) => {
    try {
      await API.post(`/users/${u.id}/promote/`, { action: "promote" });
      setUsers((prev) => prev.map((x) => x.id === u.id ? { ...x, is_staff: true, is_superuser: true } : x));
      toast.success(u.username + " promoted to staff.");
    } catch (e) {
      toast.error("Failed: " + (e.response?.data?.detail || "Error"));
    }
  };

  const handleDemote = async (u) => {
    try {
      await API.post(`/users/${u.id}/promote/`, { action: "demote" });
      setUsers((prev) => prev.map((x) => x.id === u.id ? { ...x, is_staff: false, is_superuser: false } : x));
      toast.success(u.username + " demoted to regular user.");
    } catch (e) {
      toast.error("Failed: " + (e.response?.data?.detail || "Error"));
    }
  };

  const handleDeleteProduct = async (id) => {
    if (!window.confirm("Delete this product permanently?")) return;
    try {
      await API.delete(`/admin/products/${id}/`);
      setProducts((prev) => prev.filter((p) => p.id !== id));
    } catch {
      toast.error("Failed to delete product.");
    }
  };

  const handleViewOffers = async (product) => {
    if (expandedProduct === product.id) { setExpandedProduct(null); return; }
    setExpandedProduct(product.id);
    setProductOffers([]);
    try {
      const res = await API.get(`/admin/products/${product.id}/offers/`);
      const data = res.data;
      setProductOffers(Array.isArray(data) ? data : data.results || []);
    } catch {
      setProductOffers([]);
    }
  };

  const handleAdminLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("/users/login/", adminForm);
      localStorage.setItem("shopsmart_access", res.data.access);
      localStorage.setItem("shopsmart_refresh", res.data.refresh);
      const me = await API.get("/users/me/", { headers: { Authorization: `Bearer ${res.data.access}` } });
      if (!me.data.is_staff && !me.data.is_superuser) {
        toast.error("Not a staff account.");
        return;
      }
      localStorage.setItem("shopsmart_user", JSON.stringify(me.data));
      window.location.reload();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Login failed.");
    }
  };

  const cardStyle = {
    background: "var(--bg-card)",
    border: "1px solid var(--border-color)",
    borderRadius: 12,
    padding: "1.25rem",
  };

  const inputStyle = {
    padding: "0.6rem 0.8rem",
    borderRadius: 8,
    border: "1px solid var(--border-color)",
    background: "var(--bg-card)",
    color: "var(--text-primary)",
    fontSize: "0.85rem",
    outline: "none",
  };

  const btnPrimary = {
    background: "var(--accent-cyan)",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "0.45rem 1rem",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "0.8rem",
  };

  const btnDanger = {
    background: "var(--accent-rose)",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "0.3rem 0.7rem",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "0.75rem",
  };

  const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "0.85rem",
  };

  const thStyle = {
    textAlign: "left",
    padding: "0.7rem 0.6rem",
    borderBottom: "2px solid var(--border-color)",
    color: "var(--text-secondary)",
    fontWeight: 700,
    fontSize: "0.78rem",
    textTransform: "uppercase",
    letterSpacing: "0.03em",
  };

  const tdStyle = {
    padding: "0.6rem",
    borderBottom: "1px solid var(--border-color)",
    color: "var(--text-primary)",
  };

  const badgeStyle = (color) => ({
    display: "inline-block",
    padding: "0.15rem 0.55rem",
    borderRadius: 20,
    fontSize: "0.72rem",
    fontWeight: 700,
    background: color === "cyan" ? "rgba(6,182,212,0.15)" : color === "rose" ? "rgba(244,63,94,0.15)" : "rgba(168,85,247,0.15)",
    color: color === "cyan" ? "var(--accent-cyan)" : color === "rose" ? "var(--accent-rose)" : "var(--accent-purple)",
  });

  if (loading) {
    return (
      <div style={{ padding: "4rem", textAlign: "center", color: "var(--text-secondary)", fontSize: "1rem" }}>
        <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>⏳</div>
        Verifying admin access...
      </div>
    );
  }

  if (!verified) {
    return (
      <div style={{ padding: "2rem", maxWidth: 460, margin: "3rem auto" }}>
        <div style={{ ...cardStyle, background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.25)", marginBottom: "1rem", color: "var(--accent-rose)", fontSize: "0.9rem" }}>
          {error || "You do not have admin access."}
        </div>
        <div style={cardStyle}>
          <h3 style={{ fontWeight: 800, marginBottom: "0.2rem", fontSize: "1.1rem" }}>🔐 Admin Login</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", marginBottom: "1rem" }}>
            Enter staff credentials to continue.
          </p>
          <form onSubmit={handleAdminLogin} style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
            <input
              placeholder="Username"
              value={adminForm.username}
              onChange={(e) => setAdminForm({ ...adminForm, username: e.target.value })}
              required
              style={{ ...inputStyle, padding: "0.7rem" }}
            />
            <input
              type="password"
              placeholder="Password"
              value={adminForm.password}
              onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })}
              required
              style={{ ...inputStyle, padding: "0.7rem" }}
            />
            <button type="submit" style={{ ...btnPrimary, padding: "0.7rem", fontSize: "0.9rem", borderRadius: 10 }}>
              Login as Admin
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-primary)" }}>
      {/* Sidebar */}
      <aside style={{
        width: 240,
        minWidth: 240,
        background: "var(--bg-secondary)",
        borderRight: "1px solid var(--border-color)",
        padding: "1.5rem 0",
        display: "flex",
        flexDirection: "column",
        position: "sticky",
        top: 0,
        height: "100vh",
        overflowY: "auto",
      }}>
        <div style={{ padding: "0 1.25rem 1.25rem", borderBottom: "1px solid var(--border-color)", marginBottom: "0.75rem" }}>
          <div style={{ fontWeight: 800, fontSize: "1.05rem", color: "var(--text-primary)" }}>🛡️ ShopSmart</div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.15rem" }}>Admin Panel</div>
        </div>
        <nav style={{ display: "flex", flexDirection: "column", gap: "2px", padding: "0 0.5rem", flex: 1 }}>
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.6rem",
                padding: "0.6rem 0.8rem",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
                fontSize: "0.88rem",
                fontWeight: activeTab === tab.key ? 700 : 500,
                background: activeTab === tab.key ? "rgba(6,182,212,0.12)" : "transparent",
                color: activeTab === tab.key ? "var(--accent-cyan)" : "var(--text-secondary)",
                textAlign: "left",
                transition: "all 0.15s",
              }}
            >
              <span style={{ fontSize: "1.1rem" }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
        <div style={{ padding: "1rem 1.25rem", borderTop: "1px solid var(--border-color)", fontSize: "0.78rem", color: "var(--text-muted)" }}>
          Logged in as <strong style={{ color: "var(--text-primary)" }}>{user?.username}</strong>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, padding: "2rem 2.5rem", overflowY: "auto", minWidth: 0 }}>
        {activeTab === "dashboard" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
              <div>
                <h2 style={{ fontWeight: 800, fontSize: "1.4rem", margin: 0 }}>Dashboard</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", margin: "0.3rem 0 0" }}>Overview of your platform</p>
              </div>
              {import.meta.env.DEV && (
                <button onClick={handleSeed} style={{ ...btnPrimary, padding: "0.5rem 1.2rem", fontSize: "0.82rem" }}>
                  🌱 Seed Database
                </button>
              )}
            </div>
            {statsLoading ? (
              <div style={{ color: "var(--text-secondary)", padding: "2rem", textAlign: "center" }}>Loading stats...</div>
            ) : stats ? (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
                  {[
                    { label: "Total Users", value: stats.users, icon: "👥", color: "var(--accent-cyan)" },
                    { label: "Total Products", value: stats.products, icon: "📦", color: "var(--accent-purple)" },
                    { label: "Total Offers", value: stats.offers, icon: "🏷️", color: "var(--accent-rose)" },
                    { label: "Wishlists", value: stats.wishlists, icon: "💜", color: "var(--accent-purple)" },
                    { label: "Analyses", value: stats.analyses, icon: "🔍", color: "var(--accent-cyan)" },
                    { label: "Platforms", value: stats.platforms, icon: "🌐", color: "var(--accent-rose)" },
                  ].map((item) => (
                    <div key={item.label} style={{ ...cardStyle, display: "flex", alignItems: "center", gap: "1rem" }}>
                      <div style={{ fontSize: "2rem" }}>{item.icon}</div>
                      <div>
                        <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.03em" }}>{item.label}</div>
                        <div style={{ fontSize: "1.8rem", fontWeight: 800, color: item.color, lineHeight: 1.1 }}>{item.value ?? 0}</div>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={cardStyle}>
                  <h3 style={{ fontWeight: 700, fontSize: "1rem", marginBottom: "0.75rem" }}>Recent Users</h3>
                  {(stats.recent_users || []).length === 0 ? (
                    <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No recent users.</div>
                  ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                      {(stats.recent_users || []).slice(0, 5).map((u) => (
                        <div key={u.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.55rem 0.75rem", background: "var(--bg-secondary)", borderRadius: 8 }}>
                          <span style={{ fontSize: "0.85rem" }}>
                            <strong>{u.username}</strong>
                            <span style={{ color: "var(--text-muted)", margin: "0 0.4rem" }}>•</span>
                            <span style={{ color: "var(--text-secondary)" }}>{u.email}</span>
                          </span>
                          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                            {new Date(u.date_joined).toLocaleDateString("en-IN")}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div style={{ color: "var(--text-muted)" }}>No stats available.</div>
            )}
          </div>
        )}

        {activeTab === "products" && (
          <div>
            <h2 style={{ fontWeight: 800, fontSize: "1.4rem", marginBottom: "1rem" }}>Products</h2>
            <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", alignItems: "center" }}>
              <input
                placeholder="Search products..."
                value={productsSearch}
                onChange={(e) => { setProductsSearch(e.target.value); setProductsPage(1); }}
                style={{ ...inputStyle, flex: 1, padding: "0.6rem 0.8rem" }}
              />
              <select value={productsSort} onChange={(e) => setProductsSort(e.target.value)} style={{ ...inputStyle, padding: "0.55rem" }}>
                <option value="id">Sort by ID</option>
                <option value="title">Sort by Title</option>
                <option value="brand">Sort by Brand</option>
                <option value="category">Sort by Category</option>
                <option value="-id">ID (Desc)</option>
              </select>
            </div>
            {productsLoading ? (
              <div style={{ color: "var(--text-secondary)", padding: "2rem", textAlign: "center" }}>Loading products...</div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={tableStyle}>
                  <thead>
                    <tr>
                      <th style={thStyle}>ID</th>
                      <th style={thStyle}>Image</th>
                      <th style={thStyle}>Title</th>
                      <th style={thStyle}>Brand</th>
                      <th style={thStyle}>Category</th>
                      <th style={thStyle}>Offers</th>
                      <th style={thStyle}>Created</th>
                      <th style={thStyle}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => (
                      <React.Fragment key={p.id}>
                        <tr>
                          <td style={tdStyle}>{p.id}</td>
                          <td style={tdStyle}>
                            {p.image_url ? (
                              <img src={p.image_url} alt="" style={{ width: 36, height: 36, borderRadius: 6, objectFit: "cover" }} />
                            ) : (
                              <div style={{ width: 36, height: 36, borderRadius: 6, background: "var(--bg-secondary)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.7rem", color: "var(--text-muted)" }}>N/A</div>
                            )}
                          </td>
                          <td style={{ ...tdStyle, maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{p.title}</td>
                          <td style={tdStyle}>{p.brand || "—"}</td>
                          <td style={tdStyle}>{p.category || "—"}</td>
                          <td style={tdStyle}>
                            <span style={badgeStyle("cyan")}>{p.offers_count ?? p.num_offers ?? "—"}</span>
                          </td>
                          <td style={{ ...tdStyle, color: "var(--text-muted)", fontSize: "0.8rem" }}>
                            {p.created_at ? new Date(p.created_at).toLocaleDateString("en-IN") : "—"}
                          </td>
                          <td style={{ ...tdStyle, display: "flex", gap: "0.4rem" }}>
                            <button onClick={() => handleViewOffers(p)} style={{ ...btnPrimary, fontSize: "0.75rem", padding: "0.3rem 0.6rem" }}>
                              {expandedProduct === p.id ? "Hide" : "View"}
                            </button>
                            <button onClick={() => handleDeleteProduct(p.id)} style={btnDanger}>
                              Delete
                            </button>
                          </td>
                        </tr>
                        {expandedProduct === p.id && (
                          <tr>
                            <td colSpan={8} style={{ padding: "0.75rem", background: "var(--bg-secondary)" }}>
                              <div style={{ fontSize: "0.85rem" }}>
                                <div style={{ fontWeight: 700, marginBottom: "0.5rem" }}>Product Details</div>
                                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.5rem", marginBottom: "0.75rem" }}>
                                  <div><span style={{ color: "var(--text-muted)" }}>Brand:</span> {p.brand || "—"}</div>
                                  <div><span style={{ color: "var(--text-muted)" }}>Category:</span> {p.category || "—"}</div>
                                  <div><span style={{ color: "var(--text-muted)" }}>Best Price:</span> {p.lowest_price ? `₹${p.lowest_price.toLocaleString("en-IN")}` : "—"}</div>
                                </div>
                                {productOffers.length > 0 && (
                                  <div>
                                    <div style={{ fontWeight: 700, marginBottom: "0.4rem" }}>Offers ({productOffers.length})</div>
                                    <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                                      {productOffers.map((o, i) => (
                                        <div key={i} style={{ display: "flex", gap: "1rem", padding: "0.4rem 0.6rem", background: "var(--bg-card)", borderRadius: 6, fontSize: "0.82rem" }}>
                                          <span style={badgeStyle("purple")}>{o.store_name || o.platform_name || o.platform}</span>
                                          <span style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>₹{o.current_price || o.price}</span>
                                          {(o.original_price > 0 || o.mrp) && <span style={{ color: "var(--text-muted)", textDecoration: "line-through" }}>₹{o.original_price || o.mrp}</span>}
                                          {o.rating && <span>⭐ {o.rating}</span>}
                                          {o.in_stock === false && <span style={{ color: "var(--accent-rose)" }}>Out of Stock</span>}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    ))}
                    {products.length === 0 && (
                      <tr><td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>No products found.</td></tr>
                    )}
                  </tbody>
                </table>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1rem", fontSize: "0.85rem" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Showing {products.length} of {productsCount}</span>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <button disabled={productsPage <= 1} onClick={() => setProductsPage((p) => p - 1)} style={{ ...btnPrimary, opacity: productsPage <= 1 ? 0.4 : 1 }}>Prev</button>
                    <span style={{ padding: "0.4rem 0.8rem", color: "var(--text-secondary)" }}>Page {productsPage}</span>
                    <button disabled={products.length < 20} onClick={() => setProductsPage((p) => p + 1)} style={{ ...btnPrimary, opacity: products.length < 20 ? 0.4 : 1 }}>Next</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "users" && (
          <div>
            <h2 style={{ fontWeight: 800, fontSize: "1.4rem", marginBottom: "1rem" }}>User Management</h2>
            {usersLoading ? (
              <div style={{ color: "var(--text-secondary)", padding: "2rem", textAlign: "center" }}>Loading users...</div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={tableStyle}>
                  <thead>
                    <tr>
                      <th style={thStyle}>ID</th>
                      <th style={thStyle}>Username</th>
                      <th style={thStyle}>Email</th>
                      <th style={thStyle}>Status</th>
                      <th style={thStyle}>Joined</th>
                      <th style={thStyle}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id}>
                        <td style={tdStyle}>{u.id}</td>
                        <td style={{ ...tdStyle, fontWeight: 600 }}>{u.username}</td>
                        <td style={{ ...tdStyle, color: "var(--text-secondary)" }}>{u.email}</td>
                        <td style={tdStyle}>
                          {u.is_staff ? <span style={badgeStyle("cyan")}>Staff</span> : <span style={badgeStyle("rose")}>User</span>}
                        </td>
                        <td style={{ ...tdStyle, color: "var(--text-muted)", fontSize: "0.8rem" }}>
                          {new Date(u.date_joined).toLocaleDateString("en-IN")}
                        </td>
                        <td style={tdStyle}>
                          {user?.id !== u.id ? (
                            <div style={{ display: "flex", gap: "0.4rem" }}>
                              {!u.is_staff && (
                                <button onClick={() => handlePromote(u)} style={btnPrimary}>Promote</button>
                              )}
                              {u.is_staff && (
                                <button onClick={() => handleDemote(u)} style={btnDanger}>Demote</button>
                              )}
                            </div>
                          ) : (
                            <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>You</span>
                          )}
                        </td>
                      </tr>
                    ))}
                    {users.length === 0 && (
                      <tr><td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>No users found.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "analyses" && (
          <div>
            <h2 style={{ fontWeight: 800, fontSize: "1.4rem", marginBottom: "1rem" }}>Recent Analyses</h2>
            {analysesLoading ? (
              <div style={{ color: "var(--text-secondary)", padding: "2rem", textAlign: "center" }}>Loading analyses...</div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={tableStyle}>
                  <thead>
                    <tr>
                      <th style={thStyle}>ID</th>
                      <th style={thStyle}>URL</th>
                      <th style={thStyle}>Platform</th>
                      <th style={thStyle}>Product</th>
                      <th style={thStyle}>Analyzed At</th>
                      <th style={thStyle}>User</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyses.slice(0, 20).map((a) => (
                      <tr key={a.id}>
                        <td style={tdStyle}>{a.id}</td>
                        <td style={{ ...tdStyle, maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          <a href={a.url} target="_blank" rel="noreferrer" style={{ color: "var(--accent-cyan)" }}>{a.url}</a>
                        </td>
                        <td style={tdStyle}>
                          <span style={badgeStyle("purple")}>{a.platform_name || a.platform || "—"}</span>
                        </td>
                        <td style={{ ...tdStyle, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {a.product_title || a.product || "—"}
                        </td>
                        <td style={{ ...tdStyle, color: "var(--text-muted)", fontSize: "0.8rem" }}>
                          {a.analyzed_at ? new Date(a.analyzed_at).toLocaleString("en-IN") : "—"}
                        </td>
                        <td style={{ ...tdStyle, color: "var(--text-secondary)" }}>
                          {a.user_name || a.user || "—"}
                        </td>
                      </tr>
                    ))}
                    {analyses.length === 0 && (
                      <tr><td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>No analyses found.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "offers" && (
          <div>
            <h2 style={{ fontWeight: 800, fontSize: "1.4rem", marginBottom: "1rem" }}>Offers</h2>
            <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", alignItems: "center" }}>
              <select value={offersPlatform} onChange={(e) => setOffersPlatform(e.target.value)} style={{ ...inputStyle, padding: "0.55rem" }}>
                <option value="">All Platforms</option>
                {platforms.map((pl) => (
                  <option key={pl.id} value={pl.id}>{pl.name}</option>
                ))}
              </select>
              <select value={offersSort} onChange={(e) => setOffersSort(e.target.value)} style={{ ...inputStyle, padding: "0.55rem" }}>
                <option value="">Default Sort</option>
                <option value="price">Price (Low to High)</option>
                <option value="-price">Price (High to Low)</option>
                <option value="-rating">Rating (High to Low)</option>
                <option value="rating">Rating (Low to High)</option>
              </select>
            </div>
            {offersLoading ? (
              <div style={{ color: "var(--text-secondary)", padding: "2rem", textAlign: "center" }}>Loading offers...</div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={tableStyle}>
                  <thead>
                    <tr>
                      <th style={thStyle}>ID</th>
                      <th style={thStyle}>Product</th>
                      <th style={thStyle}>Platform</th>
                      <th style={thStyle}>Price</th>
                      <th style={thStyle}>MRP</th>
                      <th style={thStyle}>Rating</th>
                      <th style={thStyle}>In Stock</th>
                    </tr>
                  </thead>
                  <tbody>
                    {offers.map((o) => (
                      <tr key={o.id}>
                        <td style={tdStyle}>{o.id}</td>
                        <td style={{ ...tdStyle, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {o.product_title || o.product || "—"}
                        </td>
                        <td style={tdStyle}>
                          <span style={badgeStyle("purple")}>{o.store_name || o.platform_name || o.platform || "—"}</span>
                        </td>
                        <td style={{ ...tdStyle, fontWeight: 700, color: "var(--accent-cyan)" }}>₹{o.current_price || o.price}</td>
                        <td style={{ ...tdStyle, color: "var(--text-muted)", textDecoration: "line-through" }}>
                          {o.original_price > 0 ? `₹${o.original_price}` : o.mrp ? `₹${o.mrp}` : "—"}
                        </td>
                        <td style={tdStyle}>
                          {o.rating ? `⭐ ${o.rating}` : "—"}
                        </td>
                        <td style={tdStyle}>
                          {o.in_stock === false ? (
                            <span style={{ color: "var(--accent-rose)", fontWeight: 600, fontSize: "0.8rem" }}>No</span>
                          ) : (
                            <span style={{ color: "#22c55e", fontWeight: 600, fontSize: "0.8rem" }}>Yes</span>
                          )}
                        </td>
                      </tr>
                    ))}
                    {offers.length === 0 && (
                      <tr><td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: "var(--text-muted)", padding: "2rem" }}>No offers found.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Admin;
