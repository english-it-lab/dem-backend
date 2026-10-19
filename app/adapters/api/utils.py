"""Utility functions for API adapters."""


def mask_email(email: str) -> str:
    """
    Mask email address for display purposes.

    Shows first character, then '***', then '@' and domain.

    Args:
        email: The email address to mask.

    Returns:
        Masked email (e.g., 'u***@example.com').

    Raises:
        ValueError: If email does not contain '@' symbol.
    """
    at_index = email.index("@")
    return f"{email[:1]}***{email[at_index:]}"
