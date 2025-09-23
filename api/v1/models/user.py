from __future__ import annotations
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from . import Base, user_role_enum, UserRole
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    fname: Mapped[str] = mapped_column(String, nullable=False)
    lname: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[UserRole] = mapped_column(user_role_enum, nullable=False, default=UserRole.regular)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # relationships
    applications: Mapped[list["Application"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    companies: Mapped[list["Company"]] = relationship(
        secondary="users_companies", back_populates="members"
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
