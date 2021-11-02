from typing import List

from . import auth_utils


class User:

    def __init__(self, username, salt=None, passwd_hash=None):
        self.username: str = username
        self.passwd_hash: bytes = passwd_hash
        self.salt: bytes = salt

        self.permissions: List[int] = []

    def toDict(self):
        return {
            'username': self.username,
            'password_hash': self.passwd_hash,
            'salt': self.salt,
            'permissions': self.permissions
        }

    def setPassword(self, password):
        if self.salt is None:
            self.salt = auth_utils.generateSalt(32, 64)
        self.passwd_hash = auth_utils.hashPassword(password, self.salt)

    def setPermissions(self, permissions):
        self.permissions = permissions