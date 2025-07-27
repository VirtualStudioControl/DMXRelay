SERIAL_AVAILABLE = False

try:
    from serial import *
    SERIAL_AVAILABLE = True
except:
    SERIAL_AVAILABLE = False

if SERIAL_AVAILABLE:

    START_BYTE = 0x7e
    END_BYTE = 0xe7

    from typing import Optional, List, Union

    from ..abstract.IDMXDevice import IDMXDevice

    class OpenDMXUSBPro(IDMXDevice):

        def __init__(self):
            super().__init__()

            self.PORT = ""
            self.serialConnection: Optional[Serial] = None

            self.BAUDRATE = 256000
            self.PARITY = PARITY_NONE
            self.STOPBITS = STOPBITS_ONE

        def initDevice(self, port, **kwargs):
            super().initDevice(**kwargs)
            self.PORT = port

            self.serialConnection = Serial(port=self.PORT, stopbits=self.STOPBITS,
                                           parity=self.PARITY, baudrate=self.BAUDRATE)

        def makeApplicationMessage(self, label: int, data: Union[list, bytearray, bytes]):
            lengthBytes = [len(data)&0xff, (len(data)>>8)&0xff]
            return [START_BYTE, label&0xff, *lengthBytes, *data, END_BYTE]

        def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
            if self.serialConnection is not None:
                source = bytearray()
                source.append(0x00)
                for i in data:
                    val = i
                    if val > 0xff:
                        val = 0xff
                    elif val < 0:
                        val = 0
                    source.append(val)

                try:
                    self.serialConnection.write(data=self.makeApplicationMessage(6, source))
                    self.serialConnection.flush()
                except SerialTimeoutException:
                    pass

        def closeDevice(self):
            if self.serialConnection is not None:
                self.serialConnection.close()
