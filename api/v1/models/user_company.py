from __future__ import annotations
from uuid import UUID
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from . import Base


class UserCompany(Base):
    __tablename__ = "users_companies"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "company_id", name="pk_users_companies"),
    )
