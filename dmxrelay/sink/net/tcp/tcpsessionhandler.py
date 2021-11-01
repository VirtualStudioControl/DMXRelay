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
                self.logger.debug("Ready to wait for messages....")
                length = self.getMessageLength()
                data = self.connection.recv(length)
                self.logger.debug("Message Recieved: {:08X} {} from {}:{}".format(length, str(data),
                                                                                      str(self.address), self.port))
                self.onMessageRecv(data)

        except ConnectionResetError:
            pass  # Ignore
        finally:
            self.connection.close()
            self.server.removeSessionHandler(self)

    def requestClose(self):
        self.shouldClose = True

    def getMessageLength(self) -> int:
        while True:
            length = self.connection.recv(4)  # 16 kb buffer
            if len(length) < 4:
                continue
            return getInt(length, start=0)

    def onMessageRecv(self, data):
        response = handleMessage(self, data)
        if response is not None:
            self.sendMessage(response)

    def sendMessage(self, message: bytes):
        if self.connection is not None:
            self.sendLock.acquire()
            try:
                self.connection.sendall(message)
            finally:
                self.sendLock.release()
