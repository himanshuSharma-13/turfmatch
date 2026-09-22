# TurfMatch Backend

FastAPI backend for the Bengaluru 8v8 football club matchmaking MVP.

## Local Setup

Start PostgreSQL:

```bash
docker compose up -d db
```

Create and activate a virtual environment:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run migrations and seed demo data:

```bash
alembic upgrade head
python -m app.seed
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8010
```

Open Swagger docs:

```text
http://localhost:8010/docs
```
