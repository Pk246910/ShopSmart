import React, { useMemo } from "react";

// Shared password-strength indicator (used by Login and Register).
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

export default PasswordStrength;
