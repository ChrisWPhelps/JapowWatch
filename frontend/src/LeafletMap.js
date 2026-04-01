import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const MARKER_COLOR = "#0b9f27";

export default function LeafletMap({ resorts, selected, onSelect }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    if (mapRef.current) return;

    mapRef.current = L.map(containerRef.current, {
      center: [37.5, 137.5],
      zoom: 6,
      zoomControl: true,
      attributionControl: false,
    });

    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      { subdomains: "abcd", maxZoom: 14 }
    ).addTo(mapRef.current);

    return () => {
      mapRef.current.remove();
      mapRef.current = null;
    };
  }, []);

  // Selected resort gets bigger + white ring automatically
  useEffect(() => {
    if (!mapRef.current) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    resorts.forEach((resort) => {
      const isSelected = selected?.name === resort.name;
      const color = resort.snow_depth_cm != null ? "#5c8fe8" : "#888";

      const marker = L.circleMarker([resort.lat, resort.lon], {
        radius: isSelected ? 10 : 6,
        fillColor: MARKER_COLOR,
        color: isSelected ? "#fdfdfd" : MARKER_COLOR,
        weight: isSelected ? 2.5 : 1,
        fillOpacity: isSelected ? 1 : 0.7,
      });

      marker.bindPopup(
        `<strong>${resort.name}</strong><br/>
        ${resort.region} · ${resort.prefecture}<br/>
        🌡 ${resort.temp_celsius}°C · ${resort.live_weather}<br/>
        ${resort.snow_depth_cm != null ? `❄ ${resort.snow_depth_cm}cm` : "No snow data"}`,
        { closeButton: false, className: "ski-popup" }
      );

      marker.on("click", () => onSelect(resort));
      // no module on hover 
      marker.addTo(mapRef.current);
      markersRef.current.push(marker);
    });
  }, [resorts, selected, onSelect]);

  // Pan to selected resort
  useEffect(() => {
    if (!mapRef.current || !selected) return;
    mapRef.current.panTo([selected.lat, selected.lon], { animate: true });
  }, [selected]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "100%", minHeight: 480 }}
    />
  );
}

