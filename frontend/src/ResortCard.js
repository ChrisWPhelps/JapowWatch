import { statusColors, statusLabels } from "./utils";

function SnowBar({ depth }) {
  const pct = Math.min(((depth ?? 0) / 350) * 100, 100);
  return (
    <div className="snow-bar-row">
      <div className="snow-track">
        <div className="snow-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="snow-label">
        {depth ?? "—"}cm
      </span>
    </div>
  );
}

export default function ResortCard({ resort, selected, onClick, cardRef }) {
  const sc = statusColors[resort.status] ?? "#6a7aa8";
  return (
    <div
      ref={cardRef}
      className={`resort-card${selected ? " selected" : ""}`}
      onClick={() => onClick(resort)}
    >
      {/* Name + region + status */}
      <div className="card-top">
        <div>
          <div className="card-name">{resort.name}</div>
          <div className="card-location">{resort.region} · {resort.prefecture}</div>
        </div>
        <div
          className="status-pill"
          style={{
            background: `${sc}16`,
            border: `1px solid ${sc}44`,
            color: sc,
          }}
        >
          {resort.timestamp ? new Date(resort.timestamp).toLocaleString() : "Unknown"}
        </div>
      </div>

      <SnowBar depth={resort.snow_depth_cm} />

      {/* Stats */}
      <div className="card-stats">
        <div className="stat-box">
          <div className="stat-label">Temp (C°)</div>
          <div className="stat-value">
            {resort.temp_celsius != null ? `${resort.temp_celsius}` : "—"}
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Snow (cm)</div>
          <div className="stat-value">
            {resort.snow_depth_cm != null ? `${resort.snow_depth_cm}` : "—"}
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Lifts</div>
          <div className="stat-value">
            {resort.lift_status != null ? resort.lift_status.length : "—"}
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Weather</div>
          <div className="stat-value">
            {resort.live_weather ?? "—"}
          </div>
        </div>
      </div>

    </div>
  );
}