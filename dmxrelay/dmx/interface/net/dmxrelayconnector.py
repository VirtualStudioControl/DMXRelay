from typing import Union

from dmxrelay.dmx.interface.abstract.IDMXDevice import IDMXDevice
from dmxrelay.sink.net.tcp.tcpclient import TCPClient
from dmxrelay.sink.protocol.clientprotocol import createDMXMessage


class DMXRelayConnector(IDMXDevice):
    def __init__(self):
        super().__init__()
        self.__isRunning = False

        self.client = None

    def initDevice(self, port, **kwargs):
        super().initDevice(**kwargs)

        self.client = TCPClient(address=kwargs["ip_address"], port=kwargs["ip_port"],
                                username=kwargs["username"], password=kwargs["password"])

        self.client.start()

    def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
        self.client.sendMessage(createDMXMessage(False, universe, data))

    def closeDevice(self):
        if not self.__isRunning:
            return
        self.client.requestStop()
        self.__isRunning = False
