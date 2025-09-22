from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, AnyUrl
from enum import Enum
from api.v1.schemas.pagination import PageEnvelope


class ApplicationStatus(str, Enum):
    submitted = "submitted"
    canceled = "canceled"
    received = "received"
    advanced = "advanced"
    rejected = "rejected"


class StatusAction(str, Enum):
    receive = "receive"
    advance = "advance"
    reject = "reject"


class ApplicationCreate(BaseModel):
    cv_url: AnyUrl
    cover_letter: Optional[str] = None


class ApplicationUpdate(BaseModel):
    cv_url: Optional[AnyUrl] = None
    cover_letter: Optional[str] = None


class ApplicationStatusChange(BaseModel):
    action: StatusAction


class ApplicationOut(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    cv_url: AnyUrl
    cover_letter: Optional[str] = None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime


ApplicationsPage = PageEnvelope[ApplicationOut]
