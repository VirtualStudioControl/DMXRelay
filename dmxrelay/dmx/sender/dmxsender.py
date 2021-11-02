from threading import Thread, Lock
from time import sleep, time
from typing import Dict

from dmxrelay.dmx.interface.abstract.IDMXDevice import IDMXDevice
from dmxrelay.dmx.sender.dmx_buffer import DMXBuffer
from dmxrelay.sink.config import config
from dmxrelay.sink.logging import logengine

logger = logengine.getLogger()

class DMXSender(Thread):

    def __init__(self, interfaces):
        super().__init__()
        self.shouldFinish = False

        self.INTERFACES = interfaces
        self.DMX_UNIVERSES: Dict[int, IDMXDevice] = {}
        self.FRAMEBUFFER = DMXBuffer()

        self.frameTime = 1/20.0

        self.universeLock = Lock()

    def rebuildUniverse(self):
        with self.universeLock:
            logger.debug("Rebuilding Universe")
            for universe in self.DMX_UNIVERSES:
                self.DMX_UNIVERSES[universe].closeDevice()
            self.DMX_UNIVERSES.clear()
            interface_configurations = config.getValueOrDefault(config.CONFIG_KEY_DMX_INTERFACES, [])

            for device in interface_configurations:
                dev = self.INTERFACES[device[config.CONFIG_KEY_DMX_INTERFACE_TYPE]]()
                dev.initDevice(device[config.CONFIG_KEY_DMX_INTERFACE_PORT])
                self.DMX_UNIVERSES[device[config.CONFIG_KEY_DMX_INTERFACE_UNIVERSE]] = dev

    def run(self) -> None:
        startTime = time()
        while not self.shouldFinish:
            with self.universeLock:
                for universe in self.DMX_UNIVERSES:
                    frame = self.FRAMEBUFFER.getNextFrame(universe)
                    self.DMX_UNIVERSES[universe].sendDMXFrame(frame)
            sleepTime = (startTime + self.frameTime) - time()
            if sleepTime > 0:
                sleep(sleepTime)
            elif sleepTime < 0:
                self.FRAMEBUFFER.getNextFrame(universe)
            logger.debug("Frame sent in {} sec".format(time() - startTime))
            startTime = time()

    def requestClose(self):
        self.shouldFinish = True
