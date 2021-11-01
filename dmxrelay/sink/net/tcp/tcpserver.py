import socket
from threading import Thread
from typing import List

from .tcpsessionhandler import TCPSessionHandler
from ...logging import logengine


class TCPServer(Thread):
    def __init__(self, listenAddress="", port=4300, backlog: int = 0, sessionHandler=TCPSessionHandler,
                 authManager=None):
        super().__init__()
        self.listeningAddress = listenAddress
        self.port = port
        self.backlog = backlog

        self.running = False

        self.sessionHandlers: List[TCPSessionHandler] = []

        self.flags = socket.NI_NUMERICHOST | socket.NI_NUMERICSERV

        self.logger = logengine.getLogger()

        self.sessionHandlerType = sessionHandler

        self.authManager = authManager


    def __str__(self):
        return "TCP Server at " + str(self.listeningAddress) + ":" + str(self.port)

    def requestStop(self):
        self.running = False

    def run(self) -> None:
        self.running = True
        # create an instance of socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to its host and port
        self.sock.bind((self.listeningAddress, self.port))
        try:
            while self.running:
                self.sock.listen(self.backlog)
                self.connection, clientAddress = self.sock.accept()
                address, port = socket.getnameinfo(clientAddress, self.flags)
                handler = self.sessionHandlerType(self, self.connection, address, port, self.authManager)
                self.sessionHandlers.append(handler)
                handler.start()
                self.logger.debug("Received Connection from {}:{}".format(address, port))
        finally:
            for sessionHandler in self.sessionHandlers:
                sessionHandler.requestClose()
            for sessionHandler in self.sessionHandlers:
                sessionHandler.join()

    def broadcastMessage(self, message: bytes):
        for sessionHander in self.sessionHandlers:
            sessionHander.sendMessage(message)

    def removeSessionHandler(self, sessionHandler):
        if sessionHandler in self.sessionHandlers:
            self.sessionHandlers.remove(sessionHandler)