from typing import Union

from dmxrelay.sink.config import config
from dmxrelay.sink.logging.logengine import getLogger

logger = getLogger("IDMXDevice")

class IDMXDevice:

    def __init__(self):
        self.base_universe = 0

    def devicename(self) -> str:
        pass

    def manufacturer(self) -> str:
        pass

    def initDevice(self, *args, **kwargs):
        self.base_universe = kwargs.get(config.CONFIG_KEY_DMX_INTERFACE_UNIVERSE, 0)
        logger.info("Initializing Interface '{}' for base universe {}".format(str(self.__class__), self.base_universe))

    def universeCount(self) -> int:
        return 1

    def sendDMXFrame(self, universe: int, data: Union[list, bytearray, bytes]):
        pass

    def flushDMXData(self):
        pass

    def closeDevice(self):
        pass
