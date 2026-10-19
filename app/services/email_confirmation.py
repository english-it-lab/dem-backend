import hashlib
import hmac
from datetime import datetime

from app.core.config import settings
from app.services.send_mails import send_email


class EmailConfirmationService:
    """Business logic for email confirmation codes."""

    CODE_LENGTH = 6

    def _generate_code_for_window(self, email: str, time_window_offset: int = 0) -> str:
        """
        Generates a 6-digit confirmation code for the email using HMAC.

        The code is deterministic for email + timestamp (per time window),
        allowing validation within the specified period.

        Args:
            email: The email address to generate code for.
            time_window_offset: Offset from current time window (0 = current, -1 = previous, etc.).

        Returns:
            6-digit confirmation code.
        """
        now = datetime.now()
        minutes = (now.hour * 60 + now.minute) // settings.email_confirmation_time_window_minutes
        target_minutes = minutes + time_window_offset
        time_window = f"{now.year}{now.month:02d}{now.day:02d}{target_minutes:05d}"

        # Create message for HMAC
        message = f"{email}:{time_window}"

        # Generate HMAC using the secret key
        hmac_hash = hmac.new(
            settings.email_confirmation_secret_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Convert hex hash to a number and take the last 6 digits
        code = str(int(hmac_hash, 16))[-self.CODE_LENGTH :]
        return code

    def generate_code(self, email: str) -> str:
        """
        Generates a 6-digit confirmation code for the email using HMAC.

        The code is deterministic for email + timestamp (per time window),
        allowing validation within the specified period.
        """
        return self._generate_code_for_window(email, time_window_offset=0)

    async def send_code(self, email: str) -> tuple[str, bool]:
        """
        Generates and sends confirmation code to the email.

        Args:
            email: Recipient email address

        Returns:
            Tuple of (code, success_status)
        """
        code = self.generate_code(email)
        subject = "Your Confirmation Code"
        body = f"""
Hello,

Your confirmation code is: {code}

If you didn't request this code, please ignore this email.
"""
        # send_email is synchronous, so we need to handle it appropriately
        # For now, we'll call it directly and catch any exceptions
        try:
            send_email(email, subject, body)
            return code, True
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
            return code, False

    def verify_code(self, email: str, code: str) -> bool:
        """
        Verifies the correctness of the code for the email.

        Takes into account the current and previous time window
        to allow for a grace period.
        """
        # Check current window
        if self.generate_code(email) == code:
            return True

        # Check previous window (grace period)
        return self._generate_code_for_previous_window(email) == code

    def _generate_code_for_previous_window(self, email: str) -> str:
        """Generates code for the previous time window."""
        return self._generate_code_for_window(email, time_window_offset=-1)
