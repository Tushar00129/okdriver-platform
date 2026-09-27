# System Architecture

The prototype separates camera protocol concerns from the operational API and dashboard. Camera adapters normalize source metadata and detection payloads before they reach the backend. Redis provides event fan-out for multiple API/WebSocket workers, while PostgreSQL remains the durable source of truth.

```mermaid
flowchart LR
    subgraph Sources[Camera sources]
        RTSP[Real RTSP camera]
        ONVIF[ONVIF camera]
        SIM[Simulator / looped test stream]
    end

    subgraph Ingestion[Ingestion and adapter layer]
        Adapter[Camera adapter interface]
        Relay[HLS / WebRTC relay]
        Events[Detection and heartbeat producers]
    end

    subgraph Backend[FastAPI backend]
        API[REST API and auth]
        Correlation[Watchlist correlation]
        AlertEngine[Alert engine]
        WS[Native WebSocket gateway]
    end

    DB[(PostgreSQL)]
    Redis[(Redis Pub/Sub)]
    Dashboard[React operator dashboard]
    Map[Live map and camera views]

    RTSP --> Adapter
    ONVIF --> Adapter
    SIM --> Adapter
    Adapter --> Relay
    Adapter --> Events
    Events --> API
    API --> DB
    API --> Correlation
    Correlation --> DB
    Correlation --> AlertEngine
    AlertEngine --> DB
    AlertEngine --> Redis
    API --> Redis
    Redis --> WS
    WS --> Dashboard
    Relay --> Dashboard
    Dashboard --> Map
    Dashboard --> API
```

## Runtime responsibilities

- **Camera sources:** physical RTSP/ONVIF devices or the local simulator.
- **Adapter layer:** translates source-specific protocols into normalized camera, heartbeat, and detection contracts.
- **FastAPI API:** validates requests, persists operational data, and exposes OpenAPI documentation.
- **Watchlist correlation and alert engine:** match normalized detection identifiers and create actionable alerts.
- **Redis Pub/Sub:** distributes real-time events across backend workers without making Redis the source of truth.
- **WebSocket gateway:** forwards event fan-out to connected dashboard operators.
- **React dashboard and map:** presents live camera status, video, detections, and alerts.
