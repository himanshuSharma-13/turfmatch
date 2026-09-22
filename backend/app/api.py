from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.db.session import get_db

router = APIRouter()


def fail(detail: str, code: int = status.HTTP_400_BAD_REQUEST) -> None:
  raise HTTPException(status_code=code, detail=detail)


def require_owner(club_id: uuid.UUID, user: models.User, db: Session) -> models.Club:
  club = db.get(models.Club, club_id)
  if not club:
    fail("Club not found", status.HTTP_404_NOT_FOUND)
  if club.owner_id != user.id:
    fail("Only the club owner can perform this action", status.HTTP_403_FORBIDDEN)
  return club


def club_read(club: models.Club) -> schemas.ClubRead:
  return schemas.ClubRead(
    id=club.id,
    owner_id=club.owner_id,
    name=club.name,
    city=club.city,
    area=club.area,
    home_turf=club.home_turf,
    description=club.description,
    skill_level=club.skill_level,
    availability=club.availability,
    play_style=club.play_style,
    rating=club.rating,
    player_count=club.player_count,
    created_at=club.created_at,
  )


def member_read(member: models.ClubMember) -> schemas.ClubMemberRead:
  profile = next((item for item in member.user.sport_profiles if item.sport == "football"), None)
  return schemas.ClubMemberRead(
    id=member.id,
    club_id=member.club_id,
    user_id=member.user_id,
    display_name=member.user.display_name,
    phone_number=member.user.phone_number,
    role=member.role,
    status=member.status,
    position=profile.position if profile else None,
    skill_level=profile.skill_level if profile else None,
    joined_at=member.joined_at,
  )


def refresh_club_count(club_id: uuid.UUID, db: Session) -> None:
  count = db.scalar(
    select(func.count()).select_from(models.ClubMember).where(
      models.ClubMember.club_id == club_id, models.ClubMember.status == models.MembershipStatus.active
    )
  )
  club = db.get(models.Club, club_id)
  if club:
    club.player_count = int(count or 0)


def accepted_count(game_id: uuid.UUID, db: Session, excluding_user: uuid.UUID | None = None) -> int:
  query = select(func.count()).select_from(models.GameParticipant).where(
    models.GameParticipant.game_id == game_id,
    models.GameParticipant.status == models.ParticipantStatus.accepted,
  )
  if excluding_user:
    query = query.where(models.GameParticipant.user_id != excluding_user)
  return int(db.scalar(query) or 0)


def refresh_game_roster(game: models.Game, db: Session) -> None:
  accepted = accepted_count(game.id, db)
  game.host_open_slots = max(game.host_player_target - accepted, 0)
  if accepted == game.host_player_target and game.status in {models.GameStatus.draft, models.GameStatus.broadcasting}:
    game.status = models.GameStatus.roster_filled
  elif accepted < game.host_player_target and game.status == models.GameStatus.roster_filled:
    game.status = models.GameStatus.broadcasting


def game_read(game: models.Game, db: Session) -> schemas.GameRead:
  accepted = accepted_count(game.id, db)
  pending = int(
    db.scalar(
      select(func.count()).select_from(models.GameParticipant).where(
        models.GameParticipant.game_id == game.id,
        models.GameParticipant.status == models.ParticipantStatus.pending,
      )
    )
    or 0
  )
  opponent = db.get(models.Club, game.opponent_club_id) if game.opponent_club_id else None
  return schemas.GameRead(
    id=game.id,
    club_id=game.club_id,
    club_name=game.host_club.name if game.host_club else db.get(models.Club, game.club_id).name,
    venue=game.venue,
    venue_area=game.venue_area,
    scheduled_at=game.scheduled_at,
    cost_per_person=game.cost_per_person,
    skill_level=game.skill_level,
    format=game.format,
    host_player_target=game.host_player_target,
    host_open_slots=game.host_open_slots,
    accepted_players=accepted,
    pending_players=pending,
    status=game.status,
    opponent_club_id=game.opponent_club_id,
    opponent_club_name=opponent.name if opponent else None,
    created_at=game.created_at,
  )


