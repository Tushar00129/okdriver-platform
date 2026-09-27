# Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ CAMERA_AUDIT_LOG : makes
    USERS ||--o{ ALERTS : resolves
    CAMERAS ||--o{ CAMERA_AUDIT_LOG : records
    CAMERAS ||--o{ DETECTION_EVENTS : produces
    CAMERAS ||--o{ ALERTS : triggers
    WATCHLIST ||--o{ ALERTS : matches
    DETECTION_EVENTS ||--o{ ALERTS : creates

    USERS {
        int id PK
        string username UK
        string password_hash
        enum role
        datetime created_at
    }
    CAMERAS {
        int id PK
        string name
        string department
        float lat
        float lng
        string camera_type
        string source_protocol
        string stream_endpoint
        enum status
        datetime last_heartbeat
        string zone
        json storage_metadata
    }
    CAMERA_AUDIT_LOG {
        int id PK
        int camera_id FK
        int changed_by FK
        string action
        json changed_fields
        datetime created_at
    }
    DETECTION_EVENTS {
        int id PK
        int camera_id FK
        datetime timestamp
        string event_type
        string vehicle_number
        string vehicle_type
        float confidence
        json bounding_box
        json raw_payload
    }
    WATCHLIST {
        int id PK
        enum entity_type
        string identifier
        string reason
        string status
        int added_by FK
        datetime created_at
    }
    ALERTS {
        int id PK
        int event_id FK
        int watchlist_id FK
        int camera_id FK
        string matched_identifier
        float confidence
        datetime timestamp
        enum status
        int resolved_by FK
    }
```

The database keeps detection events immutable and links alerts back to the event, matched watchlist item, and source camera. JSONB columns retain vendor-specific payload details without forcing schema changes for every camera integration.
