# api/v1/services/auth_service.py
from datetime import datetime, timezone
from sqlalchemy import select, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.models.refresh_token import RefreshToken
from api.v1.models.user import User
from api.v1.models.email_verification_token import EmailVerificationToken
from api.v1.schemas.auth import SignupOut, VerifyEmailOut
from api.v1.security.jwt import create_access_token
from api.v1.security.passwords import hash_password, verify_password
from api.v1.security.tokens import generate_raw_token, hash_token, expiry_in
from .email_sender import EmailSender


MIN_PASSWORD_LENGTH = 8
EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS = 24
REFRESH_TOKEN_EXPIRY_DAYS = 30


class EmailOrUsernameTaken(Exception): ...
class WeakPassword(Exception): ...
class InvalidOrExpiredToken(Exception): ...
class EmailNotVerified(Exception): ...
class InvalidCredentials(Exception): ...
class RefreshTokenInvalid(Exception): ...


class AuthService:
    def __init__(self, session: AsyncSession, mailer: EmailSender):
        self._session = session
        self._mailer = mailer

    async def signup(self, *, email: str, username: str, password: str, fname: str, lname: str | None) -> SignupOut:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise WeakPassword("password too short")

        session = self._session

        # Uniqueness check (DB constraints remain the source of truth)
        exists = await session.execute(
            select(User.id).where(or_(User.email == email, User.username == username))
        )
        if exists.scalar_one_or_none():
            raise EmailOrUsernameTaken()

        now = datetime.now(timezone.utc)
        user = User(
            email=email,
            username=username,
            fname=fname,
            lname=lname,
            hashed_password=hash_password(password),
            created_at=now,
            updated_at=now,
            # email_verified_at stays NULL
        )
        session.add(user)
        await session.flush()  # obtain user.id

        # Rotate any existing token (enforced by unique constraint on user_id)
        await session.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user.id, EmailVerificationToken.used_at.is_(None))
            .values(used_at=now)
        )

        # Create new token
        raw = generate_raw_token()
        rec = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw),
            expires_at=expiry_in(EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS),
            created_at=now,
        )
        session.add(rec)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise EmailOrUsernameTaken()

        # Send email (non-blocking patterns can come later; keep simple now)
        await self._mailer.send_verification(to_email=email, token=raw)
        return SignupOut()

    async def verify_email(self, *, email: str, token: str) -> VerifyEmailOut:
        session = self._session
        th = hash_token(token)
        now = datetime.now(timezone.utc)

        # Fetch user + token
        q_user = await session.execute(select(User).where(User.email == email))
        user = q_user.scalar_one_or_none()

        if not user:
            # avoid leaking whether email exists—use generic error
            raise InvalidOrExpiredToken()

        q_tok = await session.execute(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user.id, EmailVerificationToken.token_hash == th)
        )
        rec = q_tok.scalar_one_or_none()

        if not rec or rec.used_at is not None or rec.expires_at <= now:
            raise InvalidOrExpiredToken()

        rec.used_at = now
        user.email_verified_at = now
        user.updated_at = now
        await session.commit()
        return VerifyEmailOut()

    async def verify_email_from_link(self, *, email: str, token: str) -> dict:
        """
        Verifies using the email+token pair from a clicked link.
        - Ensures the token exists, unused, unexpired.
        - Ensures the token belongs to the user with the given email.
        - Marks token as used and user as verified.
        """
        session = self._session
        if session is None:
            raise RuntimeError("Session not provided")

        now = datetime.now(timezone.utc)
        th = hash_token(token)

        # fetch token
        q = await session.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == th)
        )
        rec = q.scalar_one_or_none()
        if not rec or rec.used_at is not None or rec.expires_at <= now:
            raise InvalidOrExpiredToken()

        # cross-check email ownership
        user = await session.get(User, rec.user_id)
        if not user or user.email.lower() != email.lower():
            raise InvalidOrExpiredToken()

        # mark used + verify user
        rec.used_at = now
        user.email_verified_at = now
        user.updated_at = now
        await session.commit()
        return {"message": "email verified"}

    # ---------- LOGIN ----------
    async def login(self, *, email_or_username: str, password: str):
        session = self._session
        if session is None:
            raise RuntimeError("Session not provided")

        q = await session.execute(
            select(User).where(
                (User.email == email_or_username) | (User.username == email_or_username)
            )
        )
        user = q.scalars().first()
        if not user:
            raise InvalidCredentials()

        if not user.is_active:
            raise InvalidCredentials()

        if user.email_verified_at is None:
            # Optionally re-send verification here if you want
            raise EmailNotVerified()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        # Issue access + refresh
        access = create_access_token(sub=str(user.id), role=user.role)

        now = datetime.now(timezone.utc)
        raw_refresh = generate_raw_token()  # opaque
        rec = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            expires_at=expiry_in(REFRESH_TOKEN_EXPIRY_DAYS * 24),
            revoked_at=None,
            created_at=now,
        )
        session.add(rec)
        await session.commit()

        return {"access_token": access, "refresh_token": raw_refresh}

    # ---------- REFRESH (rotate) ----------
    async def refresh(self, *, refresh_token: str):
        print('can reach here')
        session = self._session
        if session is None:
            raise RuntimeError("Session not provided")

        th = hash_token(refresh_token)
        q = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == th))
        rec = q.scalars().first()
        now = datetime.now(timezone.utc)
        if not rec or rec.revoked_at is not None or rec.expires_at <= now:
            raise RefreshTokenInvalid()

        # Load user
        user = await session.get(User, rec.user_id)
        if not user or not user.is_active or user.email_verified_at is None:
            raise RefreshTokenInvalid()

        print('can reach here')

        # Rotate: revoke old, mint new
        rec.revoked_at = now

        new_raw = generate_raw_token()
        new_rec = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_raw),
            expires_at=expiry_in(REFRESH_TOKEN_EXPIRY_DAYS * 24),
            revoked_at=None,
            created_at=now,
        )
        session.add(new_rec)

        access = create_access_token(sub=str(user.id), role=user.role)
        await session.commit()

        return {"access_token": access, "refresh_token": new_raw}

    # ---------- LOGOUT ----------
    async def logout(self, *, refresh_token: str):
        session = self._session
        if session is None:
            raise RuntimeError("Session not provided")

        th = hash_token(refresh_token)
        q = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == th))
        rec = q.scalars().first()
        if not rec or rec.revoked_at is not None:
            # idempotent
            return {"message": "ok"}

        rec.revoked_at = datetime.now(timezone.utc)
        await session.commit()
        return {"message": "ok"}
