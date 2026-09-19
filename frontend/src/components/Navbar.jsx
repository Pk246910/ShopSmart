import React, { useEffect, useState, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";
import API from "../api/axios";

const isActive = (pathname, path) => {
  if (path === "/") return pathname === "/";
  return pathname.startsWith(path);
};

const Navbar = () => {
  const { darkMode, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const location = useLocation();
  const [wishlistCount, setWishlistCount] = useState(0);
  const [alertCount, setAlertCount] = useState(0);
  const [mobileOpen, setMobileOpen] = useState(false);

  const fetchCount = useCallback(async () => {
    try {
      // No guest_id param: WishlistViewSet is auth-only and identifies
      // the user from the JWT. (guest_id remains in use elsewhere:
      // X-Guest-ID header for analyses/recent.)
      const res = await API.get("/wishlist/");
      const data = res.data;
      const list = data.results !== undefined ? data.results : data;
      setWishlistCount(Array.isArray(list) ? list.length : 0);
    } catch {
      setWishlistCount(0);
    }
  }, []);

  const fetchAlertCount = useCallback(async () => {
    if (!user) { setAlertCount(0); return; }
    try {
      const res = await API.get("/users/alerts/");
      const list = Array.isArray(res.data) ? res.data : res.data.results || [];
      setAlertCount(list.length);
    } catch {
      setAlertCount(0);
    }
  }, [user]);

  useEffect(() => {
    fetchCount();
    fetchAlertCount();
    const h = () => { fetchCount(); fetchAlertCount(); };
    window.addEventListener("wishlist:changed", h);
    window.addEventListener("alert:changed", h);
    return () => {
      window.removeEventListener("wishlist:changed", h);
      window.removeEventListener("alert:changed", h);
    };
  }, [fetchCount, fetchAlertCount]);

  useEffect(() => {
    fetchCount();
    fetchAlertCount();
  }, [location.pathname, fetchCount, fetchAlertCount]);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        <span>⚡</span> ShopSmart
      </Link>

      <button
        className="navbar-hamburger"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle menu"
        aria-expanded={mobileOpen}
        aria-controls="mobile-nav"
      >
        {mobileOpen ? <X size={22} /> : <Menu size={22} />}
      </button>

      {mobileOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <nav
        id="mobile-nav"
        className={`nav-links-group ${mobileOpen ? "mobile-open" : ""}`}
        role={mobileOpen ? "dialog" : undefined}
        aria-modal={mobileOpen ? "true" : undefined}
      >
        <Link to="/" className={`nav-item ${isActive(location.pathname, "/") ? "active" : ""}`}>
          Analyze
        </Link>
        <Link to="/recent" className={`nav-item ${isActive(location.pathname, "/recent") ? "active" : ""}`}>
          Recent
        </Link>
        <Link to="/wishlist" className={`nav-item ${isActive(location.pathname, "/wishlist") ? "active" : ""}`}>
          Wishlist {wishlistCount > 0 && <span style={{ background: "var(--accent-rose)", color: "#fff", fontSize: "0.7rem", padding: "0.15rem 0.45rem", borderRadius: 999, marginLeft: "0.25rem" }}>{wishlistCount}</span>}
        </Link>
        <Link to="/alerts" className={`nav-item ${isActive(location.pathname, "/alerts") ? "active" : ""}`}>
          Price Alerts {alertCount > 0 && <span style={{ background: "var(--accent-amber)", color: "#fff", fontSize: "0.7rem", padding: "0.15rem 0.45rem", borderRadius: 999, marginLeft: "0.25rem" }}>{alertCount}</span>}
        </Link>
        {user ? (
          <>
            <Link to="/profile" className={`nav-item ${isActive(location.pathname, "/profile") ? "active" : ""}`}>Profile</Link>
            {(user.is_staff || user.is_superuser) && <Link to="/admin" className={`nav-item ${isActive(location.pathname, "/admin") ? "active" : ""}`}>Admin</Link>}
            <span className="nav-item-username">Hi, {user.username}</span>
            <button onClick={logout} className="nav-btn-logout">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className={`nav-item ${isActive(location.pathname, "/login") ? "active" : ""}`}>
              Login
            </Link>
            <Link to="/register" className="nav-btn-register">
              Register
            </Link>
          </>
        )}
        <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle Theme">
          {darkMode ? "☀️ Light" : "🌙 Dark"}
        </button>
      </nav>
    </header>
  );
};

export default Navbar;
