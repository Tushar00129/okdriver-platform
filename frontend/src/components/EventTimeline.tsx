import type { Camera, DetectionEvent } from "../types/api";

export function EventTimeline({ events, cameras }: { events: DetectionEvent[]; cameras: Camera[] }) {
  const cameraName = (id: number) => cameras.find((camera) => camera.id === id)?.name ?? `Camera ${id}`;
  return <div className="timeline">{events.length === 0 && <div className="empty-state">Waiting for detection telemetry...</div>}{events.slice(0, 8).map((event) => <div className="timeline-row" key={event.id}><span className="timeline-time">{new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span><span className="timeline-line" /><div><strong>{event.vehicle_number ?? "Unknown entity"}</strong><span>{cameraName(event.camera_id)} · {event.vehicle_type ?? event.event_type}</span></div><b>{(event.confidence * 100).toFixed(0)}%</b></div>)}</div>;
}
