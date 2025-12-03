"""
pii_masker.py
Utility module for masking sensitive user information (PII) such as email IDs,
phone numbers, and account identifiers before sending data to an AI model.
"""

import re

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3})?[-. (]*\d{3}[-. )]*\d{3}[-. ]*\d{4}")


def mask_email(text: str) -> str:
    """Mask emails like john@example.com → j***@example.com"""
    def repl(match):
        email = match.group(0)
        name, domain = email.split("@")
        return f"{name[0]}***@{domain}"
    return EMAIL_REGEX.sub(repl, text)


def mask_phone(text: str) -> str:
    """Mask phone numbers like +1-987-654-3210 → ***-***-**10"""
    matches = PHONE_REGEX.findall(text)
    for m in matches:
        digits = re.sub(r"\D", "", m)
        if len(digits) < 4:  # ignore invalid
            continue
        masked = "*" * (len(digits) - 2) + digits[-2:]
        text = text.replace(m, masked)
    return text


def mask_pii(text: str) -> str:
    """Master wrapper to mask ALL supported PII"""
    if not text:
        return text
    text = mask_email(text)
    text = mask_phone(text)
    return text
