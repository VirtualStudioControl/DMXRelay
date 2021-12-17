from threading import Thread, Lock
import socket
from typing import Optional

from ...protocol.clientprotocol import handleMessage
from ...tools.bytetools import getInt
from ...logging import logengine


class TCPClient(Thread):

    def __init__(self, address="127.0.0.1", port=4300, username="", password=""):
        super().__init__()

        self.address = address
        self.port = port

        self.username: str = username
        self.password: str = password

        self.sock = None
        self.timeout: Optional[float] = None
        self.running = False

        self.sendLock = Lock()

        self.logger = logengine.getLogger()

    def __str__(self):
        return "TCP Client connected to {}@{}:{}".format(self.username, self.address, str(self.port))

    def setTimeout(self, timeout: Optional[float]):
        self.timeout = timeout
        if self.sock is not None:
            self.sock.settimeout(timeout)

    def requestStop(self):
        self.running = False

    def run(self) -> None:
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)

        self.sock.connect((self.address, self.port))
        try:
            while self.running:
                try:
                    length = self.sock.recv(4)
                    while len(length) < 4:
                        length += self.sock.recv(4 - len(length))  # 16 kb buffer
                    pkglen = getInt(length, start=0)
                    data = bytearray()
                    while len(data) < pkglen:
                        data += self.sock.recv(pkglen - len(data))

                    self.logger.debug("Message Recieved: {:08X} {}".format(getInt(length, start=0), str(data)))
                    self.onMessageRecv(data)
                except:
                    pass

        except ConnectionAbortedError:
            pass # Socket closed by another thread
        finally:
            self.sock.close()

    def onMessageRecv(self, message: bytes):
        handleMessage(self, message)

    def sendMessage(self, message: bytes):
        if self.sock is not None:
            self.sendLock.acquire()
            try:
                self.logger.debug("Sending Message")
                self.sock.sendall(message)
            finally:
                self.sendLock.release()

    def closeConnection(self):
        self.sock.close()
