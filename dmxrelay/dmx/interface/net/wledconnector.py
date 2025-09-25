import socket as so
from enum import Enum
from socket import socket
from typing import Union

from dmxrelay.dmx.interface.abstract.IDMXDevice import IDMXDevice
from dmxrelay.sink.logging.logengine import getLogger

logger = getLogger("WLED")

class WLEDProtocol(Enum):
    WARLS = 1
    DRGB = 2
    DRGBW = 3
    DNRGB = 4
    WLED_NOTIFIER = 0

CHANNELS_PER_LED = {
    WLEDProtocol.WARLS: 0,
    WLEDProtocol.DRGB: 3,
    WLEDProtocol.DRGBW: 4,
    WLEDProtocol.DNRGB: 3,
    WLEDProtocol.WLED_NOTIFIER: 0,
}

PROTOCOLS = {
    "WARLS": WLEDProtocol.WARLS,
    "DRGB": WLEDProtocol.DRGB,
    "DRGBW": WLEDProtocol.DRGBW,
    "DNRGB": WLEDProtocol.DNRGB,
    "WLED_NOTIFIER": WLEDProtocol.WLED_NOTIFIER,
}

class WLEDConnector(IDMXDevice):

    def __init__(self):
        super().__init__()

        self.PORT = ""
        self.IP_ADDRESS = "127.0.0.1"
        self.IP_PORT = 4400

        # TODO: Make Configurable
        self.protocol_type = WLEDProtocol.DRGBW
        self.protocol_timeout = 1
        self.LED_COUNT = 134

        self.frame_buffer = bytearray(self.LED_COUNT * CHANNELS_PER_LED[self.protocol_type] + 2)
        self.socketBufferSize = len(self.frame_buffer) * 5

        self.socket: socket = None
        self.__isRunning = False


    def initDevice(self, port, **kwargs):
        super().initDevice(**kwargs)
        self.PORT = port

        self.IP_ADDRESS = kwargs['ip_address']
        self.IP_PORT = kwargs['ip_port']

        self.protocol_type = PROTOCOLS[kwargs['wled_protocol']]
        self.protocol_timeout = kwargs['wled_timeout']
        self.LED_COUNT = kwargs['wled_pixel_count']

        self.frame_buffer = bytearray(self.LED_COUNT * CHANNELS_PER_LED[self.protocol_type] + 2)
        self.socketBufferSize = len(self.frame_buffer) * 5

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

    def universeCount(self) -> int:
        return 1 if self.LED_COUNT * CHANNELS_PER_LED[self.protocol_type] < 512 else 2

    def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
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
        offset = (universe - self.base_universe) * 512
        length = min(512, (self.LED_COUNT * CHANNELS_PER_LED[self.protocol_type]) - offset)
        self.frame_buffer[2 + offset: 2 + offset + length] = data[0:length]

    def flushDMXData(self):
        try:
            self.frame_buffer[0] = (self.protocol_type.value & 0xff)
            self.frame_buffer[1] = (self.protocol_timeout & 0xff)
            self.socket.sendto(self.frame_buffer, (self.IP_ADDRESS, self.IP_PORT))
        except Exception as ex:
            print("Exception occured while sending UDP packet: {}".format(ex))

    def closeDevice(self):
        if not self.__isRunning:
            return
        self.__isRunning = False
        self.socket.close()
