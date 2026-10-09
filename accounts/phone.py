import re

_E164 = re.compile(r'^\+[1-9]\d{7,14}$')
_INDIA_MOBILE = re.compile(r'^[6-9]\d{9}$')


def normalize_phone(raw):
    """
    Returns a normalised E.164 number, or None if invalid.
    10-digit Indian mobiles (with optional 0 / 91 / +91 prefix) become +91XXXXXXXXXX.
    Other countries must be typed with a leading +country-code.
    """
    if not raw:
        return None
    s = re.sub(r'[\s\-().]', '', raw.strip())
    if s.startswith('+'):
        s = '+' + re.sub(r'\D', '', s[1:])
        if s.startswith('+91'):
            return s if _INDIA_MOBILE.match(s[3:]) else None
        return s if _E164.match(s) else None
    digits = re.sub(r'\D', '', s)
    if digits.startswith('0091'):
        digits = digits[4:]
    elif len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
    return f'+91{digits}' if _INDIA_MOBILE.match(digits) else None


def mask_phone(number):
    """+919876543210 -> +91******3210"""
    if len(number) <= 7:
        return number
    return number[:3] + '*' * (len(number) - 7) + number[-4:]
