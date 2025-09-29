import socket as so
from socket import socket
from threading import Thread
from typing import Dict, Optional, List, Tuple

from urllib.request import urlopen
from urllib.parse import quote

import json

CONFIG_PATH = "tasmota.json"

URL_BASE_NO_AUTH = "http://{address}/cm?cmnd={cmd}"
URL_BASE_AUTH = "http://{address}/cm?user={user}&password={password}&cmnd={cmd}"

POWER_ON = "Power{relay} ON"
POWER_OFF = "Power{relay} OFF"

class TasmotaInterface:

    def __init__(self, host: str, channel: int, cutoff: int = 127,
                 user: Optional[str] = None, password: Optional[str] = None):
        self.host = host
        self.channel = channel
        self.cutoff = cutoff
        self.currentState = None

    def __call__(self, value):
        nextState = False
        if value > self.cutoff:
            nextState = True

        if self.currentState != nextState:
            self.currentState = nextState
            if nextState:
                self.powerOn()
            else:
                self.powerOff()

    def __send(self, url):
        urlopen(url)

    def __buildCommand(self, cmd: str, user: str = None, pwd: str = None):
        if user is None and pwd is None:
            return URL_BASE_NO_AUTH.format(address=self.host, cmd=quote(cmd))
        return URL_BASE_AUTH.format(address=self.host, cmd=quote(cmd), user=user, password=pwd)

    def powerOn(self, relay: str = "1", user: str = None, pwd: str = None, *args):
        self.__send(self.__buildCommand(cmd=POWER_ON.format(relay=relay), user=user, pwd=pwd))

    def powerOff(self, relay: str = "1", user: str = None, pwd: str = None, *args):
        self.__send(self.__buildCommand(cmd=POWER_OFF.format(relay=relay), user=user, pwd=pwd))

class UDPServer(Thread):

    def __init__(self, listenAddress: str = "127.0.0.1", listenPort: int = 4400):
        super().__init__()
        self.LISTEN_ADDRESS = listenAddress
        self.LISTEN_PORT = listenPort

        self.interfaces: Dict[int, TasmotaInterface] = {}

        self.socketBufferSize = 513 * 10

        self.socket: socket = None
        self.__isRunning = False

        self.socket = socket(so.AF_INET, so.SOCK_DGRAM)

        self.socket.setsockopt(
            so.SOL_SOCKET,
            so.SO_SNDBUF,
            self.socketBufferSize)
        self.socket.setsockopt(
            so.SOL_SOCKET,
            so.SO_RCVBUF,
            self.socketBufferSize)

       # self.socket.setblocking(False)

        self.socket.bind((self.LISTEN_ADDRESS, self.LISTEN_PORT))

    def addInterface(self, interface: TasmotaInterface):
        self.interfaces[interface.channel] = interface

    def run(self):
        self.__isRunning = True
        while self.__isRunning:
            message, address = self.socket.recvfrom(513)
            for c in self.interfaces:
                self.interfaces[c](message[c-1])

    def closeDevice(self):
        if not self.__isRunning:
            return
        self.__isRunning = False
        self.socket.close()

def readFile(path):
    """
    Read the complete file

    :param path: Path to read from
    :return: the data of the file
    """
    f = open(path, "r", encoding='utf8')
    result = ""
    try:
        result = f.read()
    finally:
        f.close()

    return result

def readJSON(path: str) -> dict:
    content = readFile(path)
    return json.loads(content)

def makeTasmotaFromPath(path: str) -> Tuple[List[TasmotaInterface], dict]:
    config = readJSON(path)
    interfaces = []
    for cfg in config["devices"]:
        interfaces.append(TasmotaInterface(cfg["host"], cfg["channel"], cfg["cutoff"],
                                           cfg["user"], cfg["password"]))
    return interfaces, config

if __name__ == "__main__":
    devices, config = makeTasmotaFromPath(CONFIG_PATH)
    server = UDPServer(listenAddress=config["listenAddress"], listenPort=config["listenPort"])
    for device in devices:
        server.addInterface(device)
    server.start()