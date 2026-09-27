# Camera simulator and adapter

The simulator represents two distinct sources:

- `traffic-junction`: MG Road traffic junction
- `rto-checkpoint`: Electronic City RTO checkpoint

Each source has a normalized adapter contract, a stream endpoint, and an event generator. The process onboards both cameras, emits heartbeats, posts detection events, and intentionally uses a configured watchlist identifier every fifth event so the alert path can be demonstrated.

## Run it

The API must be running and the simulator needs either a JWT or login credentials:

```powershell
$env:SIMULATOR_USERNAME="operator"
$env:SIMULATOR_PASSWORD="change-me"
C:/Users/verma/AppData/Local/Programs/Python/Python311/python.exe -m simulator.main
```

For a dependency-free event dry run:

```powershell
$env:SIMULATOR_DRY_RUN="true"
$env:SIMULATOR_RUN_ONCE="true"
C:/Users/verma/AppData/Local/Programs/Python/Python311/python.exe -m simulator.main --once
```

Useful environment variables include `SIMULATOR_API_URL`, `SIMULATOR_TOKEN`, `SIMULATOR_DETECTION_SECONDS`, `SIMULATOR_HEARTBEAT_SECONDS`, and `SIMULATOR_WATCHLIST_IDENTIFIERS`.

## Test HLS relay

The repository does not commit copyrighted media or require FFmpeg at install time. A local FFmpeg installation can create looped test streams for the declared endpoints:

```powershell
mkdir media\traffic-junction,media\rto-checkpoint
ffmpeg -f lavfi -i testsrc=size=1280x720:rate=15 -f lavfi -i sine=frequency=880 -tune zerolatency -c:v libx264 -preset veryfast -c:a aac -f hls -hls_time 2 -hls_list_size 5 -hls_flags delete_segments media\traffic-junction\index.m3u8
```

Serve the `media` directory on port `8081` with a static HTTP server, or replace this relay with a WebRTC/HLS gateway connected to RTSP/ONVIF cameras.

## Replacing the simulator

A production adapter should implement the same normalized operations: source registration, heartbeat, stream URL publication, and detection payload generation. RTSP/ONVIF/vendor SDK code belongs behind that adapter boundary; the FastAPI ingestion, watchlist correlation, alert engine, and dashboard do not need to know the camera protocol.
