# TurfMatch

Football matchmaking app for 5v5 turf games.

Current repo structure:

- `frontend/` - Next.js mobile-style web app
- `backend/` - FastAPI API
- `docker-compose.yml` - local PostgreSQL

## PostgreSQL Docker Details

The local PostgreSQL instance is defined in [docker-compose.yml](/Users/sharmindabadmash/Documents/Matching/docker-compose.yml).

Credentials:

- `Container name`: `turfmatch_postgres`
- `Database`: `turfmatch`
- `Username`: `turfmatch`
- `Password`: `turfmatch`
- `Port`: `5432`

Important:

- `turfmatch_postgres` is the Docker container name.
- From apps running on your Mac, including pgAdmin, use `127.0.0.1` as the host.
- Do not use `postgres` as the username or database for this container.

pgAdmin connection values:

- `Host name/address`: `127.0.0.1`
- `Port`: `5432`
- `Maintenance database`: `turfmatch`
- `Username`: `turfmatch`
- `Password`: `turfmatch`

Equivalent connection string:

```text
postgresql://turfmatch:turfmatch@127.0.0.1:5432/turfmatch
```

## Start Docker Database

From the repo root:

```bash
cd /Users/sharmindabadmash/Documents/Matching
docker compose up -d db
docker ps
```

Expected container:

- `turfmatch_postgres`

## Backend Setup

Use Python 3.11.

```bash
cd /Users/sharmindabadmash/Documents/Matching/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Backend docs:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Frontend Setup

```bash
cd /Users/sharmindabadmash/Documents/Matching/frontend
npm install
npm run dev
```

Frontend app:

- [http://localhost:3000](http://localhost:3000)

## Useful Checks

Verify Docker Postgres from terminal:

```bash
docker exec -it turfmatch_postgres psql -U turfmatch -d turfmatch
```

If pgAdmin cannot connect, check these first:

- Host must be `127.0.0.1`
- Username must be `turfmatch`
- Database must be `turfmatch`
- Password must be `turfmatch`
- Docker container must be running
