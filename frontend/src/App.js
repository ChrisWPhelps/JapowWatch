import { useState } from "react";
import "./App.css";

const RESORT_DATA = [
  {
    id: "11", name: "Niseko AAAAAAAAAA",
    region: "Hokkaido", prefecture: "Hokkaido",
    timestamp: "2026-03-16 07:16:17",
    elevation_top: 1382, elevation_base: 900, vertical: 482, // func
    lifts: { total: 12, gondolas: 0, chairs: 10, surface: 2, waitTime: 4 },
    snowDepth: 190, freshSnow48h: 20,
    status: "partial",
    price: { dayPass: 4500, halfDay: 3400, season: 68000 }, // func
        lift_status: [
            {
                "name": "Gondola",
                "status": "Open"
            },
            {
                "name": "Jumbo Pair",
                "status": "Closed"
            },
    ],
    lat: 36.98, lng: 138.35,
  },
];

// ── Japan map bounding box: lng 129→146, lat 31→45
const MAP_LNG_MIN = 129, MAP_LNG_MAX = 146;
const MAP_LAT_MIN = 31,  MAP_LAT_MAX = 45.5;

const statusColors = { open: "#e8c96a", partial: "#e8906a", closed: "#6a7aa8" };
const statusLabels = { open: "Open", partial: "Partial", closed: "Closed" };
const runColors    = { green: "#5fb87a", blue: "#5c8fe8", black: "#c8c8d8" };

function fmt(n) { return n.toLocaleString("en"); }
function fmtJPY(n) { return `¥${fmt(n)}`; }

// ── Snow bar
function SnowBar({ depth, fresh }) {
  const pct = Math.min((depth / 350) * 100, 100);
  return (
    <div className="snow-bar-row">
      <div className="snow-track">
        <div className="snow-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="snow-label">
        {depth}cm {fresh > 0 && <span style={{ color: "#a8d8f0", fontSize: 8 }}>+{fresh}cm</span>}
      </span>
    </div>
  );
}

// ── Resort card
function ResortCard({ resort, selected, onClick }) {
  const sc = statusColors[resort.status];
  return (
    <div className={`resort-card${selected ? " selected" : ""}`} onClick={() => onClick(resort)}>
      <div className="card-top">
        <div>
          <div className="card-name">{resort.name}</div>
          <div className="card-location">{resort.nameJa} · {resort.region}</div>
        </div>
        <div
          className="status-pill"
          style={{
            background: `${sc}16`,
            border: `1px solid ${sc}44`,
            color: sc,
          }}
        >
          {statusLabels[resort.status]}
        </div>
      </div>

      <SnowBar depth={resort.snowDepth} fresh={resort.freshSnow48h} />

      <div className="card-stats">
        <div className="stat-box">
          <div className="stat-label">Top</div>
          <div className="stat-value">{fmt(resort.elevation_top)}m</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Vertical</div>
          <div className="stat-value">{fmt(resort.vertical)}m</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Lifts</div>
          <div className="stat-value">{resort.lifts.total}</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Wait</div>
          <div className="stat-value">
            {resort.lifts.waitTime !== null ? `${resort.lifts.waitTime}m` : "—"}
          </div>
        </div>
      </div>

      <div className="card-bottom">
        <div style={{ textAlign: "right" }}>
          <div className="card-price">{fmtJPY(resort.price.dayPass)}</div>
          <div className="card-price-sub">day pass</div>
        </div>
      </div>
    </div>
  );
}

