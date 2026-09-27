import type { Camera } from "../types/api";
import { StatusPill } from "./StatusPill";

export function CameraTile({ camera }: { camera: Camera }) {
  return (
    <article className="camera-tile">
      <div className="camera-preview">
        {camera.stream_endpoint && camera.status !== "offline" && <video src={camera.stream_endpoint} autoPlay muted loop playsInline />}
        <div className="scanline" />
        <span className="camera-live">LIVE</span>
        <span className="camera-code">CAM-{String(camera.id).padStart(3, "0")}</span>
        {camera.status === "offline" && <div className="camera-offline">Signal unavailable</div>}
        {camera.status === "degraded" && <div className="camera-degraded">Reduced signal quality</div>}
      </div>
      <div className="camera-tile-footer">
        <div><strong>{camera.name}</strong><small>{camera.zone} · {camera.camera_type.replaceAll("_", " ")}</small></div>
        <StatusPill status={camera.status} />
      </div>
    </article>
  );
}
