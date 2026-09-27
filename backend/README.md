# Backend

## Seed local data

Run migrations first, then provide development-only passwords through the environment:

```powershell
$env:SEED_ADMIN_PASSWORD="replace-with-12-or-more-characters"
$env:SEED_OPERATOR_PASSWORD="replace-with-12-or-more-characters"
$env:PYTHONPATH="backend"
python backend/seed.py
```

The idempotent seed creates admin/operator users, two simulator cameras, and the `KA01AB1234` watchlist target. Passwords are never stored in the repository.

## Run API locally

```powershell
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload
```
