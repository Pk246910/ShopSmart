import React, { useEffect, useState } from "react";
import API from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import toast from "react-hot-toast";

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ username: "", email: "", first_name: "", last_name: "" });
  const [pwd, setPwd] = useState({ old_password: "", new_password: "" });
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    API.get("/users/me/")
      .then((res) => {
        setProfile(res.data);
        setForm({ username: res.data.username || "", email: res.data.email || "", first_name: res.data.first_name || "", last_name: res.data.last_name || "" });
      })
      .catch(() => toast.error("Failed to load profile"))
      .finally(() => setLoading(false));
  }, [user]);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await API.patch("/users/me/", form);
      setProfile(res.data);
      toast.success("Profile updated ✓");
      // update local storage
      localStorage.setItem("shopsmart_user", JSON.stringify(res.data));
    } catch (err) {
      const data = err.response?.data;
      toast.error(data ? JSON.stringify(data) : "Update failed");
    }
  };

  const handlePassword = async (e) => {
    e.preventDefault();
    if (pwd.new_password.length < 8) { toast.error("New password must be at least 8 chars"); return; }
    try {
      await API.post("/users/change-password/", pwd);
      toast.success("Password changed ✓ Please login again");
      setPwd({ old_password: "", new_password: "" });
    } catch (err) {
      const d = err.response?.data;
      let m = "Password change failed";
      if (d) {
        if (d.old_password) m = `Old password: ${Array.isArray(d.old_password) ? d.old_password.join(", ") : d.old_password}`;
        else if (d.new_password) m = `New password: ${Array.isArray(d.new_password) ? d.new_password.join(", ") : d.new_password}`;
        else if (d.detail) m = d.detail;
        else m = JSON.stringify(d);
      }
      toast.error(m);
    }
  };

  if (loading) return <div style={{ padding: "3rem", textAlign: "center", color: "var(--text-secondary)" }}>Loading profile...</div>;
  if (!profile) return null;

  return (
    <div className="app-wrapper" style={{ maxWidth: 800, margin: "0 auto", padding: "2rem 1.5rem 3rem" }}>
      <h2 style={{ fontWeight: 800, marginBottom: "0.5rem" }}>👤 Account — Profile & Settings</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>Manage your ShopSmart account. Data stored in PostgreSQL `auth_user`.</p>

      <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: 16, padding: "1.5rem", marginBottom: "1.5rem" }}>
        <h3 style={{ fontWeight: 700, marginBottom: "1rem" }}>Profile Details</h3>
        <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "1rem" }}>ID: {profile.id} • Joined: {new Date(profile.date_joined).toLocaleDateString("en-IN")} • Staff: {profile.is_staff ? "Yes" : "No"} • Superuser: {profile.is_superuser ? "Yes" : "No"}</div>
        <form onSubmit={handleUpdate} style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
          <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Username" required style={{ padding: "0.7rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" }} />
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" required style={{ padding: "0.7rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" }} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.9rem" }}>
            <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} placeholder="First Name" style={{ padding: "0.7rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" }} />
            <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} placeholder="Last Name" style={{ padding: "0.7rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)" }} />
          </div>
          <button type="submit" style={{ background: "var(--accent-cyan)", color: "#fff", padding: "0.8rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer" }}>Save Changes</button>
        </form>
      </div>

      <div style={{ background: "var(--bg-secondary)", border: "1px solid var(--border-color)", borderRadius: 16, padding: "1.5rem", marginBottom: "1.5rem" }}>
        <h3 style={{ fontWeight: 700, marginBottom: "1rem" }}>Change Password (min 8 chars)</h3>
        <form onSubmit={handlePassword} style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
          <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
            <input type={showOld ? "text" : "password"} value={pwd.old_password} onChange={(e) => setPwd({ ...pwd, old_password: e.target.value })} placeholder="Old Password" required minLength={8} style={{ padding: "0.7rem", paddingRight: "2.5rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)", width: "100%" }} />
            <button type="button" onClick={() => setShowOld((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }}>{showOld ? <EyeOff size={18} /> : <Eye size={18} />}</button>
          </div>
          <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
            <input type={showNew ? "text" : "password"} value={pwd.new_password} onChange={(e) => setPwd({ ...pwd, new_password: e.target.value })} placeholder="New Password (min 8)" required minLength={8} style={{ padding: "0.7rem", paddingRight: "2.5rem", borderRadius: 10, border: "1px solid var(--border-color)", background: "var(--bg-card)", color: "var(--text-primary)", width: "100%" }} />
            <button type="button" onClick={() => setShowNew((v) => !v)} style={{ position: "absolute", right: "0.6rem", background: "transparent", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }}>{showNew ? <EyeOff size={18} /> : <Eye size={18} />}</button>
          </div>
          <button type="submit" style={{ background: "var(--bg-card)", border: "1px solid var(--border-color)", padding: "0.7rem", borderRadius: 10, fontWeight: 700, cursor: "pointer", color: "var(--text-primary)" }}>Update Password</button>
        </form>
      </div>

      <div style={{ display: "flex", gap: "0.75rem" }}>
        <button onClick={logout} style={{ background: "var(--accent-rose)", color: "#fff", padding: "0.6rem 1.2rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer" }}>Logout</button>
        {profile.is_staff && <button onClick={() => navigate("/admin")} style={{ background: "var(--accent-amber)", color: "#fff", padding: "0.6rem 1.2rem", border: "none", borderRadius: 10, fontWeight: 700, cursor: "pointer" }}>Go to Admin Module →</button>}
      </div>
    </div>
  );
};

export default Profile;
