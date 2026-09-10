from __future__ import annotations

"""Simplify schema to clubs and club-vs-club matches.

Revision ID: 20260812_0001
Revises:
Create Date: 2026-08-12
"""

from collections.abc import Sequence
from typing import Optional, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260812_0001"
down_revision: Optional[str] = None
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


skill_level = postgresql.ENUM(
  "casual",
  "intermediate",
  name="skilllevel",
  create_type=False,
)
match_status = postgresql.ENUM(
  "pending",
  "accepted",
  "rejected",
  "completed",
  name="matchstatus",
  create_type=False,
)


def upgrade() -> None:
  postgresql.ENUM(
    "casual",
    "intermediate",
    name="skilllevel",
  ).create(op.get_bind(), checkfirst=True)
  postgresql.ENUM("pending", "accepted", "rejected", "completed", name="matchstatus").create(
    op.get_bind(), checkfirst=True
  )

  op.create_table(
    "users",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("phone_number", sa.String(length=32), nullable=False),
    sa.Column("display_name", sa.String(length=120), nullable=False),
    sa.Column("city", sa.String(length=120), nullable=False),
    sa.Column("is_captain", sa.Boolean(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.UniqueConstraint("phone_number"),
  )
  op.create_table(
    "clubs",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("captain_id", sa.Uuid(), nullable=False),
    sa.Column("name", sa.String(length=140), nullable=False),
    sa.Column("area", sa.String(length=160), nullable=False),
    sa.Column("home_turf", sa.String(length=160), nullable=False),
    sa.Column("description", sa.Text(), nullable=False),
    sa.Column("skill_level", skill_level, nullable=False),
    sa.Column("player_count", sa.Integer(), nullable=False),
    sa.Column("open_slots", sa.Integer(), nullable=False),
    sa.Column("availability", sa.String(length=160), nullable=False),
    sa.Column("play_style", sa.String(length=240), nullable=False),
    sa.Column("rating", sa.Float(), nullable=False),
    sa.Column("image_url", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(["captain_id"], ["users.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
  )
  op.create_table(
    "club_matches",
    sa.Column("id", sa.Uuid(), nullable=False),
    sa.Column("home_club_id", sa.Uuid(), nullable=False),
    sa.Column("away_club_id", sa.Uuid(), nullable=False),
    sa.Column("status", match_status, nullable=False),
    sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("venue", sa.String(length=160), nullable=False),
    sa.Column("message", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(["home_club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(["away_club_id"], ["clubs.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
  )


def downgrade() -> None:
  op.drop_table("club_matches")
  op.drop_table("clubs")
  op.drop_table("users")
  match_status.drop(op.get_bind(), checkfirst=True)
  skill_level.drop(op.get_bind(), checkfirst=True)
