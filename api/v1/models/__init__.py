# SQLAlchemy 2.0 base + project-wide enums (DB enums live here)
from __future__ import annotations
from enum import Enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import ENUM


class Base(DeclarativeBase):
    pass


class ApplicationStatus(str, Enum):
    submitted = "submitted"
    canceled  = "canceled"
    received  = "received"
    advanced  = "advanced"
    rejected  = "rejected"


class UserRole(str, Enum):
    regular   = "regular"
    recruiter = "recruiter"


class SiteType(str, Enum):
    on_site = "on_site"
    hybrid  = "hybrid"
    remote  = "remote"


class EmploymentType(str, Enum):
    full_time  = "full_time"
    part_time  = "part_time"
    contract   = "contract"
    internship = "internship"


application_status_enum = ENUM(
    *[e.value for e in ApplicationStatus], name="application_status", native_enum=True
)
user_role_enum = ENUM(
    *[e.value for e in UserRole], name="user_role", native_enum=True
)
site_type_enum = ENUM(
    *[e.value for e in SiteType], name="site_type", native_enum=True
)
employment_type_enum = ENUM(
    *[e.value for e in EmploymentType], name="employment_type", native_enum=True
)


__all__ = [
    "Base",
    "ApplicationStatus", "UserRole", "SiteType", "EmploymentType",
    "application_status_enum", "user_role_enum", "site_type_enum", "employment_type_enum",
]
