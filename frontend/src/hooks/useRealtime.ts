import { useEffect, useRef, useState } from "react";
import { websocketUrl } from "../services/api";

export interface RealtimeEvent {
  type: "detection_event" | "watchlist_alert" | "camera_status_changed" | "alert_status_changed";
  data: Record<string, unknown>;
}

export function useRealtime(onEvent: (event: RealtimeEvent) => void) {
  const callback = useRef(onEvent);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    callback.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    const socket = new WebSocket(websocketUrl());
    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => setConnected(false);
    socket.onmessage = (message) => {
      try {
        callback.current(JSON.parse(message.data) as RealtimeEvent);
      } catch {
        // Ignore malformed third-party relay messages.
      }
    };
    return () => socket.close();
  }, []);

  return connected;
}
