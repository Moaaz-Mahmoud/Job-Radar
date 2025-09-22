from pydantic import BaseModel, EmailStr


class SignupIn(BaseModel):
    email: EmailStr
    username: str
    password: str
    fname: str
    lname: str | None = None


class VerifyEmailIn(BaseModel):
    token: str


class LoginEmailIn(BaseModel):
    email: EmailStr
    password: str


class LoginUsernameIn(BaseModel):  # fixed typo
    username: str
    password: str


# For /auth/login and /auth/refresh
class TokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# For /auth/refresh
class RefreshIn(BaseModel):
    refresh_token: str
