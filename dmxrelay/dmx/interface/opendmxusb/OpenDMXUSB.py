from serial import *
from typing import Optional, List, Union

from dmxrelay.sink.logging import logengine
from ..abstract.IDMXDevice import IDMXDevice

logger = logengine.getLogger()

class OpenDMXUSB(IDMXDevice):

    def __init__(self):
        self.PORT = ""
        self.HEADDER: List[int] = [0]
        self.FOOTER: List[int] = []
        self.serialConnection: Optional[Serial] = None

        self.BAUDRATE = 250000
        self.PARITY = PARITY_NONE
        self.STOPBITS = STOPBITS_TWO

    def initDevice(self, port):
        self.PORT = port

        self.serialConnection = Serial(port=self.PORT, stopbits=self.STOPBITS,
                                       parity=self.PARITY, baudrate=self.BAUDRATE)
        self.serialConnection.setRTS(0)
        self.serialConnection.write_timeout = 0.3
        self.serialConnection.set_input_flow_control(False)
        self.serialConnection.set_output_flow_control(False)

    def sendDMXFrame(self, data: Union[list, bytearray, bytes]):
        if self.serialConnection is not None:
            source = bytearray([0])
            source += bytearray(data)
            try:
                self.serialConnection.break_condition = True
                self.serialConnection.break_condition = False
                self.serialConnection.write(data=source)

            except SerialTimeoutException as ex:
                logger.exception(ex)

    def closeDevice(self):
        if self.serialConnection is not None:
            self.serialConnection.close()
