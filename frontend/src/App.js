import { useState, useEffect, useRef } from "react";
import "./App.css";
import ResortCard from "./ResortCard";
import LeafletMap from "./LeafletMap";
import { statusColors, statusLabels } from "./utils";

// ── Filters:  loops through
function Filters({ resorts, filter, onChange }) {
  const regions = ["All", ...new Set(resorts.map(r => r.region))];
  return (
    <div className="filters">
      <select 
        className="filter-select" 
        value={filter.region}
        onChange={e => onChange({ ...filter, region: e.target.value })}
      >
        <option value="" disabled>Prefecture</option>
        {regions.map(r => 
          <option 
          key={r}> {r}
          </option>)}
      </select>
      <input className="filter-input" placeholder="Search resort…"
        value={filter.query}
        onChange={e => onChange({ ...filter, query: e.target.value })} />
    </div>
  );
}

// ── App
export default function SkiJapan() {
  const [resorts, setResorts] = useState([]);

  useEffect(() => {
    fetch("/resort_data.json")
      .then(res => res.json())
      .then(data => setResorts(data));
  }, []);

  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState({ region: "All", query: "" });

  const filtered = resorts.filter(r => {
    if (filter.region !== "All" && r.region !== filter.region) return false;
    if (filter.query) {
      const q = filter.query.toLowerCase();
      if (!r.name.toLowerCase().startsWith(q) && !r.region.toLowerCase().startsWith(q)) return false;
    }
    return true;
  });

  const sorted = [...filtered].sort((a, b) => (b.snow_depth_cm ?? 0) - (a.snow_depth_cm ?? 0));
  
  const selectedCardRef = useRef(null);

  useEffect(() => {
    if (selectedCardRef.current) {
      selectedCardRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [selected]);

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
            <div className="header-stat-value">{resorts.length}</div>
          </div>
          <div className="header-stat">
          </div>
          <button className="btn-refresh">↻ Refresh</button>
        </div>
      </header>

      <main className="main">

        <div className="map-panel">
          <LeafletMap resorts={filtered} selected={selected} onSelect={setSelected} />

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
              <div className="detail-region">{selected.prefecture} · {selected.region}</div>
              <div className="detail-meta">
                🌡 {selected.temp_celsius}°C · {selected.live_weather}<br />
                {selected.snow_depth_cm != null
                  ? `❄ ${selected.snow_depth_cm}cm snow depth`
                  : "Snow depth unavailable"}
              </div>
              {selected.lift_status && (
                <div className="detail-meta" style={{ marginTop: 6 }}>
                  {selected.lift_status.map(l => (
                    <div key={l.name}>{l.name}: {l.status}</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="list-panel">
          <div className="list-header">
            <div className="list-meta-row">
              <span className="list-count">{filtered.length} destinations</span>
              <span className="list-sort">sorted by snow depth ↓</span>
            </div>
            <Filters resorts={resorts} filter={filter} onChange={setFilter} />
          </div>

          <div className="list-scroll">
            {sorted.length === 0 ? (
              <div className="empty-state">No resorts match your filters</div>
            ) : (
              sorted.map(r => (
                <ResortCard     
                  key={r.name}
                  resort={r}
                  selected={selected?.name === r.name}
                  onClick={setSelected}
                  cardRef={selected?.name === r.name ? selectedCardRef : null} />
              ))
            )}
          </div>
        </div>

      </main>
    </div>
  );
}