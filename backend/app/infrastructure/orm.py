"""SQLAlchemy ORM models mapping domain entities to database tables."""

from datetime import datetime, timezone
from typing import List
from uuid import UUID as UUID_t
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


group_members = Table(
    "group_members",
    Base.metadata,
    Column(
        "group_id",
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class UserORM(Base):
    """ORM mapping for the users table."""

    __tablename__ = "users"

    id: Mapped[UUID_t] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    groups: Mapped[List["GroupORM"]] = relationship(
        secondary=group_members,
        back_populates="members",
        lazy="selectin",
    )


class GroupORM(Base):
    """ORM mapping for the groups table."""

    __tablename__ = "groups"

    id: Mapped[UUID_t] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    members: Mapped[List[UserORM]] = relationship(
        secondary=group_members,
        back_populates="groups",
        lazy="selectin",
    )


class ExpenseORM(Base):
    """ORM mapping for the expenses table."""

    __tablename__ = "expenses"

    id: Mapped[UUID_t] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    group_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    payer_id = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
