from __future__ import annotations
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from . import Base, employment_type_enum, site_type_enum


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    vacancies: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # >= 0

    location: Mapped[str | None] = mapped_column(String, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(employment_type_enum, nullable=True)
    site: Mapped[str | None] = mapped_column(site_type_enum, nullable=True)

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EGP")

    company_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    company: Mapped["Company"] = relationship(back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # salary_max >= salary_min when both present; vacancies >= 0
        CheckConstraint("(salary_max IS NULL OR salary_min IS NULL OR salary_max >= salary_min)", name="ck_jobs_salary_bounds"),
        CheckConstraint("vacancies >= 0", name="ck_jobs_vacancies_nonnegative"),
        Index("ix_jobs_title", "title"),
        Index("ix_jobs_company_archived", "company_id", "is_archived"),
        Index("ix_jobs_loc_emp_site", "location", "employment_type", "site"),
        Index("ix_jobs_created_desc", "created_at", "id"),  # helps pagination + sorting
    )
