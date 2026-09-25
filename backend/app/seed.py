from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from app import models
from app.auth import hash_password
from app.db.session import SessionLocal

DEMO_PASSWORD = "turfmatch123"
SAMPLE_GAMES = (
  ("Whitefield Wanderers", "Whitefield", "Turf Park Whitefield", "intermediate", 2, 19, 30, 250,
   "Fast transitions and friendly competition every week.",
   "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1000&q=80"),
  ("HSR Rovers", "HSR Layout", "HSR Football Arena", "casual", 4, 20, 0, 300,
   "Mixed-ability side that plays an easygoing passing game.",
   "https://images.unsplash.com/photo-1551958219-acbc608c6377?auto=format&fit=crop&w=1000&q=80"),
  ("Northside FC", "Hebbal", "Hebbal Sports Turf", "advanced", 6, 21, 0, 350,
   "Competitive 8v8 football with a high press.",
   "https://images.unsplash.com/photo-1526232761682-d26e03ac148e?auto=format&fit=crop&w=1000&q=80"),
)


def get_or_create_user(db, phone: str, name: str, position: str, skill: models.SkillLevel) -> models.User:
  user = db.scalar(select(models.User).where(models.User.phone_number == phone))
  if not user:
    user = models.User(phone_number=phone, display_name=name, city="Bengaluru", password_hash=hash_password(DEMO_PASSWORD))
    db.add(user)
    db.flush()
  else:
    user.display_name = name
    user.city = "Bengaluru"
    user.password_hash = hash_password(DEMO_PASSWORD)
  profile = db.scalar(select(models.SportProfile).where(models.SportProfile.user_id == user.id, models.SportProfile.sport == "football"))
  if not profile:
    db.add(models.SportProfile(user_id=user.id, sport="football", skill_level=skill, position=position))
  else:
    profile.skill_level = skill
    profile.position = position
  return user


def add_member(db, club: models.Club, user: models.User, owner: bool = False) -> None:
  membership = db.scalar(select(models.ClubMember).where(models.ClubMember.club_id == club.id, models.ClubMember.user_id == user.id))
  if not membership:
    db.add(
      models.ClubMember(
        club_id=club.id,
        user_id=user.id,
        role=models.MembershipRole.owner if owner else models.MembershipRole.player,
        status=models.MembershipStatus.active,
        joined_at=datetime.now(UTC),
      )
    )


def get_or_create_club(db, owner: models.User, name: str, area: str, turf: str, skill: models.SkillLevel) -> models.Club:
  club = db.scalar(select(models.Club).where(models.Club.name == name, models.Club.city == "Bengaluru"))
  if not club:
    club = models.Club(
      owner_id=owner.id,
      name=name,
      city="Bengaluru",
      area=area,
      home_turf=turf,
      description=f"A Bengaluru 8v8 football club based around {area}.",
      skill_level=skill,
      player_count=0,
      open_slots=0,
      availability="Weeknights after 8 PM",
      play_style="Balanced passing and quick transitions",
      rating=4.5,
      image_url="",
    )
    db.add(club)
    db.flush()
  add_member(db, club, owner, owner=True)
  return club


def seed_discovery_games(db) -> None:
  local_now = datetime.now(ZoneInfo("Asia/Kolkata"))
  positions = ["Goalkeeper", "Defender", "Defender", "Midfielder", "Midfielder", "Winger", "Striker"]

  for club_index, (name, area, venue, skill_value, days_ahead, hour, minute, cost, description, image_url) in enumerate(SAMPLE_GAMES):
    skill = models.SkillLevel(skill_value)
    phone_base = 919100000000 + club_index * 100
    owner = get_or_create_user(db, f"+{phone_base + 1}", f"{area} Captain", "Midfielder", skill)
    club = get_or_create_club(db, owner, name, area, venue, skill)
    club.description = description
    club.play_style = "Quick passing and organized 8v8 football"
    club.image_url = image_url
    roster = [owner]
    for index, position in enumerate(positions, start=2):
      player = get_or_create_user(db, f"+{phone_base + index}", f"{area} Player {index - 1}", position, skill)
      add_member(db, club, player)
      roster.append(player)

    db.flush()
    club.player_count = len(roster)
    existing = db.scalar(
      select(models.Game)
      .where(
        models.Game.club_id == club.id,
        models.Game.status == models.GameStatus.published,
        models.Game.scheduled_at > datetime.now(UTC),
      )
      .order_by(models.Game.scheduled_at.desc())
    )
    if existing:
      continue

    scheduled_at = (local_now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    game = models.Game(
      club_id=club.id,
      created_by=owner.id,
      venue=venue,
      venue_area=area,
      scheduled_at=scheduled_at,
      cost_per_person=cost,
      skill_level=skill,
      host_player_target=8,
      host_open_slots=0,
      status=models.GameStatus.published,
    )
    db.add(game)
    db.flush()
    db.add_all([
      models.GameParticipant(
        game_id=game.id,
        user_id=player.id,
        status=models.ParticipantStatus.accepted,
        responded_at=datetime.now(UTC),
      )
      for player in roster
    ])
    db.add(models.MatchCard(game_id=game.id, club_id=club.id, status=models.CardStatus.active))


def run() -> None:
  db = SessionLocal()
  try:
    data_owner = get_or_create_user(db, "+919000000001", "Arjun Mehta", "Midfielder", models.SkillLevel.intermediate)
    rivals_owner = get_or_create_user(db, "+919000000002", "Kiran Rao", "Defender", models.SkillLevel.intermediate)
    data_club = get_or_create_club(db, data_owner, "Indiranagar FC", "Indiranagar", "Indiranagar Turf", models.SkillLevel.intermediate)
    rivals_club = get_or_create_club(db, rivals_owner, "Koramangala United", "Koramangala", "Koramangala Sports Arena", models.SkillLevel.intermediate)

    positions = ["Goalkeeper", "Defender", "Defender", "Defender", "Midfielder", "Midfielder", "Winger", "Striker"]
    for index, position in enumerate(positions, start=3):
      player = get_or_create_user(db, f"+9190000000{index:02d}", f"Indiranagar Player {index - 2}", position, models.SkillLevel.intermediate)
      add_member(db, data_club, player)
    for index, position in enumerate(positions, start=11):
      player = get_or_create_user(db, f"+919000000{index:02d}", f"Koramangala Player {index - 10}", position, models.SkillLevel.intermediate)
      add_member(db, rivals_club, player)

    db.flush()
    for club in (data_club, rivals_club):
      club.player_count = int(
        db.scalar(
          select(func.count()).select_from(models.ClubMember).where(
            models.ClubMember.club_id == club.id, models.ClubMember.status == models.MembershipStatus.active
          )
        )
        or 0
      )
    seed_discovery_games(db)
    db.commit()
    print("Demo data ready.")
    print("Owner accounts: +919000000001 and +919000000002")
    print(f"Password: {DEMO_PASSWORD}")
  finally:
    db.close()


if __name__ == "__main__":
  run()
