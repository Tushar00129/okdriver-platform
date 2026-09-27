# okDriver Platform

Centralized CCTV monitoring, video analytics, and real-time alerting prototype for road-safety operations.

## Project status

The implementation is being delivered in phases. Phases 1 and 2 are complete:

1. Project scaffolding and architecture - complete
2. PostgreSQL schema and Alembic migrations - complete
3. FastAPI APIs, JWT authentication, RBAC, and WebSockets - in progress
4. Camera simulator and adapter layer - complete
5. React operator dashboard
6. Security hardening - in progress
7. Docker packaging
8. Documentation and seed data

## Repository layout

- `backend/` FastAPI application, database layer, services, and camera simulator
- `frontend/` React, Vite, TypeScript, Tailwind dashboard
- `docs/` architecture, data model, and scalability documentation
- `docker-compose.yml` local PostgreSQL, Redis, Adminer, backend, and frontend services

The simulator is documented in [backend/simulator/README.md](backend/simulator/README.md) and can run independently from the backend API.

To create login users and representative camera/watchlist data, follow [backend/README.md](backend/README.md). The seed command requires passwords supplied through environment variables.

## Phase 1 setup

Copy `.env.example` to `.env` and replace development secrets before running the stack:

```powershell
Copy-Item .env.example .env
$env:RUN_SEED="true"
$env:SEED_ADMIN_PASSWORD="replace-with-12-or-more-characters"
$env:SEED_OPERATOR_PASSWORD="replace-with-12-or-more-characters"
docker compose up --build
```

The local services will be available at:

- API and Swagger UI: http://localhost:8000/docs
- Frontend dashboard: http://localhost:5173
- Adminer: http://localhost:8080

With `RUN_SEED=true`, the backend runs Alembic migrations, creates the operator/admin users, adds the two simulator cameras, and creates the representative watchlist target before the simulator starts posting telemetry. Keep `RUN_SEED=false` after the first successful initialization if you do not want the seed step repeated.

## API surface

FastAPI publishes interactive REST documentation at `/docs` and the OpenAPI schema at `/openapi.json`. The API includes JWT auth, camera registry and heartbeats, simulated onboarding, detection ingestion, watchlist CRUD, alert acknowledgement/resolution, and vehicle movement history. Real-time detection, alert, and camera status events are delivered over `/ws`; WebSocket routes are not represented in the OpenAPI `paths` document.

Docker must be installed and running. Backend and frontend implementation is added in later phases.

## Camera adapter direction

Camera ingestion is isolated behind an adapter boundary. The Phase 4 simulator will emit looped test streams and synthetic detection events through the same contracts that a future RTSP/ONVIF or vendor-SDK adapter can implement. A production deployment can place an HLS/WebRTC relay beside the adapter layer without coupling the dashboard to camera vendor protocols.

## Security

No secrets belong in committed files. `.env.example` contains placeholders only; `.env` is ignored by Git.
