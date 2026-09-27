# Alembic migrations

The initial monitoring schema is defined in `versions/0001_initial_schema.py` and uses the shared SQLAlchemy metadata from `app.models`.

Run migrations from the repository root after copying `.env.example` to `.env`:

```powershell
alembic upgrade head
```

The migration environment reads `DATABASE_URL` from the environment and uses the async PostgreSQL driver configured by the backend.
