import type { Alert, Camera, DetectionEvent, User } from "../types/api";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("okdriver_token");
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with ${response.status}`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export async function login(username: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username, password });
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) throw new Error("Invalid operator credentials");
  const result = (await response.json()) as { access_token: string };
  localStorage.setItem("okdriver_token", result.access_token);
  return result.access_token;
}

export const getMe = () => request<User>("/auth/me");
export const getCameras = () => request<Camera[]>("/cameras");
export const getAlerts = () => request<Alert[]>("/alerts");
export const getRecentEvents = () => request<DetectionEvent[]>("/events?limit=30");
export const updateAlert = (id: number, action: "acknowledge" | "resolve") =>
  request<Alert>(`/alerts/${id}/${action}`, { method: "POST" });

export function logout() {
  localStorage.removeItem("okdriver_token");
}

export const websocketUrl = () => {
  const configured = import.meta.env.VITE_WS_URL;
  if (configured) return configured;
  return `${API_URL.replace(/^http/, "ws")}/ws`;
};
