import React from "react";

const shimmerStyle = {
  background: "linear-gradient(90deg, var(--bg-card) 25%, var(--border-color) 50%, var(--bg-card) 75%)",
  backgroundSize: "200% 100%",
  animation: "shimmer 1.5s infinite",
  borderRadius: 8,
};

export const SkeletonBox = ({ width = "100%", height = 20, style = {} }) => (
  <div style={{ ...shimmerStyle, width, height, ...style }} />
);

export const SkeletonText = ({ lines = 3, gap = "0.5rem" }) => (
  <div style={{ display: "flex", flexDirection: "column", gap }}>
    {Array.from({ length: lines }).map((_, i) => (
      <SkeletonBox
        key={i}
        height={14}
        width={i === lines - 1 ? "60%" : "100%"}
      />
    ))}
  </div>
);

export const SkeletonProductCard = () => (
  <div style={{
    background: "var(--bg-card)",
    border: "1px solid var(--border-color)",
    borderRadius: 18,
    padding: "1.25rem",
  }}>
    <SkeletonBox height={160} style={{ borderRadius: 12, marginBottom: "0.75rem" }} />
    <SkeletonBox height={12} width="40%" style={{ marginBottom: "0.5rem" }} />
    <SkeletonBox height={16} width="90%" style={{ marginBottom: "0.25rem" }} />
    <SkeletonBox height={16} width="70%" style={{ marginBottom: "0.75rem" }} />
    <SkeletonBox height={22} width="35%" />
  </div>
);

export const SkeletonTable = ({ rows = 5, cols = 5 }) => (
  <div style={{ overflowX: "auto" }}>
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          {Array.from({ length: cols }).map((_, i) => (
            <td key={i} style={{ padding: "0.75rem", borderBottom: "1px solid var(--border-color)" }}>
              <SkeletonBox height={14} width="80%" />
            </td>
          ))}
        </tr>
      </thead>
      <tbody>
        {Array.from({ length: rows }).map((_, r) => (
          <tr key={r}>
            {Array.from({ length: cols }).map((_, c) => (
              <td key={c} style={{ padding: "0.75rem", borderBottom: "1px solid var(--border-subtle)" }}>
                <SkeletonBox height={14} width={c === 0 ? "30%" : "70%"} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export const SkeletonChart = ({ height = 260 }) => (
  <div style={{ padding: "1rem" }}>
    <SkeletonBox height={height} style={{ borderRadius: 12 }} />
  </div>
);

export const SkeletonProductDetail = () => (
  <div style={{ display: "flex", gap: "2rem", padding: "2rem", alignItems: "flex-start" }}>
    <SkeletonBox width={200} height={200} style={{ borderRadius: 16, flexShrink: 0 }} />
    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "1rem" }}>
      <SkeletonBox height={14} width="30%" />
      <SkeletonBox height={28} width="90%" />
      <SkeletonBox height={14} width="40%" />
      <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
        <SkeletonBox height={40} width={140} style={{ borderRadius: 10 }} />
        <SkeletonBox height={40} width={100} style={{ borderRadius: 10 }} />
      </div>
    </div>
  </div>
);

export const SkeletonAnalysisPage = () => (
  <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1.5rem" }}>
    <SkeletonBox height={16} width={120} style={{ marginBottom: "1.5rem" }} />
    <SkeletonProductDetail />
    <div style={{ marginTop: "1.5rem" }}>
      <SkeletonBox height={80} style={{ borderRadius: 16 }} />
    </div>
    <div style={{ marginTop: "1.5rem" }}>
      <SkeletonBox height={200} style={{ borderRadius: 16 }} />
    </div>
    <div style={{ marginTop: "1.5rem" }}>
      <SkeletonTable rows={4} cols={8} />
    </div>
  </div>
);
