from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SkillLevel(str, enum.Enum):
  beginner = "beginner"
  casual = "casual"
  intermediate = "intermediate"
  advanced = "advanced"


class MembershipRole(str, enum.Enum):
  owner = "owner"
  player = "player"


class MembershipStatus(str, enum.Enum):
  pending = "pending"
  active = "active"
  removed = "removed"


class GameStatus(str, enum.Enum):
  draft = "draft"
  broadcasting = "broadcasting"
  roster_filled = "roster_filled"
  published = "published"
  matched = "matched"
  completed = "completed"
  cancelled = "cancelled"


class ParticipantStatus(str, enum.Enum):
  pending = "pending"
  accepted = "accepted"
  rejected = "rejected"


class CardStatus(str, enum.Enum):
  active = "active"
  matched = "matched"
  expired = "expired"
  cancelled = "cancelled"


class SwipeDirection(str, enum.Enum):
  like = "like"
  pass_ = "pass"


class ChallengeStatus(str, enum.Enum):
  pending = "pending"
  confirmed = "confirmed"
  rejected = "rejected"
  cancelled = "cancelled"
  completed = "completed"


class User(Base):
  __tablename__ = "users"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  phone_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
  display_name: Mapped[str] = mapped_column(String(120), nullable=False)
  city: Mapped[str] = mapped_column(String(120), default="Bengaluru", nullable=False)
  is_captain: Mapped[bool] = mapped_column(default=False, nullable=False)
  password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  sport_profiles: Mapped[list["SportProfile"]] = relationship(back_populates="user", cascade="all, delete-orphan")
  club_memberships: Mapped[list["ClubMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
  owned_clubs: Mapped[list["Club"]] = relationship(back_populates="owner", foreign_keys="Club.owner_id")
  game_participations: Mapped[list["GameParticipant"]] = relationship(back_populates="user")


class SportProfile(Base):
  __tablename__ = "sport_profiles"
  __table_args__ = (UniqueConstraint("user_id", "sport", name="uq_sport_profile_user_sport"),)

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  sport: Mapped[str] = mapped_column(String(40), default="football", nullable=False)
  skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel, name="skilllevel", create_type=False), nullable=False)
  position: Mapped[str] = mapped_column(String(60), default="Flexible", nullable=False)

  user: Mapped[User] = relationship(back_populates="sport_profiles")


class Club(Base):
  __tablename__ = "clubs"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  # The initial migration named this column captain_id; keep the physical column for compatibility.
  owner_id: Mapped[uuid.UUID] = mapped_column("captain_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  name: Mapped[str] = mapped_column(String(140), nullable=False)
  city: Mapped[str] = mapped_column(String(120), default="Bengaluru", nullable=False)
  area: Mapped[str] = mapped_column(String(160), nullable=False)
  home_turf: Mapped[str] = mapped_column(String(160), nullable=False)
  description: Mapped[str] = mapped_column(Text, nullable=False)
  skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel, name="skilllevel", create_type=False), nullable=False)
  player_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  open_slots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  availability: Mapped[str] = mapped_column(String(160), nullable=False)
  play_style: Mapped[str] = mapped_column(String(240), nullable=False)
  rating: Mapped[float] = mapped_column(default=0, nullable=False)
  image_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  owner: Mapped[User] = relationship(back_populates="owned_clubs", foreign_keys=[owner_id])
  members: Mapped[list["ClubMember"]] = relationship(back_populates="club", cascade="all, delete-orphan")
  games: Mapped[list["Game"]] = relationship(back_populates="host_club", foreign_keys="Game.club_id")


class ClubMember(Base):
  __tablename__ = "club_members"
  __table_args__ = (UniqueConstraint("club_id", "user_id", name="uq_club_member"),)

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
  user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole, name="membershiprole"), default=MembershipRole.player, nullable=False)
  status: Mapped[MembershipStatus] = mapped_column(Enum(MembershipStatus, name="membershipstatus"), default=MembershipStatus.pending, nullable=False)
  joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  club: Mapped[Club] = relationship(back_populates="members")
  user: Mapped[User] = relationship(back_populates="club_memberships")


class Game(Base):
  __tablename__ = "games"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
  created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  sport: Mapped[str] = mapped_column(String(40), default="football", nullable=False)
  format: Mapped[str] = mapped_column(String(20), default="8v8", nullable=False)
  venue: Mapped[str] = mapped_column(String(160), nullable=False)
  venue_area: Mapped[str] = mapped_column(String(160), nullable=False)
  scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  cost_per_person: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
  skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel, name="skilllevel", create_type=False), nullable=False)
  host_player_target: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
  host_open_slots: Mapped[int] = mapped_column(Integer, default=8, nullable=False)
  opponent_club_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
  status: Mapped[GameStatus] = mapped_column(Enum(GameStatus, name="gamestatus"), default=GameStatus.draft, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

  host_club: Mapped[Club] = relationship(back_populates="games", foreign_keys=[club_id])
  participants: Mapped[list["GameParticipant"]] = relationship(back_populates="game", cascade="all, delete-orphan")
  match_card: Mapped["MatchCard | None"] = relationship(back_populates="game", uselist=False, cascade="all, delete-orphan")


class GameParticipant(Base):
  __tablename__ = "game_participants"
  __table_args__ = (UniqueConstraint("game_id", "user_id", name="uq_game_participant"),)

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
  user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  status: Mapped[ParticipantStatus] = mapped_column(Enum(ParticipantStatus, name="participantstatus"), default=ParticipantStatus.pending, nullable=False)
  responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

  game: Mapped[Game] = relationship(back_populates="participants")
  user: Mapped[User] = relationship(back_populates="game_participations")


class MatchCard(Base):
  __tablename__ = "match_cards"

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), unique=True, nullable=False)
  club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
  status: Mapped[CardStatus] = mapped_column(Enum(CardStatus, name="cardstatus"), default=CardStatus.active, nullable=False)
  published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  game: Mapped[Game] = relationship(back_populates="match_card")


class Swipe(Base):
  __tablename__ = "swipes"
  __table_args__ = (UniqueConstraint("match_card_id", "swiping_club_id", name="uq_card_club_swipe"),)

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  match_card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("match_cards.id", ondelete="CASCADE"), nullable=False)
  swiping_club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
  swiping_owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  direction: Mapped[SwipeDirection] = mapped_column(Enum(SwipeDirection, name="swipedirection"), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Challenge(Base):
  __tablename__ = "challenges"
  __table_args__ = (UniqueConstraint("match_card_id", "challenger_club_id", name="uq_challenge_card_club"),)

  id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
  match_card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("match_cards.id", ondelete="CASCADE"), nullable=False)
  game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
  host_club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
  challenger_club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
  challenger_owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  status: Mapped[ChallengeStatus] = mapped_column(Enum(ChallengeStatus, name="challengestatus"), default=ChallengeStatus.pending, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
