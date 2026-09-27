export type CameraStatus = "online" | "offline" | "degraded";
export type AlertStatus = "new" | "acknowledged" | "resolved";

export interface Camera {
  id: number;
  name: string;
  department: string;
  lat: number;
  lng: number;
  camera_type: string;
  source_protocol: string;
  stream_endpoint: string;
  status: CameraStatus;
  last_heartbeat: string | null;
  zone: string;
}

export interface DetectionEvent {
  id: number;
  camera_id: number;
  timestamp: string;
  event_type: string;
  vehicle_number: string | null;
  vehicle_type: string | null;
  confidence: number;
  bounding_box: Record<string, number>;
}

export interface Alert {
  id: number;
  event_id: number;
  watchlist_id: number;
  camera_id: number;
  matched_identifier: string;
  confidence: number;
  timestamp: string;
  status: AlertStatus;
  resolved_by: number | null;
  resolved_at: string | null;
}

export interface User {
  id: number;
  username: string;
  role: "admin" | "operator";
}
