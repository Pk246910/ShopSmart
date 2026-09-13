import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import API from "../api/axios";
import { Eye, EyeOff } from "lucide-react";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", new_password: "", confirm_password: "" });
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.new_password.length < 8) { toast.error("New password must be at least 8 chars"); return; }
    if (form.new_password !== form.confirm_password) { toast.error("Passwords do not match"); return; }
    setLoading(true);
    try {
      const res = await API.post("/users/forgot-password/", {
        username: form.username,
        email: form.email,
        new_password: form.new_password,
        confirm_password: form.confirm_password,
      });
      toast.success(res.data.detail || "Password reset successfully");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      const d = err.response?.data;
      let m = "Reset failed";
      if (d) {
        if (d.detail) m = d.detail;
        else {
          const parts = [];
          for (const [k, v] of Object.entries(d)) parts.push(`${k}: ${Array.isArray(v) ? v.join(", ") : v}`);
          m = parts.join(" | ");
        }
      }
      toast.error(m);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 480, margin: "2rem auto", background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: 16 }}>
      <h2 style={{ fontWeight: 800 }}>Forgot Password</h2>
      <p style={{ color: "var(--text-secondary)", margin: "0.5rem 0 1.5rem" }}>Verify username + email, then set new password (min 8 chars). No email needed for demo.</p>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required style={{ padding: "0.75rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" }} />
        <input type="email" placeholder="Registered Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required style={{ padding: "0.75rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" }} />
        <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
          <input type={showNew ? "text" : "password"} placeholder="New Password (min 8)" value={form.new_password} onChange={(e) => setForm({ ...form, new_password: e.target.value })} required minLength={8} style={{ padding: "0.75rem", paddingRight: "2.5rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)", width: "100%" }} />
          <button type="button" onClick={() => setShowNew((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }}>{showNew ? <EyeOff size={18} /> : <Eye size={18} />}</button>
        </div>
        <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
          <input type={showConfirm ? "text" : "password"} placeholder="Confirm New Password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} required minLength={8} style={{ padding: "0.75rem", paddingRight: "2.5rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)", width: "100%" }} />
          <button type="button" onClick={() => setShowConfirm((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }}>{showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}</button>
        </div>
        <button type="submit" disabled={loading} style={{ background: "var(--accent-cyan)", color: "#fff", padding: "0.8rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer", opacity: loading ? 0.6 : 1 }}>{loading ? "Resetting..." : "Reset Password"}</button>
      </form>
      <p style={{ marginTop: "1rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>Remembered? <Link to="/login" style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>Login</Link></p>
    </div>
  );
};

export default ForgotPassword;
