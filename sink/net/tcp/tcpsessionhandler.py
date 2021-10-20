from threading import Lock, Thread

from ...tools.bytetools import *
from ...logging import logengine


class TCPSessionHandler(Thread):
    def __init__(self, connection, address, port):
        super().__init__()
        self.connection = connection
        self.address = address
        self.port = port

        self.sendLock = Lock()

        self.logger = logengine.getLogger()

        self.shouldClose = True

    def run(self) -> None:
        try:
            self.shouldClose = False
            while not self.shouldClose:
                length = self.getMessageLength()
                data = self.connection.recv(length)
                self.logger.debug("Message Recieved: {:08X} {} from {}:{:06d}".format(length, str(data),
                                                                                      str(self.address), self.port))
                self.onMessageRecv(data)

        except ConnectionResetError:
            pass  # Ignore
        finally:
            self.connection.close()

    def requestClose(self):
        self.shouldClose = True

    def getMessageLength(self) -> int:
        while True:
            length = self.connection.recv(4)  # 16 kb buffer
            if len(length) < 4:
                continue
            return getInt(length, start=0)

    def onMessageRecv(self, data):
        pass

    def sendMessage(self, message: bytes):
        if self.connection is not None:
            self.sendLock.acquire()
            try:
                self.connection.sendall(message)
            finally:
                self.sendLock.release()
