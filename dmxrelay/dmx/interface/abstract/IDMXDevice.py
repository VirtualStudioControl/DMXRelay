from typing import Union


class IDMXDevice:

    def devicename(self) -> str:
        pass

    def manufacturer(self) -> str:
        pass

    def initDevice(self, port, **kwargs):
        pass

    def universeCount(self) -> int:
        return 1

    def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
        pass

    def closeDevice(self):
        pass
