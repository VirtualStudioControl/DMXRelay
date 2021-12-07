from typing import List
import base64

from . import auth_utils


class User:

    def __init__(self, username, salt=None, passwd_hash=None, permissions=None):
        if permissions is None:
            permissions = []

        self.username: str = username
        self.passwd_hash: bytes = self.ensureDecoding(passwd_hash)
        self.salt: bytes = self.ensureDecoding(salt)

        self.permissions: List[int] = []

    def ensureDecoding(self, val):
        if type(val) == str:
            print("DECODING B64:", val)
            return base64.b64decode(val)
        return val

    def toDict(self):
        return {
            'username': self.username,
            'passwd_hash': str(base64.b64encode(self.passwd_hash)),
            'salt': str(base64.b64encode(self.salt)),
            'permissions': self.permissions
        }

    def setPassword(self, password):
        if self.salt is None:
            self.salt = auth_utils.generateSalt(32, 64)
        self.passwd_hash = auth_utils.hashPassword(password, self.salt)

    def setPermissions(self, permissions):
        self.permissions = permissions
