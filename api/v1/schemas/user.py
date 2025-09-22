from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    regular = "regular"
    recruiter = "recruiter"


class UserCreate(BaseModel):
    fname: str
    lname: Optional[str] = None
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = UserRole.regular


class UserUpdateMe(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)


class UserOut(BaseModel):
    id: UUID
    fname: str
    lname: Optional[str] = None
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