def card_read(card: models.MatchCard, db: Session) -> schemas.MatchCardRead:
  game = card.game
  club = db.get(models.Club, card.club_id)
  return schemas.MatchCardRead(
    id=card.id,
    game_id=game.id,
    club_id=club.id,
    club_name=club.name,
    club_area=club.area,
    club_skill_level=club.skill_level,
    club_rating=club.rating,
    venue_area=game.venue_area,
    scheduled_at=game.scheduled_at,
    cost_per_person=game.cost_per_person,
    skill_level=game.skill_level,
    format=game.format,
    status=card.status,
    published_at=card.published_at,
  )


def challenge_read(challenge: models.Challenge, db: Session) -> schemas.ChallengeRead:
  host = db.get(models.Club, challenge.host_club_id)
  challenger = db.get(models.Club, challenge.challenger_club_id)
  return schemas.ChallengeRead(
    id=challenge.id,
    game_id=challenge.game_id,
    match_card_id=challenge.match_card_id,
    host_club_id=challenge.host_club_id,
    host_club_name=host.name,
    challenger_club_id=challenge.challenger_club_id,
    challenger_club_name=challenger.name,
    status=challenge.status,
    created_at=challenge.created_at,
    confirmed_at=challenge.confirmed_at,
  )


@router.get("/health")
def health() -> dict[str, str]:
  return {"status": "ok"}


@router.post("/auth/signup", response_model=schemas.AuthRead, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.SignupInput, db: Session = Depends(get_db)) -> schemas.AuthRead:
  if db.scalar(select(models.User).where(models.User.phone_number == payload.phone_number)):
    fail("Phone number already registered", status.HTTP_409_CONFLICT)
  user = models.User(
    phone_number=payload.phone_number,
    display_name=payload.display_name,
    city="Bengaluru",
    password_hash=hash_password(payload.password),
  )
  db.add(user)
  db.flush()
  db.add(models.SportProfile(user_id=user.id, sport="football", skill_level=payload.skill_level, position=payload.position))
  db.commit()
  db.refresh(user)
  return schemas.AuthRead(access_token=create_access_token(user.id), user=user)


@router.post("/auth/login", response_model=schemas.AuthRead)
def login(payload: schemas.LoginInput, db: Session = Depends(get_db)) -> schemas.AuthRead:
  user = db.scalar(select(models.User).where(models.User.phone_number == payload.phone_number))
  if not user or not verify_password(payload.password, user.password_hash):
    fail("Invalid phone number or password", status.HTTP_401_UNAUTHORIZED)
  return schemas.AuthRead(access_token=create_access_token(user.id), user=user)


@router.get("/users/me", response_model=schemas.UserRead)
def read_me(user: models.User = Depends(get_current_user)) -> models.User:
  return user


@router.put("/users/me/football-profile", response_model=schemas.SportProfileRead)
def update_football_profile(
  payload: schemas.SportProfileInput, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
) -> models.SportProfile:
  profile = db.scalar(select(models.SportProfile).where(models.SportProfile.user_id == user.id, models.SportProfile.sport == "football"))
  if not profile:
    profile = models.SportProfile(user_id=user.id, sport="football", **payload.model_dump())
    db.add(profile)
  else:
    profile.skill_level = payload.skill_level
    profile.position = payload.position
  db.commit()
  db.refresh(profile)
  return profile


@router.get("/clubs", response_model=list[schemas.ClubRead])
def list_clubs(area: str | None = None, skill_level: models.SkillLevel | None = None, db: Session = Depends(get_db)) -> list[schemas.ClubRead]:
  query = select(models.Club).where(models.Club.city == "Bengaluru")
  if area:
    query = query.where(models.Club.area.ilike(f"%{area}%"))
  if skill_level:
    query = query.where(models.Club.skill_level == skill_level)
  clubs = db.scalars(query.order_by(models.Club.rating.desc(), models.Club.created_at.desc())).all()
  return [club_read(club) for club in clubs]


