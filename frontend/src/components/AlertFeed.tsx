import type { Alert, Camera } from "../types/api";

export function AlertFeed({ alerts, cameras, onAction }: { alerts: Alert[]; cameras: Camera[]; onAction: (id: number, action: "acknowledge" | "resolve") => void }) {
  const cameraName = (id: number) => cameras.find((camera) => camera.id === id)?.name ?? `Camera ${id}`;
  return <div className="alert-feed">
    {alerts.length === 0 && <div className="empty-state">No active watchlist alerts</div>}
    {alerts.slice(0, 5).map((alert) => <article className={`alert-row alert-${alert.status}`} key={alert.id}>
      <span className="alert-mark">!</span>
      <div className="alert-copy"><strong>{alert.matched_identifier}</strong><span>{cameraName(alert.camera_id)}</span><small>{new Date(alert.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} · {(alert.confidence * 100).toFixed(0)}% confidence</small></div>
      <div className="alert-actions">{alert.status === "new" && <button onClick={() => onAction(alert.id, "acknowledge")} aria-label="Acknowledge alert">ACK</button>}{alert.status !== "resolved" && <button onClick={() => onAction(alert.id, "resolve")} aria-label="Resolve alert">RESOLVE</button>}</div>
    </article>)}
  </div>;
}
