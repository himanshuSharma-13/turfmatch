from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.session import get_db

router = APIRouter()


def get_mock_user(db: Session) -> models.User:
  user = db.scalar(select(models.User).where(models.User.phone_number == "+919999999999"))
  if user:
    return user

  user = models.User(
    phone_number="+919999999999",
    display_name="Demo Captain",
    city="Banglore",
    is_captain=True,
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


@router.get("/health")
def health() -> dict[str, str]:
  return {"status": "ok"}


@router.get("/me", response_model=schemas.UserRead)
def read_me(db: Session = Depends(get_db)) -> models.User:
  return get_mock_user(db)


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
  existing = db.scalar(select(models.User).where(models.User.phone_number == payload.phone_number))
  if existing:
    raise HTTPException(status_code=409, detail="Phone number already exists")

  user = models.User(**payload.model_dump())
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


@router.get("/clubs", response_model=list[schemas.ClubRead])
def list_clubs(
  skill_level: Optional[models.SkillLevel] = None, db: Session = Depends(get_db)
) -> list[models.Club]:
  query = select(models.Club)
  if skill_level:
    query = query.where(models.Club.skill_level == skill_level)
  return list(db.scalars(query.order_by(models.Club.rating.desc(), models.Club.player_count.desc())))


@router.post("/clubs", response_model=schemas.ClubRead, status_code=status.HTTP_201_CREATED)
def create_club(payload: schemas.ClubCreate, db: Session = Depends(get_db)) -> models.Club:
  user = get_mock_user(db)
  club = models.Club(captain_id=user.id, **payload.model_dump())
  db.add(club)
  db.commit()
  db.refresh(club)
  return club


@router.get("/matches", response_model=list[schemas.MatchRead])
def list_matches(db: Session = Depends(get_db)) -> list[models.ClubMatch]:
  return list(db.scalars(select(models.ClubMatch).order_by(models.ClubMatch.created_at.desc())))


@router.post("/matches", response_model=schemas.MatchRead, status_code=status.HTTP_201_CREATED)
def create_match(payload: schemas.MatchCreate, db: Session = Depends(get_db)) -> models.ClubMatch:
  if payload.home_club_id == payload.away_club_id:
    raise HTTPException(status_code=400, detail="A club cannot play itself")

  home_club = db.get(models.Club, payload.home_club_id)
  away_club = db.get(models.Club, payload.away_club_id)
  if not home_club or not away_club:
    raise HTTPException(status_code=404, detail="Club not found")

  match = models.ClubMatch(**payload.model_dump())
  db.add(match)
  db.commit()
  db.refresh(match)
  return match


@router.patch("/matches/{match_id}", response_model=schemas.MatchRead)
def update_match_status(
  match_id: uuid.UUID, payload: schemas.MatchStatusUpdate, db: Session = Depends(get_db)
) -> models.ClubMatch:
  match = db.get(models.ClubMatch, match_id)
  if not match:
    raise HTTPException(status_code=404, detail="Match not found")

  match.status = payload.status
  db.commit()
  db.refresh(match)
  return match
