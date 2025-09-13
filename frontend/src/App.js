import React, { useEffect, useState, useRef } from "react";

const HOUSES = [
  { name: "Gryff", icon: "🦁" },
  { name: "Slyth", icon: "🐍" },
  { name: "Raven", icon: "🦅" },
  { name: "Huff", icon: "🦡" },
];

const API_BASE = "http://localhost:5000";

function formatNum(n) {
  return n.toLocaleString();
}

export default function App() {
  const [windowSel, setWindowSel] = useState("all");
  const [totals, setTotals] = useState({ Gryff: 0, Slyth: 0, Raven: 0, Huff: 0 });
  const [live, setLive] = useState(false);
  const esRef = useRef(null);

  async function fetchTotals(win) {
    try {
      const r = await fetch(`${API_BASE}/api/totals?window=${win}`);
      const j = await r.json();
      setTotals(j.totals);
    } catch (err) {
      console.error("Error fetching totals:", err);
    }
  }

  useEffect(() => { fetchTotals(windowSel); }, [windowSel]);

  useEffect(() => {
    if (!live) {
      if (esRef.current) { esRef.current.close(); esRef.current = null; }
      return;
    }
    const es = new EventSource(`${API_BASE}/stream`);
    es.onmessage = () => { fetchTotals(windowSel); };
    es.onerror = () => { es.close(); esRef.current = null; };
    esRef.current = es;
    return () => { es.close(); esRef.current = null; };
  }, [live, windowSel]);

  const maxPoints = Math.max(...HOUSES.map(h => totals[h.name] || 0), 1);

  return (
    <div style={{ maxWidth: 700, margin: "20px auto", fontFamily: "Arial, sans-serif" }}>
      <h3 style={{ textAlign: "center" }}>📊 Live Leaderboard</h3>
      <div style={{ display: "flex", justifyContent: "center", gap: 12, marginBottom: 16 }}>
        <button onClick={() => setLive(!live)}>
          {live ? "⏸ Stop Updates" : "▶ Start Updates"}
        </button>
        <select value={windowSel} onChange={(e) => setWindowSel(e.target.value)}>
          <option value="5m">Last 5 minutes</option>
          <option value="1h">Last 1 hour</option>
          <option value="all">All Time</option>
        </select>
      </div>

      <div style={{ padding: 16, border: "1px solid #ddd", borderRadius: 8, background: "#fff" }}>
        {HOUSES.map(h => {
          const points = totals[h.name] || 0;
          const pct = Math.round((points / maxPoints) * 100);
          return (
            <div key={h.name} style={{ display: "flex", alignItems: "center", marginBottom: 20 }}>
              {/* Icon with tooltip */}
              <div
                style={{ width: 80, display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }}
                title={`${h.name}: ${formatNum(points)}`}
              >
                <span style={{ fontSize: "1.2em" }}>{h.icon}</span>
                <span>{h.name}</span>
              </div>

              {/* Progress bar */}
              <div style={{
                flex: 1,
                background: "#f2f4f7",
                height: 32,
                borderRadius: 6,
                overflow: "hidden",
                marginRight: 12,
              }}>
                <div style={{
                  height: "100%",
                  width: `${pct}%`,
                  background: "#223fcd",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  paddingLeft: 8,
                  fontWeight: "bold",
                  transition: "width 0.5s ease"
                }}>
                  {formatNum(points)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
