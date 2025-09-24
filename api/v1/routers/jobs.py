from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/jobs")
