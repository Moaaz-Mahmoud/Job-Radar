from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class CompanyCreate(BaseModel):
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None


class CompanyOut(BaseModel):
    id: UUID
    name: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CompanyMemberAdd(BaseModel):
    user_id: UUID


class CompanyMemberOut(BaseModel):
    user_id: UUID
    company_id: UUID
