from __future__ import annotations
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from . import Base, application_status_enum, ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[UUID]  = mapped_column(PG_UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"),  nullable=False)

    cv_url: Mapped[str] = mapped_column(String, nullable=False)
    cover_letter: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(application_status_enum, nullable=False, default=ApplicationStatus.submitted)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="applications")
    job:  Mapped["Job"]  = relationship(back_populates="applications")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),
        Index("ix_applications_job_status", "job_id", "status"),
        Index("ix_applications_created_desc", "created_at", "id"),
    )
