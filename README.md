# TurfMatch

TurfMatch is a Bengaluru-only, 8v8 football club matching MVP. A club owner creates a game, fills eight internal player slots, publishes it for opponent discovery, and approves one rival club to create a confirmed fixture.

The product rules are in [docs/product-spec.md](docs/product-spec.md).
The current implementation snapshot and remaining gaps are in [docs/checkpoint-2026-09-23.md](docs/checkpoint-2026-09-23.md).

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

Open [http://localhost:3002](http://localhost:3002). The frontend forwards `/api/v1` to the backend at `http://127.0.0.1:8010`, so browser requests work when the site is opened from another device. Set `API_BACKEND_URL` in `frontend/.env.local` if the backend runs elsewhere, then restart Next.js. See `frontend/.env.local.example`.

## Demo accounts

Run `python -m app.seed` once after migrations. It creates two club-owner accounts:

```text
Indiranagar FC owner: +919000000001
Koramangala United owner: +919000000002
Password for both: turfmatch123
```

The seed creates eight additional active players for each club. They use the same password and phone numbers from `+919000000003` upward.

### Try Discover

1. Log in as the Indiranagar FC owner (`+919000000001`). Open **Discover** to see three future 8v8 games from Whitefield Wanderers, HSR Rovers, and Northside FC.
2. Swipe left or press **Pass** to skip a game. Swipe right or press **Request game** to send a challenge as Indiranagar FC.
3. Open **Requests** to see the challenge under **Sent game requests**. It stays pending until the host captain approves it.
4. To try the host side for the Whitefield game, log in as `+919100000001` with password `turfmatch123`. Open **Requests** and confirm or decline the incoming challenge.

`python -m app.seed` creates these sample cards on a new database and can be run again without duplicating existing future published demo games. A card disappears from a club's Discover deck once that club passes or requests it.

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
