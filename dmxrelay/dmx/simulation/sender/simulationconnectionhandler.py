from threading import Lock, Thread

from dmxrelay.sink.logging import logengine
from dmxrelay.sink.tools.bytetools import getInt


class SimulationConnectionHandler(Thread):

    def __init__(self, server, connection, address, port, authManager):
        self.server = server
        self.connection = connection
        self.address = address
        self.port = port

        self.sendLock = Lock()
        self.logger = logengine.getLogger()

        self.shouldClose = True

    def run(self):
        try:
            self.shouldClose = False
            while not self.shouldClose:
                length = self.getMessageLength()
                data = bytearray()
                while len(data) < length:
                    data += self.connection.recv(length - len(data))
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
        pass

    def sendMessage(self, message: bytes):
        if self.connection is not None:
            self.sendLock.acquire()
            try:
                self.connection.sendall(message)
            finally:
                self.sendLock.release()