// Map panel
function MapPanel({ resorts, selected, onSelect }) {
  const W = 540, H = 480;

  const toX = (lng) => ((lng - MAP_LNG_MIN) / (MAP_LNG_MAX - MAP_LNG_MIN)) * W;
  const toY = (lat) => ((MAP_LAT_MAX - lat) / (MAP_LAT_MAX - MAP_LAT_MIN)) * H;

  return (
    <div className="map-panel">
      <div className="map-bg" />

      {/* Grain */}
      <svg className="map-grain" width="100%" height="100%">
        <filter id="noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.82" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#noise)" />
      </svg>

      {/* Japan outline */}
      <svg className="map-svg" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet">
        {/* Subtle grid */}
        {Array.from({ length: 10 }).map((_, i) => (
          <line key={`v${i}`} x1={(i / 9) * W} y1={0} x2={(i / 9) * W} y2={H}
            stroke="#4a7ab5" strokeWidth="0.4" opacity="0.07" />
        ))}
        {Array.from({ length: 9 }).map((_, i) => (
          <line key={`h${i}`} x1={0} y1={(i / 8) * H} x2={W} y2={(i / 8) * H}
            stroke="#4a7ab5" strokeWidth="0.4" opacity="0.07" />
        ))}

        {/* Region label: Hokkaido */}
        <text x={toX(141.5)} y={toY(43.5)} fill="rgba(240,232,216,0.1)"
          fontSize="11" fontFamily="'Shippori Mincho',serif" letterSpacing="3">
          HOKKAIDO
        </text>
        <text x={toX(137.5)} y={toY(36.2)} fill="rgba(240,232,216,0.08)"
          fontSize="10" fontFamily="'Shippori Mincho',serif" letterSpacing="3">
          HONSHU
        </text>

        {/* Pins */}
        {resorts.map(r => {
          const x = toX(r.lng);
          const y = toY(r.lat);
          const isSel = selected?.id === r.id;
          const col = statusColors[r.status];
          return (
            <g key={r.id} style={{ cursor: "pointer" }} onClick={() => onSelect(r)}>
              {isSel && (
                <>
                  <circle cx={x} cy={y} r={20} fill={col} opacity={0}>
                    <animate attributeName="r" values="10;22;10" dur="2.2s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0.2;0;0.2" dur="2.2s" repeatCount="indefinite" />
                  </circle>
                  <circle cx={x} cy={y} r={10} fill={col} opacity={0.14} />
                </>
              )}
              <circle cx={x} cy={y} r={isSel ? 7 : 5} fill={col} opacity={isSel ? 1 : 0.7} />
              <circle cx={x} cy={y} r={isSel ? 3.5 : 2.5} fill="#070e18" />
              {isSel && (
                <text x={x} y={y - 12} textAnchor="middle" fill={col} fontSize="9"
                  fontFamily="'Shippori Mincho',serif" letterSpacing="0.5">
                  {r.name}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      <div className="map-label">Japan · 日本</div>

      {/* Legend */}
      <div className="map-legend">
        {Object.entries(statusColors).map(([k, v]) => (
          <div key={k} className="legend-row">
            <div className="legend-dot" style={{ background: v }} />
            {statusLabels[k]}
          </div>
        ))}
      </div>

      {/* Selected detail card */}
      {selected && (
        <div className="map-detail-card">
          <div className="detail-name">{selected.name}</div>
          <div className="detail-region">{selected.nameJa} · {selected.region}</div>
          <div className="detail-meta">
            ↑ {fmt(selected.elevation_top)}m summit · ↕ {fmt(selected.vertical)}m vertical<br />
            {selected.lifts.gondolas}G / {selected.lifts.chairs}C / {selected.lifts.surface}S lifts
            {selected.lifts.waitTime !== null && ` · ~${selected.lifts.waitTime}min wait`}<br />
            Season {selected.season.opens} – {selected.season.closes}
          </div>
          <div className="detail-runs">
            {["green", "blue", "black"].map(d => (
              <div key={d} className="run-dot">
                <div
                  className={d === "black" ? "run-square" : "run-circle"}
                  style={{ background: runColors[d] }}
                />
                {selected.runs[d]}
              </div>
            ))}
            <div className="run-dot" style={{ marginLeft: "auto", color: "rgba(240,232,216,0.4)" }}>
              {selected.runs.total} total
            </div>
          </div>
          <div className="detail-price">
            <div>
              <div className="price-label">Day Pass</div>
              <div className="price-value">{fmtJPY(selected.price.dayPass)}</div>
            </div>
            {selected.price.halfDay && (
              <div style={{ textAlign: "center" }}>
                <div className="price-label">Half Day</div>
                <div className="price-value" style={{ fontSize: 12 }}>{fmtJPY(selected.price.halfDay)}</div>
              </div>
            )}
            {selected.price.season && (
              <div style={{ textAlign: "right" }}>
                <div className="price-label">Season</div>
                <div className="price-value" style={{ fontSize: 12 }}>{fmtJPY(selected.price.season)}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Filters
function Filters({ filter, onChange }) {
  const regions = ["All", ...new Set(RESORT_DATA.map(r => r.region))];
  return (
    <div className="filters">
      <select className="filter-select" value={filter.region}
        onChange={e => onChange({ ...filter, region: e.target.value })}>
        {regions.map(r => <option key={r}>{r}</option>)}
      </select>
      <select className="filter-select" value={filter.status}
        onChange={e => onChange({ ...filter, status: e.target.value })}>
        <option value="All">All Statuses</option>
        <option value="open">Open</option>
        <option value="partial">Partial</option>
        <option value="closed">Closed</option>
      </select>
      <input className="filter-input" placeholder="Search resort…"
        value={filter.query}
        onChange={e => onChange({ ...filter, query: e.target.value })} />
    </div>
  );
}

// ── App
export default function SkiJapan() {
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState({ region: "All", status: "All", query: "" });

  const filtered = RESORT_DATA.filter(r => {
    if (filter.region !== "All" && r.region !== filter.region) return false;
    if (filter.status !== "All" && r.status !== filter.status) return false;
    if (filter.query) {
      const q = filter.query.toLowerCase();
      if (!r.name.toLowerCase().includes(q) && !r.nameJa.includes(q) &&
          !r.region.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const sorted = [...filtered].sort((a, b) => b.snowDepth - a.snowDepth);

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <span className="logo">SkiPiea</span>
          <span className="logo-sub">Japan Ski Explorer</span>
        </div>
        <div className="header-right">
          <div className="header-stat">
            <div className="header-stat-label">Resorts tracked</div>
            <div className="header-stat-value">{RESORT_DATA.length}</div>
          </div>
          <div className="header-stat">
            <div className="header-stat-label">Currently open</div>
            <div className="header-stat-value" style={{ color: "#e8c96a" }}>
              {RESORT_DATA.filter(r => r.status === "open").length}
            </div>
          </div>
          <button className="btn-refresh">↻ Refresh</button>
        </div>
      </header>

      <main className="main">
        <MapPanel resorts={filtered} selected={selected} onSelect={setSelected} />

        <div className="list-panel">
          <div className="list-header">
            <div className="list-meta-row">
              <span className="list-count">{filtered.length} destinations</span>
              <span className="list-sort">sorted by snow depth ↓</span>
            </div>
            <Filters filter={filter} onChange={setFilter} />
          </div>

          <div className="list-scroll">
            {sorted.length === 0 ? (
              <div className="empty-state">No resorts match your filters</div>
            ) : (
              sorted.map(r => (
                <ResortCard key={r.id} resort={r}
                  selected={selected?.id === r.id}
                  onClick={setSelected} />
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}