@router.post("/clubs", response_model=schemas.ClubRead, status_code=status.HTTP_201_CREATED)
def create_club(payload: schemas.ClubCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> schemas.ClubRead:
  club = models.Club(owner_id=user.id, city="Bengaluru", image_url="", **payload.model_dump())
  db.add(club)
  db.flush()
  db.add(
    models.ClubMember(
      club_id=club.id,
      user_id=user.id,
      role=models.MembershipRole.owner,
      status=models.MembershipStatus.active,
      joined_at=datetime.now(UTC),
    )
  )
  refresh_club_count(club.id, db)
  user.is_captain = True
  db.commit()
  db.refresh(club)
  return club_read(club)


@router.get("/clubs/{club_id}", response_model=schemas.ClubRead)
def read_club(club_id: uuid.UUID, db: Session = Depends(get_db)) -> schemas.ClubRead:
  club = db.get(models.Club, club_id)
  if not club:
    fail("Club not found", status.HTTP_404_NOT_FOUND)
  return club_read(club)


@router.get("/clubs/{club_id}/members", response_model=list[schemas.ClubMemberRead])
def list_members(club_id: uuid.UUID, db: Session = Depends(get_db)) -> list[schemas.ClubMemberRead]:
  members = db.scalars(
    select(models.ClubMember)
    .options(joinedload(models.ClubMember.user).selectinload(models.User.sport_profiles))
    .where(models.ClubMember.club_id == club_id)
    .order_by(models.ClubMember.status, models.ClubMember.role)
  ).all()
  return [member_read(member) for member in members]


@router.post("/clubs/{club_id}/join-requests", response_model=schemas.ClubMemberRead, status_code=status.HTTP_201_CREATED)
def request_to_join(club_id: uuid.UUID, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> schemas.ClubMemberRead:
  if not db.get(models.Club, club_id):
    fail("Club not found", status.HTTP_404_NOT_FOUND)
  existing = db.scalar(select(models.ClubMember).where(models.ClubMember.club_id == club_id, models.ClubMember.user_id == user.id))
  if existing:
    fail("You already have a membership or request for this club", status.HTTP_409_CONFLICT)
  member = models.ClubMember(club_id=club_id, user_id=user.id)
  db.add(member)
  db.commit()
  db.refresh(member)
  member.user = user
  return member_read(member)


@router.get("/clubs/{club_id}/join-requests", response_model=list[schemas.ClubMemberRead])
def list_join_requests(club_id: uuid.UUID, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[schemas.ClubMemberRead]:
  require_owner(club_id, user, db)
  members = db.scalars(
    select(models.ClubMember)
    .options(joinedload(models.ClubMember.user).selectinload(models.User.sport_profiles))
    .where(models.ClubMember.club_id == club_id, models.ClubMember.status == models.MembershipStatus.pending)
  ).all()
  return [member_read(member) for member in members]


@router.post("/club-members/{member_id}/decision", response_model=schemas.ClubMemberRead)
def decide_membership(
  member_id: uuid.UUID,
  payload: schemas.MembershipDecision,
  user: models.User = Depends(get_current_user),
  db: Session = Depends(get_db),
) -> schemas.ClubMemberRead:
  member = db.scalar(
    select(models.ClubMember)
    .options(joinedload(models.ClubMember.user).selectinload(models.User.sport_profiles))
    .where(models.ClubMember.id == member_id)
  )
  if not member:
    fail("Membership request not found", status.HTTP_404_NOT_FOUND)
  require_owner(member.club_id, user, db)
  if member.status != models.MembershipStatus.pending:
    fail("This membership request has already been decided")
  member.status = models.MembershipStatus.active if payload.approve else models.MembershipStatus.removed
  member.joined_at = datetime.now(UTC) if payload.approve else None
  refresh_club_count(member.club_id, db)
  db.commit()
  db.refresh(member)
  return member_read(member)


@router.get("/clubs/{club_id}/games", response_model=list[schemas.GameRead])
def list_club_games(club_id: uuid.UUID, db: Session = Depends(get_db)) -> list[schemas.GameRead]:
  games = db.scalars(
    select(models.Game).options(joinedload(models.Game.host_club)).where(models.Game.club_id == club_id).order_by(models.Game.scheduled_at)
  ).all()
  return [game_read(game, db) for game in games]


@router.post("/clubs/{club_id}/games", response_model=schemas.GameRead, status_code=status.HTTP_201_CREATED)
def create_game(
  club_id: uuid.UUID, payload: schemas.GameCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
) -> schemas.GameRead:
  club = require_owner(club_id, user, db)
  game = models.Game(club_id=club.id, created_by=user.id, sport="football", format="8v8", **payload.model_dump())
  db.add(game)
  db.commit()
  db.refresh(game)
  game.host_club = club
  return game_read(game, db)


@router.get("/games/{game_id}", response_model=schemas.GameRead)
def read_game(game_id: uuid.UUID, db: Session = Depends(get_db)) -> schemas.GameRead:
  game = db.scalar(select(models.Game).options(joinedload(models.Game.host_club)).where(models.Game.id == game_id))
  if not game:
    fail("Game not found", status.HTTP_404_NOT_FOUND)
  return game_read(game, db)


@router.get("/games/{game_id}/participants", response_model=list[schemas.ParticipantRead])
def list_participants(
  game_id: uuid.UUID, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[schemas.ParticipantRead]:
  game = db.get(models.Game, game_id)
  if not game:
    fail("Game not found", status.HTTP_404_NOT_FOUND)
  if game.created_by != user.id:
    is_invited = db.scalar(select(models.GameParticipant.id).where(models.GameParticipant.game_id == game_id, models.GameParticipant.user_id == user.id))
    if not is_invited:
      fail("You do not have access to this game", status.HTTP_403_FORBIDDEN)
  rows = db.scalars(
    select(models.GameParticipant).options(joinedload(models.GameParticipant.user)).where(models.GameParticipant.game_id == game_id)
  ).all()
  return [schemas.ParticipantRead(id=row.id, game_id=row.game_id, user_id=row.user_id, display_name=row.user.display_name, status=row.status, responded_at=row.responded_at) for row in rows]


@router.post("/games/{game_id}/invitations", response_model=list[schemas.ParticipantRead])
def invite_players(
  game_id: uuid.UUID, payload: schemas.InvitationInput, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[schemas.ParticipantRead]:
  game = db.get(models.Game, game_id)
  if not game:
    fail("Game not found", status.HTTP_404_NOT_FOUND)
  require_owner(game.club_id, user, db)
  if game.status not in {models.GameStatus.draft, models.GameStatus.broadcasting}:
    fail("Invitations can only be sent while a game roster is being filled")
  active_ids = set(
    db.scalars(
      select(models.ClubMember.user_id).where(
        models.ClubMember.club_id == game.club_id, models.ClubMember.status == models.MembershipStatus.active
      )
    ).all()
  )
  requested = set(payload.player_ids)
  if not requested.issubset(active_ids):
    fail("Every invited player must be an active club member")
  existing_ids = set(db.scalars(select(models.GameParticipant.user_id).where(models.GameParticipant.game_id == game_id)).all())
  new_ids = requested - existing_ids
  for player_id in new_ids:
    db.add(models.GameParticipant(game_id=game.id, user_id=player_id, status=models.ParticipantStatus.pending))
  game.status = models.GameStatus.broadcasting
  db.commit()
  rows = db.scalars(
    select(models.GameParticipant).options(joinedload(models.GameParticipant.user)).where(models.GameParticipant.game_id == game_id)
  ).all()
  return [schemas.ParticipantRead(id=row.id, game_id=row.game_id, user_id=row.user_id, display_name=row.user.display_name, status=row.status, responded_at=row.responded_at) for row in rows]


@router.get("/users/me/games/upcoming", response_model=list[schemas.GameRead])
def my_upcoming_games(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[schemas.GameRead]:
  games = db.scalars(
    select(models.Game)
    .options(joinedload(models.Game.host_club))
    .join(models.GameParticipant)
    .where(models.GameParticipant.user_id == user.id, models.Game.status.not_in([models.GameStatus.cancelled, models.GameStatus.completed]))
    .order_by(models.Game.scheduled_at)
  ).all()
  return [game_read(game, db) for game in games]


@router.post("/games/{game_id}/respond", response_model=schemas.ParticipantRead)
def respond_to_game(
  game_id: uuid.UUID,
  payload: schemas.ParticipantResponse,
  user: models.User = Depends(get_current_user),
  db: Session = Depends(get_db),
) -> schemas.ParticipantRead:
  participant = db.scalar(
    select(models.GameParticipant).options(joinedload(models.GameParticipant.user)).where(
      models.GameParticipant.game_id == game_id, models.GameParticipant.user_id == user.id
    )
  )
  if not participant:
    fail("You were not invited to this game", status.HTTP_404_NOT_FOUND)
  game = db.get(models.Game, game_id)
  if payload.status == models.ParticipantStatus.pending:
    fail("A response must be accepted or rejected")
  if payload.status == models.ParticipantStatus.accepted:
    if accepted_count(game_id, db, excluding_user=user.id) >= game.host_player_target:
      fail("This game roster is already full", status.HTTP_409_CONFLICT)
  participant.status = payload.status
  participant.responded_at = datetime.now(UTC)
  db.flush()
  refresh_game_roster(game, db)
  db.commit()
  db.refresh(participant)
  return schemas.ParticipantRead(id=participant.id, game_id=participant.game_id, user_id=participant.user_id, display_name=participant.user.display_name, status=participant.status, responded_at=participant.responded_at)


@router.post("/games/{game_id}/publish", response_model=schemas.MatchCardRead, status_code=status.HTTP_201_CREATED)
def publish_game(game_id: uuid.UUID, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> schemas.MatchCardRead:
  game = db.scalar(select(models.Game).options(joinedload(models.Game.host_club)).where(models.Game.id == game_id))
  if not game:
    fail("Game not found", status.HTTP_404_NOT_FOUND)
  require_owner(game.club_id, user, db)
  refresh_game_roster(game, db)
  if game.host_open_slots != 0 or game.status != models.GameStatus.roster_filled:
    fail("Eight host players must accept before this game can be published")
  if game.match_card:
    fail("This game is already published", status.HTTP_409_CONFLICT)
  card = models.MatchCard(game_id=game.id, club_id=game.club_id, status=models.CardStatus.active)
  game.status = models.GameStatus.published
  db.add(card)
  db.commit()
  db.refresh(card)
  card.game = game
  return card_read(card, db)


@router.get("/match-cards/feed", response_model=list[schemas.MatchCardRead])
def match_card_feed(
  club_id: uuid.UUID, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[schemas.MatchCardRead]:
  require_owner(club_id, user, db)
  swiped = select(models.Swipe.match_card_id).where(models.Swipe.swiping_club_id == club_id)
  cards = db.scalars(
    select(models.MatchCard)
    .options(joinedload(models.MatchCard.game))
    .where(
      models.MatchCard.status == models.CardStatus.active,
      models.MatchCard.club_id != club_id,
      models.MatchCard.id.not_in(swiped),
    )
    .order_by(models.MatchCard.published_at.desc())
  ).all()
  return [card_read(card, db) for card in cards]


@router.post("/match-cards/{card_id}/swipe", response_model=schemas.ChallengeRead | None)
def swipe_card(
  card_id: uuid.UUID,
  payload: schemas.SwipeInput,
  user: models.User = Depends(get_current_user),
  db: Session = Depends(get_db),
) -> schemas.ChallengeRead | None:
  card = db.scalar(select(models.MatchCard).options(joinedload(models.MatchCard.game)).where(models.MatchCard.id == card_id))
  if not card or card.status != models.CardStatus.active:
    fail("Match card is not available", status.HTTP_404_NOT_FOUND)
  club = require_owner(payload.club_id, user, db)
  if card.club_id == club.id:
    fail("A club cannot challenge its own game")
  existing = db.scalar(select(models.Swipe).where(models.Swipe.match_card_id == card.id, models.Swipe.swiping_club_id == club.id))
  if existing:
    fail("This club has already acted on this game card", status.HTTP_409_CONFLICT)
  db.add(models.Swipe(match_card_id=card.id, swiping_club_id=club.id, swiping_owner_id=user.id, direction=payload.direction))
  if payload.direction == models.SwipeDirection.pass_:
    db.commit()
    return None
  active_members = int(
    db.scalar(
      select(func.count()).select_from(models.ClubMember).where(
        models.ClubMember.club_id == club.id, models.ClubMember.status == models.MembershipStatus.active
      )
    )
    or 0
  )
  if active_members < 8:
    fail("Your club needs at least eight active members before challenging a game")
  challenge = models.Challenge(
    match_card_id=card.id,
    game_id=card.game_id,
    host_club_id=card.club_id,
    challenger_club_id=club.id,
    challenger_owner_id=user.id,
    status=models.ChallengeStatus.pending,
  )
  db.add(challenge)
  db.commit()
  db.refresh(challenge)
  return challenge_read(challenge, db)


@router.get("/clubs/{club_id}/challenges/incoming", response_model=list[schemas.ChallengeRead])
def incoming_challenges(
  club_id: uuid.UUID, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[schemas.ChallengeRead]:
  require_owner(club_id, user, db)
  challenges = db.scalars(
    select(models.Challenge).where(models.Challenge.host_club_id == club_id).order_by(models.Challenge.created_at.desc())
  ).all()
  return [challenge_read(challenge, db) for challenge in challenges]


@router.post("/challenges/{challenge_id}/decision", response_model=schemas.ChallengeRead)
def decide_challenge(
  challenge_id: uuid.UUID,
  payload: schemas.MembershipDecision,
  user: models.User = Depends(get_current_user),
  db: Session = Depends(get_db),
) -> schemas.ChallengeRead:
  challenge = db.get(models.Challenge, challenge_id)
  if not challenge:
    fail("Challenge not found", status.HTTP_404_NOT_FOUND)
  require_owner(challenge.host_club_id, user, db)
  if challenge.status != models.ChallengeStatus.pending:
    fail("This challenge has already been decided")
  game = db.get(models.Game, challenge.game_id)
  card = db.get(models.MatchCard, challenge.match_card_id)
  if payload.approve:
    if game.status != models.GameStatus.published or card.status != models.CardStatus.active:
      fail("This game is no longer available for matching")
    challenge.status = models.ChallengeStatus.confirmed
    challenge.confirmed_at = datetime.now(UTC)
    game.status = models.GameStatus.matched
    game.opponent_club_id = challenge.challenger_club_id
    card.status = models.CardStatus.matched
    other_pending = db.scalars(
      select(models.Challenge).where(
        models.Challenge.game_id == game.id,
        models.Challenge.id != challenge.id,
        models.Challenge.status == models.ChallengeStatus.pending,
      )
    ).all()
    for other in other_pending:
      other.status = models.ChallengeStatus.rejected
  else:
    challenge.status = models.ChallengeStatus.rejected
  db.commit()
  db.refresh(challenge)
  return challenge_read(challenge, db)


@router.get("/fixtures", response_model=list[schemas.ChallengeRead])
def fixtures(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[schemas.ChallengeRead]:
  club_ids = select(models.Club.id).where(models.Club.owner_id == user.id)
  challenges = db.scalars(
    select(models.Challenge)
    .where(
      models.Challenge.status == models.ChallengeStatus.confirmed,
      (models.Challenge.host_club_id.in_(club_ids)) | (models.Challenge.challenger_club_id.in_(club_ids)),
    )
    .order_by(models.Challenge.confirmed_at.desc())
  ).all()
  return [challenge_read(challenge, db) for challenge in challenges]
