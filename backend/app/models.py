from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SkillLevel(str, enum.Enum):
  casual = "casual"
  intermediate = "intermediate"


class MatchStatus(str, enum.Enum):
  pending = "pending"
  accepted = "accepted"
  rejected = "rejected"
  completed = "completed"


class User(Base):
  __tablename__ = "users"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  phone_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
  display_name: Mapped[str] = mapped_column(String(120), nullable=False)
  city: Mapped[str] = mapped_column(String(120), default="Mumbai", nullable=False)
  is_captain: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )

  clubs: Mapped[list["Club"]] = relationship(back_populates="captain")


class Club(Base):
  __tablename__ = "clubs"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  captain_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
  name: Mapped[str] = mapped_column(String(140), nullable=False)
  area: Mapped[str] = mapped_column(String(160), nullable=False)
  home_turf: Mapped[str] = mapped_column(String(160), nullable=False)
  description: Mapped[str] = mapped_column(Text, nullable=False)
  skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), nullable=False)
  player_count: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
  open_slots: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
  availability: Mapped[str] = mapped_column(String(160), nullable=False)
  play_style: Mapped[str] = mapped_column(String(240), nullable=False)
  rating: Mapped[float] = mapped_column(Float, default=0, nullable=False)
  image_url: Mapped[str] = mapped_column(Text, nullable=False)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )

  captain: Mapped[User] = relationship(back_populates="clubs")
  home_matches: Mapped[list["ClubMatch"]] = relationship(
    back_populates="home_club", foreign_keys="ClubMatch.home_club_id"
  )
  away_matches: Mapped[list["ClubMatch"]] = relationship(
    back_populates="away_club", foreign_keys="ClubMatch.away_club_id"
  )


class ClubMatch(Base):
  __tablename__ = "club_matches"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  home_club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"))
  away_club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"))
  status: Mapped[MatchStatus] = mapped_column(
    Enum(MatchStatus), default=MatchStatus.pending, nullable=False
  )
  scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
  venue: Mapped[str] = mapped_column(String(160), nullable=False)
  message: Mapped[str] = mapped_column(Text, nullable=False)
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )

  home_club: Mapped[Club] = relationship(back_populates="home_matches", foreign_keys=[home_club_id])
  away_club: Mapped[Club] = relationship(back_populates="away_matches", foreign_keys=[away_club_id])
