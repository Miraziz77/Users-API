import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_verification_email(to_email: str, code: str) -> None:
    """Send a verification code to the given email address via SMTP.

    In case the SMTP server is unreachable or misconfigured, the error is
    not swallowed: it propagates so the caller can decide how to handle it.
    For local development convenience, the code is also printed to console.
    """
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = f"{settings.PROJECT_NAME} — Email Verification"
    message.set_content(
        f"Your verification code is: {code}\n\n"
        f"This code will expire in {settings.VERIFICATION_CODE_EXPIRE_HOURS} hour(s)."
    )

    # Dev convenience: always log the code to console alongside the real email send.
    if settings.ENVIRONMENT == "dev":
        print(f"[DEV] Verification code for {to_email}: {code}")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=settings.SMTP_USE_TLS,
    )


async def send_verification_email_safe(to_email: str, code: str) -> None:
    """Background-task wrapper around send_verification_email that logs
    failures instead of raising, since there is no request context left
    to propagate the error to once the response has already been sent
    to the client. With more time this would go through Celery with
    retries instead of a fire-and-forget background task.
    """
    try:
        await send_verification_email(to_email, code)
    except Exception:
        logger.exception("Failed to send verification email to %s", to_email)