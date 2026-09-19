import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import API from "../api/axios";
import { Eye, EyeOff } from "lucide-react";

const inputStyle = { padding: "0.75rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" };

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [step, setStep] = useState(params.get("uid") && params.get("token") ? 2 : 1);
  const [form, setForm] = useState({
    username: "",
    email: "",
    uid: params.get("uid") || "",
    token: params.get("token") || "",
    new_password: "",
    confirm_password: "",
  });
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);

  const errText = (err, fallback) => {
    const d = err.response?.data;
    if (!d) return fallback;
    if (d.detail) return d.detail;
    const parts = [];
    for (const [k, v] of Object.entries(d)) parts.push(`${k}: ${Array.isArray(v) ? v.join(", ") : v}`);
    return parts.join(" | ") || fallback;
  };

  const handleRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await API.post("/users/forgot-password/", {
        username: form.username,
        email: form.email,
      });
      toast.success(res.data.detail || "Reset link sent");
      setStep(2);
    } catch (err) {
      toast.error(errText(err, "Request failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    if (form.new_password.length < 8) { toast.error("New password must be at least 8 chars"); return; }
    if (form.new_password !== form.confirm_password) { toast.error("Passwords do not match"); return; }
    setLoading(true);
    try {
      const res = await API.post("/users/reset-password/", {
        uid: form.uid,
        token: form.token,
        new_password: form.new_password,
        confirm_password: form.confirm_password,
      });
      toast.success(res.data.detail || "Password reset successfully");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      toast.error(errText(err, "Reset failed — link may be invalid or expired"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 480, margin: "2rem auto", background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: 16 }}>
      <h2 style={{ fontWeight: 800 }}>Forgot Password</h2>
      {step === 1 ? (
        <>
          <p style={{ color: "var(--text-secondary)", margin: "0.5rem 0 1.5rem" }}>Enter your username + email. If an account matches, a reset link will be emailed to you.</p>
          <form onSubmit={handleRequest} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required style={inputStyle} />
            <input type="email" placeholder="Registered Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required style={inputStyle} />
            <button type="submit" disabled={loading} style={{ background: "var(--accent-cyan)", color: "#fff", padding: "0.8rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer", opacity: loading ? 0.6 : 1 }}>{loading ? "Sending..." : "Send Reset Link"}</button>
          </form>
        </>
      ) : (
        <>
          <p style={{ color: "var(--text-secondary)", margin: "0.5rem 0 1.5rem" }}>Paste the reset link details from your email, then set a new password (min 8 chars).</p>
          <form onSubmit={handleConfirm} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <input placeholder="Reset ID (uid)" value={form.uid} onChange={(e) => setForm({ ...form, uid: e.target.value })} required style={inputStyle} />
            <input placeholder="Reset token" value={form.token} onChange={(e) => setForm({ ...form, token: e.target.value })} required style={inputStyle} />
            <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
              <input type={showNew ? "text" : "password"} placeholder="New Password (min 8)" value={form.new_password} onChange={(e) => setForm({ ...form, new_password: e.target.value })} required minLength={8} style={{ ...inputStyle, paddingRight: "2.5rem", width: "100%" }} />
              <button type="button" onClick={() => setShowNew((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }} aria-label={showNew ? "Hide password" : "View password"}>{showNew ? <EyeOff size={18} /> : <Eye size={18} />}</button>
            </div>
            <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
              <input type={showConfirm ? "text" : "password"} placeholder="Confirm New Password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} required minLength={8} style={{ ...inputStyle, paddingRight: "2.5rem", width: "100%" }} />
              <button type="button" onClick={() => setShowConfirm((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }} aria-label={showConfirm ? "Hide password" : "View password"}>{showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}</button>
            </div>
            <button type="submit" disabled={loading} style={{ background: "var(--accent-cyan)", color: "#fff", padding: "0.8rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer", opacity: loading ? 0.6 : 1 }}>{loading ? "Resetting..." : "Reset Password"}</button>
          </form>
        </>
      )}
      <p style={{ marginTop: "1rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>Remembered? <Link to="/login" style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>Login</Link></p>
    </div>
  );
};

export default ForgotPassword;
