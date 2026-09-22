# TurfMatch

TurfMatch is a Bengaluru-only, 8v8 football club matching MVP. A club owner creates a game, fills eight internal player slots, publishes it for opponent discovery, and approves one rival club to create a confirmed fixture.

The product rules are in [docs/product-spec.md](docs/product-spec.md).

## What works in V1

- Phone number and password signup/login.
- Football profile with skill level and position.
- Club creation and owner-approved player join requests.
- 8v8 game creation with venue, time, cost, and skill level.
- Invite active club members; members accept or reject game invitations.
- A game can publish only after eight players accept.
- Club owners can pass or challenge published opponent cards.
- Host owners can approve one challenge and confirm a fixture.

## Local setup

Requirements:

- Python 3.11
- Node.js 20 or later
- Docker Desktop

Start PostgreSQL from the project root:

```bash
cd /Users/sharmindabadmash/Documents/projs/Matching
docker compose up -d db
```

Prepare the backend, migrate PostgreSQL, and seed demo data:

```bash
cd /Users/sharmindabadmash/Documents/projs/Matching/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8010
```

Open API documentation at [http://127.0.0.1:8010/docs](http://127.0.0.1:8010/docs).

Start the frontend in a second terminal:

```bash
cd /Users/sharmindabadmash/Documents/projs/Matching/frontend
npm install
npm run dev -- --port 3002
```

Open [http://localhost:3002](http://localhost:3002). The frontend expects the backend at `http://127.0.0.1:8010/api/v1`; override it with `NEXT_PUBLIC_API_BASE_URL` if needed. See `frontend/.env.local.example`.

## Demo accounts

Run `python -m app.seed` once after migrations. It creates two club-owner accounts:

```text
Indiranagar FC owner: +919000000001
Koramangala United owner: +919000000002
Password for both: turfmatch123
```

The seed creates eight additional active players for each club. They use the same password and phone numbers from `+919000000003` upward.

## PostgreSQL

```text
Host: 127.0.0.1
Port: 5432
Database: turfmatch
User: turfmatch
Password: turfmatch
```

## Deliberately deferred

Real OTP, payment processing, turf inventory/booking, push notifications, chat, ratings, verification, extra cities, and formats beyond 8v8 are intentionally outside this V1.
