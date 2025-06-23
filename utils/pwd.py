import hashlib
import uuid


def generate_salt() -> str:
    """
    生成盐值

    Returns:
        str: 32位十六进制盐值
    """
    return uuid.uuid4().hex


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    密码哈希加密

    Args:
        password: 明文密码
        salt: 盐值

    Returns:
        tuple[str, str]: (加密后的密码, 盐值)
    """
    if salt is None:
        salt = generate_salt()

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    验证密码

    Args:
        password: 明文密码
        hashed_password: 存储的哈希密码
        salt: 盐值

    Returns:
        bool: 密码是否匹配
    """
    verified_hash, _ = hash_password(password, salt)
    return verified_hash == hashed_password
