# TurfMatch checkpoint - 2026-09-23

## Project state

- Source: `/Users/sharmindabadmash/Documents/projs/Matching`
- GitHub: `https://github.com/himanshuSharma-13/turfmatch`
- V1 implementation commit before this note: `32e3559` (`Build TurfMatch 8v8 matching V1`)
- Product rules: [product-spec.md](product-spec.md)

V1 focuses on football in Bengaluru, 8v8 games, and one host club against one challenger club. The UI is intentionally simple.

## Implemented

1. PostgreSQL runs through Docker Compose. Alembic revision `20260922_0002` adds football profiles, club memberships, games, invited players, public match cards, swipes, and club challenges while retaining the earlier tables.
2. FastAPI supports phone/password signup and login, signed bearer tokens, football profiles, club creation, join requests, and owner approval.
3. A club owner can create a game, invite active members, and track accepted and open roster places. Invited players can accept or reject. Publishing requires eight accepted host players.
4. Other club owners can discover a published game, pass, or send a challenge. The host owner can accept one challenge, producing a confirmed fixture.
5. The Next.js mobile web UI connects to these APIs for login, clubs, games, discovery, requests, and profile views. Seed data provides two Bengaluru clubs and demo accounts.

Key files: `backend/app/models.py`, `backend/app/api.py`, `backend/app/auth.py`, `backend/alembic/versions/20260922_0002_game_matching_v1.py`, and `frontend/app/page.tsx`.

## Verification completed at this checkpoint

- Applied Alembic revision `20260922_0002` to the local PostgreSQL database.
- Compiled the backend modules and built the Next.js frontend for production.
- Exercised the API flow against local PostgreSQL: create game, invite eight members, receive eight acceptances, publish, challenge from another club, and confirm the fixture.
- Checked that the local API health route and frontend returned successful HTTP responses.

There is no automated test suite yet. The manual flow created a confirmed fixture in the local demo database; seed data and local database contents may differ from a fresh installation.

## Known gaps for later work

- Real phone verification, turf booking, payments, chat, notifications, ratings, and other cities or formats are deferred by the V1 product rules.
- The UI uses button actions for pass/challenge rather than drag gestures.
- Auth uses a development secret by default. Set `AUTH_SECRET` in `backend/.env` before any deployment.
- Existing data from the original prototype may still be present in a reused Docker volume. A fresh database is the clearest way to review only the new demo data.
- Game completion/cancellation controls, richer fixture details, and automated API/UI tests remain future work.

## Resume locally

Follow the commands in the root [README.md](../README.md). The expected development addresses are frontend `http://localhost:3002` and API docs `http://127.0.0.1:8010/docs`. Demo owner credentials are listed in the README.
