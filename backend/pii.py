import re
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

PHONE_PLACEHOLDER = "<PHONE_MASKED>"
EMAIL_PLACEHOLDER = "<EMAIL_MASKED>"

email_re = re.compile(r"[\w\.-]+@[\w\.-]+")


def mask_emails(text: str) -> str:
    return email_re.sub(EMAIL_PLACEHOLDER, text)


def mask_phones(text: str, default_region="US") -> str:
    # Use phonenumbers to detect international phones
    out = text
    try:
        for match in phonenumbers.PhoneNumberMatcher(text, default_region):
            s = match.raw_string
            out = out.replace(s, PHONE_PLACEHOLDER)
    except NumberParseException:
        pass
    return out


def mask_pii(text: str) -> str:
    text = mask_emails(text)
    text = mask_phones(text)
    return text
