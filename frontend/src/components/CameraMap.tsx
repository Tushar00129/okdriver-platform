import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Camera } from "../types/api";

const statusColors = { online: "#23b26d", degraded: "#f3a93b", offline: "#d85d5d" };

function markerIcon(status: Camera["status"]) {
  return L.divIcon({
    className: "camera-marker-wrap",
    html: `<span class="camera-marker" style="background:${statusColors[status]}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

export function CameraMap({ cameras }: { cameras: Camera[] }) {
  const center: [number, number] = cameras[0] ? [cameras[0].lat, cameras[0].lng] : [12.9716, 77.5946];
  return (
    <MapContainer center={center} zoom={11} scrollWheelZoom className="map-canvas">
      <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {cameras.map((camera) => (
        <Marker key={camera.id} position={[camera.lat, camera.lng]} icon={markerIcon(camera.status)}>
          <Popup>
            <strong>{camera.name}</strong>
            <br />
            {camera.zone} · {camera.status}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
