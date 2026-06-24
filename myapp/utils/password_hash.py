import base64
import os
import hashlib

# 和Django官方默认参数保持一致
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 180000
SALT_BYTE_LEN = 16


def make_password(raw_password: str) -> str:
    """
    明文密码生成Django兼容的PBKDF2加盐哈希
    格式：算法名$迭代次数$base64盐$base64哈希值
    """
    # 生成加密安全的随机盐
    salt = os.urandom(SALT_BYTE_LEN)

    # 使用Python标准库PBKDF2-HMAC-SHA256生成慢哈希
    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=raw_password.encode("utf-8"),
        salt=salt,
        iterations=ITERATIONS,
        dklen=32
    )

    # 盐和哈希值转base64字符串，方便存入数据库
    salt_b64 = base64.b64encode(salt).decode("ascii").strip()
    hash_b64 = base64.b64encode(hash_bytes).decode("ascii").strip()

    # 拼接成Django标准格式
    return f"{ALGORITHM}${ITERATIONS}${salt_b64}${hash_b64}"


def check_password(raw_password: str, encoded_str: str) -> bool:
    """
    校验明文密码和数据库中存储的哈希是否匹配
    防时序攻击：使用常量时间对比
    """
    try:
        # 拆分Django格式的哈希字符串
        alg, iter_str, salt_b64, hash_b64 = encoded_str.split("$", 3)
        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(hash_b64)
    except Exception:
        return False

    # 用完全相同的参数重新计算哈希
    computed_hash = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=raw_password.encode("utf-8"),
        salt=salt,
        iterations=iterations,
        dklen=32
    )

    # 常量时间对比，防御时序攻击
    # 先对两个哈希再做一次SHA256，再对比，保证耗时一致
    return hashlib.sha256(computed_hash).digest() == hashlib.sha256(stored_hash).digest()