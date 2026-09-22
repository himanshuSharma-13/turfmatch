from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import (
  CardStatus,
  ChallengeStatus,
  GameStatus,
  MembershipRole,
  MembershipStatus,
  ParticipantStatus,
  SkillLevel,
  SwipeDirection,
)


class UserRead(BaseModel):
  id: uuid.UUID
  phone_number: str
  display_name: str
  city: str
  is_captain: bool
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class SportProfileInput(BaseModel):
  skill_level: SkillLevel
  position: str = Field(default="Flexible", min_length=2, max_length=60)


class SportProfileRead(SportProfileInput):
  id: uuid.UUID
  sport: str

  model_config = ConfigDict(from_attributes=True)


class SignupInput(BaseModel):
  phone_number: str = Field(min_length=8, max_length=32)
  display_name: str = Field(min_length=2, max_length=120)
  password: str = Field(min_length=8, max_length=128)
  skill_level: SkillLevel = SkillLevel.casual
  position: str = Field(default="Flexible", min_length=2, max_length=60)


class LoginInput(BaseModel):
  phone_number: str = Field(min_length=8, max_length=32)
  password: str = Field(min_length=8, max_length=128)


class AuthRead(BaseModel):
  access_token: str
  token_type: str = "bearer"
  user: UserRead


class ClubCreate(BaseModel):
  name: str = Field(min_length=2, max_length=140)
  area: str = Field(min_length=2, max_length=160)
  home_turf: str = Field(min_length=2, max_length=160)
  description: str = Field(min_length=2, max_length=1000)
  skill_level: SkillLevel
  availability: str = Field(min_length=2, max_length=160)
  play_style: str = Field(min_length=2, max_length=240)


class ClubRead(ClubCreate):
  id: uuid.UUID
  owner_id: uuid.UUID
  city: str
  rating: float
  player_count: int
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)


class ClubMemberRead(BaseModel):
  id: uuid.UUID
  club_id: uuid.UUID
  user_id: uuid.UUID
  display_name: str
  phone_number: str
  role: MembershipRole
  status: MembershipStatus
  position: str | None = None
  skill_level: SkillLevel | None = None
  joined_at: datetime | None


class MembershipDecision(BaseModel):
  approve: bool


class GameCreate(BaseModel):
  venue: str = Field(min_length=2, max_length=160)
  venue_area: str = Field(min_length=2, max_length=160)
  scheduled_at: datetime
  cost_per_person: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
  skill_level: SkillLevel


class GameRead(BaseModel):
  id: uuid.UUID
  club_id: uuid.UUID
  club_name: str
  venue: str
  venue_area: str
  scheduled_at: datetime
  cost_per_person: Decimal
  skill_level: SkillLevel
  format: str
  host_player_target: int
  host_open_slots: int
  accepted_players: int
  pending_players: int
  status: GameStatus
  opponent_club_id: uuid.UUID | None
  opponent_club_name: str | None = None
  created_at: datetime


class InvitationInput(BaseModel):
  player_ids: list[uuid.UUID] = Field(min_length=1, max_length=20)


class ParticipantResponse(BaseModel):
  status: ParticipantStatus


class ParticipantRead(BaseModel):
  id: uuid.UUID
  game_id: uuid.UUID
  user_id: uuid.UUID
  display_name: str
  status: ParticipantStatus
  responded_at: datetime | None


class MatchCardRead(BaseModel):
  id: uuid.UUID
  game_id: uuid.UUID
  club_id: uuid.UUID
  club_name: str
  club_area: str
  club_skill_level: SkillLevel
  club_rating: float
  venue_area: str
  scheduled_at: datetime
  cost_per_person: Decimal
  skill_level: SkillLevel
  format: str
  status: CardStatus
  published_at: datetime


class SwipeInput(BaseModel):
  club_id: uuid.UUID
  direction: SwipeDirection


class ChallengeRead(BaseModel):
  id: uuid.UUID
  game_id: uuid.UUID
  match_card_id: uuid.UUID
  host_club_id: uuid.UUID
  host_club_name: str
  challenger_club_id: uuid.UUID
  challenger_club_name: str
  status: ChallengeStatus
  created_at: datetime
  confirmed_at: datetime | None
