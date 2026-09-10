# TurfMatch V1 Product Contract

## Product scope

TurfMatch V1 is a Bengaluru-only football app for clubs arranging 8v8 turf fixtures.
It has two connected loops:

1. A club fills its own eight-player roster for a game.
2. Once its roster is full, the club finds one opposing eight-player club through a swipeable game card.

## Fixed V1 rules

- Sport: football only.
- City: Bengaluru only.
- Game format: 8v8 only.
- A game has one host club and one challenger club.
- A club can publish a game only after eight host players have accepted it.
- A challenger sends one directional request by liking a Match Card.
- The host owner accepts or rejects that request; there is no mutual swipe.
- Once the host accepts a challenger, the game is locked as one confirmed fixture.
- V1 records a manually entered venue, area, date, time, and per-player cost. It does not provide live turf availability, payments, or turf booking.

## Roles

- Owner: creates a club, manages members, creates games, and accepts or rejects opponent requests.
- Player: joins a club through an owner-approved request and accepts or rejects game invitations.

V1 keeps the roles intentionally small. Captain and admin roles can be added later without changing the core model.

## Roster and slot terminology

`open_slots` means unfilled player places on the host club's game roster.

For an 8v8 game:

```text
host_player_target = 8
accepted_host_players = number of players who accepted
host_open_slots = 8 - accepted_host_players
```

The game cannot be published while `host_open_slots` is greater than zero.

Opponent discovery does not use `open_slots` in V1. A Match Card says "Looking for an 8-player opponent club." A challenger club must be able to bring eight players.

Club membership is separate from game slots. A player can request to join a club, but joining a club does not reserve a place in a particular game.

## Game lifecycle

```text
draft
  -> broadcasting
  -> roster_filled
  -> published
  -> matched
  -> completed

cancelled can be reached before completion.
```

## Match lifecycle

```text
pending
  -> confirmed
  -> completed

rejected or cancelled can be reached before completion.
```

## V1 user journeys

### Owner creates and fills a game

1. Owner creates an 8v8 football game with venue, area, date, time, skill level, and cost.
2. Owner selects up to eight club members and sends them game invitations.
3. Invited players accept or reject.
4. Owner replaces any rejected player until eight players have accepted.
5. The owner publishes the fully filled game to find an opponent club.

### Player joins a club

1. Player creates a football profile with position and skill level.
2. Player discovers a club and sends a join request.
3. Owner accepts or rejects.
4. Once active, the player can receive invitations to that club's games.

### Club finds an opponent

1. Host publishes a fully rostered game as a Match Card.
2. Another club owner discovers the card and sends a challenge request.
3. Host reviews the challenger club's summary and accepts or rejects.
4. Acceptance creates a confirmed 8v8 fixture visible to both clubs.

## Deferred until V2

- Multiple football formats.
- Cities beyond Bengaluru.
- Real phone OTP integration.
- Turf inventory, availability, booking, and payments.
- Chat and notifications.
- Ratings, reliability scores, verification badges, and cancellation penalties.
- Captain/admin permissions.
- Players from multiple clubs filling one opponent side.
