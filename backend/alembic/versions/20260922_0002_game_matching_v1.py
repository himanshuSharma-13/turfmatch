"""Add TurfMatch V1 game, roster, and club matching model.

Revision ID: 20260922_0002
Revises: 20260812_0001
Create Date: 2026-09-22
"""

from collections.abc import Sequence
from typing import Optional, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260922_0002"
down_revision: Optional[str] = "20260812_0001"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


skill_level = postgresql.ENUM("beginner", "casual", "intermediate", "advanced", name="skilllevel", create_type=False)
membership_role = postgresql.ENUM("owner", "player", name="membershiprole", create_type=False)
membership_status = postgresql.ENUM("pending", "active", "removed", name="membershipstatus", create_type=False)
game_status = postgresql.ENUM("draft", "broadcasting", "roster_filled", "published", "matched", "completed", "cancelled", name="gamestatus", create_type=False)
participant_status = postgresql.ENUM("pending", "accepted", "rejected", name="participantstatus", create_type=False)
card_status = postgresql.ENUM("active", "matched", "expired", "cancelled", name="cardstatus", create_type=False)
swipe_direction = postgresql.ENUM("like", "pass", name="swipedirection", create_type=False)
challenge_status = postgresql.ENUM("pending", "confirmed", "rejected", "cancelled", "completed", name="challengestatus", create_type=False)


def upgrade() -> None:
  bind = op.get_bind()
  op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
  op.execute("ALTER TYPE skilllevel ADD VALUE IF NOT EXISTS 'beginner'")
  op.execute("ALTER TYPE skilllevel ADD VALUE IF NOT EXISTS 'advanced'")
  for enum in (membership_role, membership_status, game_status, participant_status, card_status, swipe_direction, challenge_status):
    enum.create(bind, checkfirst=True)

  op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))
  op.add_column("clubs", sa.Column("city", sa.String(length=120), server_default="Bengaluru", nullable=False))
  op.alter_column("clubs", "city", server_default=None)

  op.create_table(
    "sport_profiles",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("user_id", sa.Uuid(), nullable=False),
    sa.Column("sport", sa.String(length=40), server_default="football", nullable=False),
    sa.Column("skill_level", skill_level, nullable=False),
    sa.Column("position", sa.String(length=60), server_default="Flexible", nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("user_id", "sport", name="uq_sport_profile_user_sport"),
  )
  op.create_table(
    "club_members",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("club_id", sa.Uuid(), nullable=False),
    sa.Column("user_id", sa.Uuid(), nullable=False),
    sa.Column("role", membership_role, server_default="player", nullable=False),
    sa.Column("status", membership_status, server_default="pending", nullable=False),
    sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("club_id", "user_id", name="uq_club_member"),
  )
  op.create_table(
    "games",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("club_id", sa.Uuid(), nullable=False),
    sa.Column("created_by", sa.Uuid(), nullable=False),
    sa.Column("sport", sa.String(length=40), server_default="football", nullable=False),
    sa.Column("format", sa.String(length=20), server_default="8v8", nullable=False),
    sa.Column("venue", sa.String(length=160), nullable=False),
    sa.Column("venue_area", sa.String(length=160), nullable=False),
    sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("cost_per_person", sa.Numeric(10, 2), server_default="0", nullable=False),
    sa.Column("skill_level", skill_level, nullable=False),
    sa.Column("host_player_target", sa.Integer(), server_default="8", nullable=False),
    sa.Column("host_open_slots", sa.Integer(), server_default="8", nullable=False),
    sa.Column("opponent_club_id", sa.Uuid(), nullable=True),
    sa.Column("status", game_status, server_default="draft", nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["opponent_club_id"], ["clubs.id"], ondelete="SET NULL"),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_table(
    "game_participants",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("game_id", sa.Uuid(), nullable=False),
    sa.Column("user_id", sa.Uuid(), nullable=False),
    sa.Column("status", participant_status, server_default="pending", nullable=False),
    sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("game_id", "user_id", name="uq_game_participant"),
  )
  op.create_table(
    "match_cards",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("game_id", sa.Uuid(), nullable=False),
    sa.Column("club_id", sa.Uuid(), nullable=False),
    sa.Column("status", card_status, server_default="active", nullable=False),
    sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("game_id"),
  )
  op.create_table(
    "swipes",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("match_card_id", sa.Uuid(), nullable=False),
    sa.Column("swiping_club_id", sa.Uuid(), nullable=False),
    sa.Column("swiping_owner_id", sa.Uuid(), nullable=False),
    sa.Column("direction", swipe_direction, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(["match_card_id"], ["match_cards.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["swiping_club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["swiping_owner_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("match_card_id", "swiping_club_id", name="uq_card_club_swipe"),
  )
  op.create_table(
    "challenges",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("match_card_id", sa.Uuid(), nullable=False),
    sa.Column("game_id", sa.Uuid(), nullable=False),
    sa.Column("host_club_id", sa.Uuid(), nullable=False),
    sa.Column("challenger_club_id", sa.Uuid(), nullable=False),
    sa.Column("challenger_owner_id", sa.Uuid(), nullable=False),
    sa.Column("status", challenge_status, server_default="pending", nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(["match_card_id"], ["match_cards.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["host_club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["challenger_club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["challenger_owner_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("match_card_id", "challenger_club_id", name="uq_challenge_card_club"),
  )

  op.execute("UPDATE users SET city = 'Bengaluru'")
  op.execute("UPDATE clubs SET city = 'Bengaluru'")
  op.execute("""
    INSERT INTO club_members (id, club_id, user_id, role, status, joined_at)
    SELECT gen_random_uuid(), id, captain_id, 'owner', 'active', NOW() FROM clubs
    ON CONFLICT (club_id, user_id) DO NOTHING
  """)


def downgrade() -> None:
  op.drop_table("challenges")
  op.drop_table("swipes")
  op.drop_table("match_cards")
  op.drop_table("game_participants")
  op.drop_table("games")
  op.drop_table("club_members")
  op.drop_table("sport_profiles")
  op.drop_column("clubs", "city")
  op.drop_column("users", "password_hash")
