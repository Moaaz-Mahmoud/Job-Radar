from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from api.db import get_async_session
from api.v1.schemas.auth import SignupIn, SignupOut, VerifyEmailIn, VerifyEmailOut
from api.v1.services.auth_service import AuthService, EmailOrUsernameTaken, WeakPassword, InvalidOrExpiredToken
from api.v1.services.email_sender import (
    ConsoleEmailSender,
    BrevoEmailSender,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def get_mailer():
    provider = os.getenv("MAIL_PROVIDER", "console").lower()
    
    if provider == "brevo":
        return BrevoEmailSender()
    
    return ConsoleEmailSender()


def get_auth_service(session: AsyncSession = Depends(get_async_session), mailer=Depends(get_mailer)) -> AuthService:
    return AuthService(session, mailer)


@router.post("/signup", response_model=SignupOut)
async def signup(payload: SignupIn, svc: AuthService = Depends(get_auth_service)):
    try:
        return await svc.signup(**payload.model_dump())
    except WeakPassword as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EmailOrUsernameTaken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email or username already in use")


@router.post("/verify-email", response_model=VerifyEmailOut)
async def verify_email(payload: VerifyEmailIn, svc: AuthService = Depends(get_auth_service)):
    try:
        return await svc.verify_email(**payload.model_dump())
    except InvalidOrExpiredToken:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token")

@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email_link(email: str, token: str, svc: AuthService = Depends(get_auth_service)):
    try:
        await svc.verify_email_from_link(email=email, token=token)
        # Tiny HTML page so browser clicks look nice
        return HTMLResponse(
            "<h2>Email verified ✅</h2><p>You can close this tab and return to the app.</p>",
            status_code=200,
        )
    except InvalidOrExpiredToken:
        return HTMLResponse(
            "<h2>Verification failed ❌</h2><p>The link is invalid or expired.</p>",
            status_code=400,
        )
