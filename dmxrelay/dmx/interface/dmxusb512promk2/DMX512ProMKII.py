from serial import *
from typing import Optional, List

from ..abstract.IDMXDevice import IDMXDevice

class DMX512ProMKII(IDMXDevice):

    def __init__(self):
        self.PORT = ""
        self.HEADDER: List[int]= [0x7e, 6, 1, 2, 0]
        self.FOOTER: List[int]= [0xe7]
        self.serialConnection: Optional[Serial] = None

        self.BAUDRATE = 256000
        self.PARITY = PARITY_NONE
        self.STOPBITS = STOPBITS_ONE

    def initDevice(self, port):
        self.PORT = port

        self.serialConnection = Serial(port=self.PORT, stopbits=self.STOPBITS,
                                       parity=self.PARITY, baudrate=self.BAUDRATE)

    def sendDMXFrame(self, data: list):
        if self.serialConnection is not None:
            source = bytearray()
            for i in self.HEADDER:
                source.append(i)
            for i in data:
                val = i
                if val > 0xff:
                    val = 0xff
                elif val < 0:
                    val = 0
                source.append(val)
            for i in self.FOOTER:
                source.append(i)
            try:
                self.serialConnection.write(data=source)
                self.serialConnection.flush()
            except SerialTimeoutException:
                pass

    def closeDevice(self):
        if self.serialConnection is not None:
            self.serialConnection.close()
