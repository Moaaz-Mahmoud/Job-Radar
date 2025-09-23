from __future__ import annotations
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from . import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # relationships
    jobs: Mapped[list["Job"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    members: Mapped[list["User"]] = relationship(
        secondary="users_companies", back_populates="companies"
    )
