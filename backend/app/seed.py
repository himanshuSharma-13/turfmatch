from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select

from app import models
from app.auth import hash_password
from app.db.session import SessionLocal

DEMO_PASSWORD = "turfmatch123"


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
    db.commit()
    print("Demo data ready.")
    print("Owner accounts: +919000000001 and +919000000002")
    print(f"Password: {DEMO_PASSWORD}")
  finally:
    db.close()


if __name__ == "__main__":
  run()
