from sqlalchemy import select

from app import models
from app.db.session import SessionLocal

IMAGE_ONE = "https://images.unsplash.com/photo-1551958219-acbc608c6377?auto=format&fit=crop&w=900&q=80"
IMAGE_TWO = "https://images.unsplash.com/photo-1526232761682-d26e03ac148e?auto=format&fit=crop&w=900&q=80"
IMAGE_THREE = "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=900&q=80"


def run() -> None:
  db = SessionLocal()
  try:
    if db.scalar(select(models.Club)):
      print("Seed data already exists.")
      return

    captain_one = models.User(
      phone_number="+919999999999",
      display_name="Demo Captain",
      city="Banglore",
      is_captain=True,
    )
    captain_two = models.User(
      phone_number="+918888888888",
      display_name="Rival Captain",
      city="Bengaluru",
      is_captain=True,
    )
    db.add_all([captain_one, captain_two])
    db.flush()

    home_club = models.Club(
      captain_id=captain_one.id,
      name="Data FC",
      area="Andheri West",
      home_turf="Arena 52",
      description="A compact club side with a balanced midfield and quick passing game.",
      skill_level=models.SkillLevel.intermediate,
      player_count=10,
      open_slots=2,
      availability="Weeknights after 8 PM",
      play_style="Passing-heavy, compact shape, quick counters",
      rating=4.4,
      image_url=IMAGE_TWO,
    )
    away_club = models.Club(
      captain_id=captain_two.id,
      name="Juhu Strikers",
      area="Juhu",
      home_turf="Juhu Turf Park",
      description="Fast, aggressive club team looking for a strong turf fixture this week.",
      skill_level=models.SkillLevel.casual,
      player_count=8,
      open_slots=1,
      availability="Tomorrow, 8:30 PM",
      play_style="High press, direct attacks, strong tackles",
      rating=4.8,
      image_url=IMAGE_ONE,
    )
    db.add_all([home_club, away_club])
    db.flush()

    db.add(
      models.ClubMatch(
        home_club_id=home_club.id,
        away_club_id=away_club.id,
        status=models.MatchStatus.pending,
        venue="Andheri Turf Arena",
        message="Looking for a competitive club-vs-club fixture this week.",
      )
    )
    db.commit()
    print("Seed data inserted.")
  finally:
    db.close()


if __name__ == "__main__":
  run()
