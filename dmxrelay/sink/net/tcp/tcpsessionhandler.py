from threading import Lock, Thread
from typing import Optional

from ...tools.bytetools import *
from ...logging import logengine
from ...auth.auth_utils import generateSalt
from ...protocol.serverprotocol import handleMessage

class TCPSessionHandler(Thread):
    def __init__(self, server, connection, address, port, authManager):
        super().__init__()
        self.server = server
        self.connection = connection
        self.address = address
        self.port = port

        self.sendLock = Lock()

        self.logger = logengine.getLogger()

        self.shouldClose = True
        self.authenticated = False
        self.challenge = generateSalt(64, 128)
        self.authManager = authManager
        self.username: Optional[str] = None

    def run(self) -> None:
        try:
            self.shouldClose = False
            while not self.shouldClose:
                length = self.getMessageLength()
                data = bytearray()
                while len(data) < length:
                    data += self.connection.recv(length - len(data))
                #data = self.connection.recv(length)
                self.onMessageRecv(data)

        except ConnectionResetError:
            pass  # Ignore
        finally:
            self.connection.close()
            self.server.removeSessionHandler(self)

    def requestClose(self):
        self.shouldClose = True

    def getMessageLength(self) -> int:
        length = self.connection.recv(4)
        while len(length) < 4:
            length += self.connection.recv(4 - len(length))  # 16 kb buffer
        return getInt(length, start=0)

    def onMessageRecv(self, data):
        response = handleMessage(self, data)
        if response is not None:
            self.sendMessage(response)

    def sendMessage(self, message: bytes):
        self.logger.info("Sending Message: {}".format(message))
        if self.connection is not None:
            self.sendLock.acquire()
            try:
                self.connection.sendall(message)
            finally:
                self.sendLock.release()
