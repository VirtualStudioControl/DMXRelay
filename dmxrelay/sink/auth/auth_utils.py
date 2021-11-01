import secrets
import hashlib


def generateSalt(minBytes, maxBytes):
    return secrets.token_bytes(secrets.choice(range(minBytes, maxBytes, 1)))


def hashPassword(password: str, salt: bytes):
    hash = hashlib.sha512(password.encode("utf-8"))
    hash.update(salt)
    return hash.digest()


def generateAuthBytes(username: str, password: str, salt: bytes, challenge: bytes):
    return generateAuthBytesFromSaltedPassword(username, hashPassword(password, salt), challenge)


def generateAuthBytesFromSaltedPassword(username: str, password_hash: bytes, challenge: bytes):
    hash = hashlib.sha512(username.encode("utf-8"))
    hash.update(password_hash)
    hash.update(challenge)
    return hash.digest()
