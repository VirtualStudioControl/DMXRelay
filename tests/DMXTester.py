from serial import *
from typing import Optional, List

class DMX512ProMKII():

    def __init__(self):
        self.PORT = ""
        self.HEADDER: List[int]= [0]
        self.FOOTER: List[int]= []
        self.serialConnection: Optional[Serial] = None

        self.BAUDRATE = 250000
        self.PARITY = PARITY_NONE
        self.STOPBITS = STOPBITS_TWO

    def initDevice(self, port):
        self.PORT = port

        self.serialConnection = Serial(port=self.PORT, stopbits=self.STOPBITS,
                                       parity=self.PARITY, baudrate=self.BAUDRATE)
        self.serialConnection.setRTS(0)

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
                self.serialConnection.send_break(0.005)
                self.serialConnection.write(data=source)
                self.serialConnection.flush()
            except SerialTimeoutException:
                pass

    def closeDevice(self):
        if self.serialConnection is not None:
            self.serialConnection.close()

if __name__ == "__main__":
    dmxout = DMX512ProMKII()
    dmxout.initDevice("/dev/ttyUSB0")

    dmxframe = [0]*512
    dmxframe[0] = 0xff
    dmxframe[4] = 0xff
    dmxframe[8] = 0xff

    try:
        while True:
            dmxout.sendDMXFrame(dmxframe)
    finally:
        dmxout.closeDevice()