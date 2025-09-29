# api/v1/services/email_sender.py
import os
import json
import httpx
from typing import Optional

try:
    import aiosmtplib
except Exception:
    aiosmtplib = None  # optional dependency for SMTP mode


class EmailSender:
    async def send_verification(self, *, to_email: str, token: str) -> None: ...


class ConsoleEmailSender(EmailSender):
    async def send_verification(self, *, to_email: str, token: str) -> None:
        print(f"[DEV EMAIL] To: {to_email} | Verify token: {token}")


# ---------------------------
# Brevo (Sendinblue) REST API
# ---------------------------
class BrevoEmailSender(EmailSender):
    """
    Uses Brevo transactional endpoint:
    POST https://api.brevo.com/v3/smtp/email
    Headers: { "api-key": <BREVO_API_KEY>, "accept": "application/json", "content-type": "application/json" }
    JSON:
    {
      "sender": {"email": "...", "name": "..."},
      "to": [{"email": "..."}],
      "subject": "...",
      "textContent": "..."
    }
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("BREVO_API_KEY")
        self.from_email = from_email or os.getenv("BREVO_FROM_EMAIL", "noreply@yourdomain.com")
        self.from_name = from_name or os.getenv("BREVO_FROM_NAME", "JobRadar")
        self.base_url = base_url or os.getenv("BREVO_BASE_URL", "https://api.brevo.com/v3")
        if not self.api_key:
            raise RuntimeError("Brevo config missing: set BREVO_API_KEY")

    async def send_verification(self, *, to_email: str, token: str) -> None:
        verify_url = os.getenv("VERIFY_URL_BASE", "https://your.app/verify-email")
        link = f"{verify_url}?email={to_email}&token={token}"
        payload = {
            "sender": {"email": self.from_email, "name": self.from_name},
            "to": [{"email": to_email}],
            "subject": "Verify your email",
            "textContent": f"Welcome to JobRadar!\n\nClick to verify: {link}\n\nIf you didn't sign up, go fight with Moaaz.",
        }
        headers = {
            "api-key": self.api_key,
            "accept": "application/json",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(f"{self.base_url}/smtp/email", headers=headers, json=payload)
            r.raise_for_status()
