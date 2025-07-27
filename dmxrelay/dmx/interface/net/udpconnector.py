from typing import Union

from dmxrelay.dmx.interface.abstract.IDMXDevice import IDMXDevice

import socket as so
from socket import socket

class UDPConnector(IDMXDevice):

    def __init__(self):
        super().__init__()

        self.PORT = ""
        self.IP_ADDRESS = "127.0.0.1"
        self.IP_PORT = 4400

        self.socketBufferSize = 512 * 2

        self.socket: socket = None
        self.__isRunning = False


    def initDevice(self, port, **kwargs):
        super().initDevice(**kwargs)
        self.PORT = port

        self.IP_ADDRESS = kwargs['ip_address']
        self.IP_PORT = kwargs['ip_port']

        self.socket = socket(so.AF_INET, so.SOCK_DGRAM)

        self.socket.setsockopt(
            so.SOL_SOCKET,
            so.SO_SNDBUF,
            self.socketBufferSize)
        self.socket.setsockopt(
            so.SOL_SOCKET,
            so.SO_RCVBUF,
            self.socketBufferSize)

        self.socket.setblocking(False)

        self.socket.bind(('', 0))
        self.__isRunning = True

    def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
        try:
            if isinstance(data, list):
                source = bytearray()

                for i in data:
                    val = i
                    if val > 0xff:
                        val = 0xff
                    elif val < 0:
                        val = 0
                    source.append(val)
                data = source

            self.socket.sendto(data, (self.IP_ADDRESS, self.IP_PORT))
        except Exception as ex:
            print("Exception occured while sending UDP packet: {}".format(ex))

    def closeDevice(self):
        if not self.__isRunning:
            return
        self.__isRunning = False
        self.socket.close()
