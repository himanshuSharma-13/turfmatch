from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import MatchStatus, SkillLevel


class UserCreate(BaseModel):
  phone_number: str = Field(min_length=8, max_length=32)
  display_name: str = Field(min_length=2, max_length=120)
  city: str = "Mumbai"
  is_captain: bool = True


class UserRead(UserCreate):
  id: uuid.UUID
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class ClubCreate(BaseModel):
  name: str = Field(min_length=2, max_length=140)
  area: str = Field(min_length=2, max_length=160)
  home_turf: str = Field(min_length=2, max_length=160)
  description: str = Field(min_length=2)
  skill_level: SkillLevel
  player_count: int = Field(default=10, ge=1, le=20)
  open_slots: int = Field(default=2, ge=0, le=20)
  availability: str = Field(min_length=2, max_length=160)
  play_style: str = Field(min_length=2, max_length=240)
  image_url: str


class ClubRead(ClubCreate):
  id: uuid.UUID
  captain_id: uuid.UUID
  rating: float
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class MatchCreate(BaseModel):
  home_club_id: uuid.UUID
  away_club_id: uuid.UUID
  venue: str = Field(min_length=2, max_length=160)
  scheduled_at: Optional[datetime] = None
  message: str = Field(min_length=2)


class MatchRead(MatchCreate):
  id: uuid.UUID
  status: MatchStatus
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class MatchStatusUpdate(BaseModel):
  status: MatchStatus
