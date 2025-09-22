from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from enum import Enum
from datetime import datetime
from api.v1.schemas.pagination import PageEnvelope


class EmploymentType(str, Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    internship = "internship"


class SiteType(str, Enum):
    on_site = "on_site"
    hybrid = "hybrid"
    remote = "remote"


def ensure_salary_bounds(smin: int | None, smax: int | None) -> None:
    if smin is not None and smax is not None and smax < smin:
        raise ValueError("salary_max must be >= salary_min")


class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None
    vacancies: int = Field(ge=0, default=1)
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    site: Optional[SiteType] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    salary_currency: str = Field(default="EGP", min_length=3, max_length=3)
    company_id: UUID
    tags: Optional[List[str]] = None

    @model_validator(mode="after")
    def _validate(self):
        ensure_salary_bounds(self.salary_min, self.salary_max)
        return self


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    vacancies: Optional[int] = Field(default=None, ge=0)
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    site: Optional[SiteType] = None
    salary_min: Optional[int] = Field(default=None, ge=0)
    salary_max: Optional[int] = Field(default=None, ge=0)
    salary_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    tags: Optional[List[str]] = None

    @model_validator(mode="after")
    def _validate(self):
        ensure_salary_bounds(self.salary_min, self.salary_max)
        return self


class JobOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    is_archived: bool
    vacancies: int
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    site: Optional[SiteType] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str
    company_id: UUID
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


JobsPage = PageEnvelope[JobOut]
