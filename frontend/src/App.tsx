import { useCallback, useEffect, useState } from "react";
import { AlertFeed } from "./components/AlertFeed";
import { CameraMap } from "./components/CameraMap";
import { CameraTile } from "./components/CameraTile";
import { EventTimeline } from "./components/EventTimeline";
import { LoginScreen } from "./components/LoginScreen";
import { MetricCard } from "./components/MetricCard";
import { useRealtime, type RealtimeEvent } from "./hooks/useRealtime";
import { AlertsPage, CameraRegistryPage, EntitySearchPage, WatchlistPage } from "./pages/WorkspacePages";
import { getAlerts, getCameras, getMe, getRecentEvents, logout, updateAlert } from "./services/api";
import type { Alert, Camera, DetectionEvent, User } from "./types/api";

const navItems = ["Live operations", "Camera registry", "Entity search", "Watchlist", "Alerts"];

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(localStorage.getItem("okdriver_token")));
  if (!authenticated) return <LoginScreen onLogin={() => setAuthenticated(true)} />;
  return <Operations onLogout={() => { logout(); setAuthenticated(false); }} />;
}

function Operations({ onLogout }: { onLogout: () => void }) {
  const [activeNav, setActiveNav] = useState(navItems[0]);
  const [user, setUser] = useState<User | null>(null);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [events, setEvents] = useState<DetectionEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [me, cameraData, alertData, eventData] = await Promise.all([getMe(), getCameras(), getAlerts(), getRecentEvents()]);
      setUser(me); setCameras(cameraData); setAlerts(alertData); setEvents(eventData);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to connect to the operations API");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void loadData(); }, [loadData]);

  const handleEvent = useCallback((event: RealtimeEvent) => {
    if (event.type === "camera_status_changed") {
      setCameras((current) => current.map((camera) => camera.id === event.data.camera_id ? { ...camera, status: event.data.status as Camera["status"] } : camera));
    }
    if (event.type === "detection_event") {
      setEvents((current) => [{ ...(event.data as unknown as DetectionEvent) }, ...current].slice(0, 30));
    }
    if (event.type === "watchlist_alert") {
      const data = event.data;
      setAlerts((current) => [{ id: Number(data.id), event_id: Number(data.event_id), watchlist_id: 0, camera_id: Number(data.camera_id), matched_identifier: String(data.identifier), confidence: Number(data.confidence), timestamp: String(data.timestamp), status: "new", resolved_by: null, resolved_at: null }, ...current]);
    }
    if (event.type === "alert_status_changed") {
      setAlerts((current) => current.map((alert) => alert.id === Number(event.data.id) ? { ...alert, status: event.data.status as Alert["status"] } : alert));
    }
  }, []);
  const realtimeConnected = useRealtime(handleEvent);

  async function actOnAlert(id: number, action: "acknowledge" | "resolve") {
    try { const updated = await updateAlert(id, action); setAlerts((current) => current.map((alert) => alert.id === id ? updated : alert)); } catch (err) { setError(err instanceof Error ? err.message : "Alert action failed"); }
  }

  const online = cameras.filter((camera) => camera.status === "online").length;
  const degraded = cameras.filter((camera) => camera.status === "degraded").length;
  const offline = cameras.filter((camera) => camera.status === "offline").length;
  const activeAlerts = alerts.filter((alert) => alert.status !== "resolved").length;

  const workspace = activeNav === "Camera registry" ? <CameraRegistryPage cameras={cameras} onRefresh={() => void loadData()} user={user} /> : activeNav === "Entity search" ? <EntitySearchPage cameras={cameras} /> : activeNav === "Watchlist" ? <WatchlistPage onRefresh={() => void loadData()} /> : activeNav === "Alerts" ? <AlertsPage cameras={cameras} /> : null;

  return <div className="app-shell">
    <aside className="sidebar"><div className="brand-mark">OK<span>•</span>DRIVER</div><div className="sidebar-label">OPERATIONS CENTER</div><nav>{navItems.map((item, index) => <button className={activeNav === item ? "nav-item active" : "nav-item"} key={item} onClick={() => setActiveNav(item)}><span className="nav-index">0{index + 1}</span>{item}<span className="nav-arrow">↗</span></button>)}</nav><div className="sidebar-bottom"><div className="relay-state"><span className={realtimeConnected ? "pulse live" : "pulse"} />{realtimeConnected ? "LIVE RELAY CONNECTED" : "RECONNECTING TO RELAY"}</div><button className="profile-button"><span className="avatar">{user?.username.slice(0, 1).toUpperCase() ?? "O"}</span><span><strong>{user?.username ?? "operator"}</strong><small>{user?.role ?? "operator"}</small></span><span>···</span></button></div></aside>
    <main className="content"><header className="topbar"><div><p className="eyebrow">SUNDAY / 27 SEPTEMBER 2026</p><h1>{activeNav}</h1></div><div className="top-actions"><span className="system-clock">{new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} <small>LOCAL</small></span><button className="icon-button" onClick={() => void loadData()} aria-label="Refresh operations data">↻</button><button className="logout-button" onClick={onLogout}>Sign out</button></div></header>{error && <div className="connection-banner"><span>!</span>{error}<button onClick={() => void loadData()}>RETRY</button></div>}{activeNav === "Live operations" ? <><section className="metrics-grid"><MetricCard label="Cameras online" value={loading ? "—" : online} note={`${cameras.length} registered sources`} tone="green" /><MetricCard label="Active alerts" value={loading ? "—" : activeAlerts} note="Requires operator review" tone="coral" /><MetricCard label="Degraded feeds" value={loading ? "—" : degraded} note={`${offline} offline · status now`} tone="amber" /><MetricCard label="Events today" value={loading ? "—" : events.length} note="Live telemetry window" /></section><section className="dashboard-grid"><div className="section-block camera-block"><div className="section-heading"><div><p className="eyebrow">SOURCE MONITORING</p><h2>Live camera wall</h2></div><span className="section-count">{cameras.length} SOURCES</span></div><div className="camera-grid">{cameras.length === 0 && !loading ? <div className="empty-state wide">No cameras registered. Run the simulator onboarding to populate this wall.</div> : cameras.map((camera) => <CameraTile camera={camera} key={camera.id} />)}</div></div><div className="section-block alert-block"><div className="section-heading"><div><p className="eyebrow">PRIORITY QUEUE</p><h2>Watchlist alerts</h2></div><span className="alert-count">{activeAlerts} OPEN</span></div><AlertFeed alerts={alerts.filter((alert) => alert.status !== "resolved")} cameras={cameras} onAction={actOnAlert} /></div><div className="section-block map-block"><div className="section-heading"><div><p className="eyebrow">GEOSPATIAL OVERVIEW</p><h2>Camera network</h2></div><span className="section-count">{online} ONLINE</span></div><CameraMap cameras={cameras} /></div><div className="section-block timeline-block"><div className="section-heading"><div><p className="eyebrow">INGESTION STREAM</p><h2>Detection timeline</h2></div><span className="section-count">REAL-TIME</span></div><EventTimeline events={events} cameras={cameras} /></div></section></> : workspace}</main>
  </div>;
}
