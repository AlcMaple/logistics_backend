import re
from typing import Optional

PHONE_REGEX = r"^1[3-9]\d{9}$"


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    return bool(re.match(PHONE_REGEX, phone))
