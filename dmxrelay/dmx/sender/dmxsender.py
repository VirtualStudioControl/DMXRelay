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
                try:
                    dev = self.INTERFACES[device[config.CONFIG_KEY_DMX_INTERFACE_TYPE]]()
                    dev.initDevice(**device)
                    self.DMX_UNIVERSES[device[config.CONFIG_KEY_DMX_INTERFACE_UNIVERSE]] = dev
                except Exception as ex:
                    logger.warning("Found invalid configuration: {}".format(device))
                    logger.exception(ex)

    def getCurrentFrameData(self):
        return self.FRAMEBUFFER.getCurrentFrameData()

    def storeExitFrame(self):
        self.FRAMEBUFFER.storeExitFrame()

    def run(self) -> None:
        startTime = time()
        while not self.shouldFinish:
            loop_start_time = time() - startTime
            with self.universeLock:
                lock_gotten_time = time() - startTime
                for universe in self.DMX_UNIVERSES:
                    frame_start_time = time() - startTime
                    frame = self.FRAMEBUFFER.getNextFrame(universe)
                    got_frame_time = time() - startTime
                    try:
                        self.DMX_UNIVERSES[universe].sendDMXFrame(frame)
                    except Exception as ex:
                        logger.warning("Failed to send DMX Frame")
                        logger.exception(ex)
                    frame_send_time = time() - startTime
                lock_release_time = time() - startTime
            sleepTime = (startTime + self.frameTime) - time()
            sleep_start_time = time() - startTime
            if sleepTime > 0:
                sleep(sleepTime)
            elif sleepTime < 0:
                self.FRAMEBUFFER.getNextFrame(universe)
            sleep_end_time = time() - startTime

            loopTime = time() - startTime
            if loopTime > 0.5:
                logger.debug("Frame sent in {} sec".format(loopTime))
                logger.debug("Timings: Loop Start: {}, Got Lock: {}, Start Frame: {}, Got Frame: {}, Sent Frame: {}, Released Lock: {}, Started Sleeping: {}, Ended Sleeping: {}".format(loop_start_time, lock_gotten_time,
                                frame_start_time, got_frame_time, frame_send_time, lock_release_time, sleep_start_time,
                                sleep_end_time))
            startTime = time()

    def requestClose(self):
        self.shouldFinish = True
