from typing import List, Dict, Optional

from .user import User
from .auth_utils import generateSalt
from ..io.filetools import writeJSON, readJSON
from ..config.config import getValueOrDefault, CONFIG_KEY_USER_DB


class AuthManager:

    def __init__(self):
        self.users: Dict[str, User] = {}

    def getUserByName(self, username) -> Optional[User]:
        if username in self.users:
            return self.users[username]
        return None

    def createUser(self, username, password, permissions=None):
        if permissions is None:
            permissions = []

        user = User(username)
        user.setPassword(password)

        user.setPermissions(permissions)
        self.addUser(user)

    def addUser(self, user: User):
        self.users[user.username] = user

    def storeDB(self):
        userList = []
        for user in self.users:
            userList.append(self.users[user].toDict())

        data = {
            'users': userList
        }

        writeJSON(getValueOrDefault(CONFIG_KEY_USER_DB, "users.json"), data)


    def loadDB(self):
        values = readJSON(getValueOrDefault(CONFIG_KEY_USER_DB, "users.json"))
