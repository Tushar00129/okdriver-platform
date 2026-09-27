import type { CameraStatus } from "../types/api";

export function StatusPill({ status }: { status: CameraStatus }) {
  return <span className={`status-pill status-${status}`}><span className="status-dot" />{status}</span>;
}
