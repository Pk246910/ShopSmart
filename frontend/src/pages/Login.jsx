import React, { useState, useMemo } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import { Eye, EyeOff } from "lucide-react";

const PasswordStrength = ({ password }) => {
  const checks = useMemo(() => {
    return [
      { label: "8+ characters", met: password.length >= 8 },
      { label: "Uppercase letter", met: /[A-Z]/.test(password) },
      { label: "Lowercase letter", met: /[a-z]/.test(password) },
      { label: "Number", met: /[0-9]/.test(password) },
      { label: "Special character", met: /[^A-Za-z0-9]/.test(password) },
    ];
  }, [password]);

  if (!password) return null;

  return (
    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
      {checks.map((c, i) => (
        <span
          key={i}
          style={{
            fontSize: "0.7rem",
            fontWeight: 600,
            padding: "0.2rem 0.5rem",
            borderRadius: 999,
            background: c.met ? "rgba(16,185,129,0.12)" : "rgba(244,63,94,0.08)",
            color: c.met ? "var(--accent-green)" : "var(--text-muted)",
            border: `1px solid ${c.met ? "rgba(16,185,129,0.3)" : "var(--border-color)"}`,
            display: "flex",
            alignItems: "center",
            gap: "0.25rem",
          }}
        >
          {c.met ? "✓" : "✗"} {c.label}
        </span>
      ))}
    </div>
  );
};

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || "/";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (err) {
      const data = err.response?.data;
      const msg = data?.detail || data?.username?.[0] || data?.password?.[0] || JSON.stringify(data) || "Login failed — check username/password";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 440, margin: "2rem auto", background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: 16, boxShadow: "var(--shadow-card)" }}>
      <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ fontWeight: 800, fontSize: "1.5rem", marginBottom: "0.25rem" }}>Welcome Back</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>Sign in to track prices and get deal alerts</p>
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <label style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.3rem", display: "block" }}>Username</label>
          <input placeholder="Enter your username" value={username} onChange={(e) => setUsername(e.target.value)} required style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "0.75rem", borderRadius: 10, color: "var(--text-primary)", width: "100%", fontSize: "0.95rem", transition: "border-color 0.2s" }} onFocus={(e) => e.target.style.borderColor = "var(--accent-cyan)"} onBlur={(e) => e.target.style.borderColor = "var(--border-color)"} />
        </div>
        <div>
          <label style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "0.3rem", display: "block" }}>Password</label>
          <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "0.75rem", paddingRight: "2.5rem", borderRadius: 10, width: "100%", color: "var(--text-primary)", fontSize: "0.95rem", transition: "border-color 0.2s" }}
              onFocus={(e) => e.target.style.borderColor = "var(--accent-cyan)"}
              onBlur={(e) => e.target.style.borderColor = "var(--border-color)"}
            />
            <button type="button" onClick={() => setShowPassword((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex", alignItems: "center" }} aria-label={showPassword ? "Hide password" : "View password"}>
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          <PasswordStrength password={password} />
        </div>
        <div style={{ textAlign: "right" }}>
          <Link to="/forgot-password" style={{ color: "var(--accent-cyan)", fontSize: "0.82rem", fontWeight: 600 }}>Forgot password?</Link>
        </div>
        <button type="submit" disabled={loading} style={{ background: "var(--gradient-brand)", color: "#fff", padding: "0.8rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer", opacity: loading ? 0.6 : 1, transition: "all 0.2s ease", fontSize: "0.95rem" }}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <div style={{ marginTop: "1.25rem", textAlign: "center", fontSize: "0.88rem", color: "var(--text-secondary)" }}>
        No account? <Link to="/register" style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>Register</Link>
      </div>
    </div>
  );
};

export default Login;
