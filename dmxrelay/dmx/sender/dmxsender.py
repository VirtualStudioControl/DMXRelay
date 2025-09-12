from threading import Thread, Lock
from time import sleep, time
from typing import Dict, List

from dmxrelay.dmx.interface.abstract.IDMXDevice import IDMXDevice
from dmxrelay.dmx.sender.dmx_buffer import DMXBuffer
from dmxrelay.sink.config import config
from dmxrelay.sink.logging import logengine

logger = logengine.getLogger()

class DMXSender(Thread):

    def __init__(self, interfaces, simulation = None):
        super().__init__()
        self.SIMULATION = simulation
        self.shouldFinish = False

        self.INTERFACES = interfaces
        #self.DMX_UNIVERSES: Dict[int, IDMXDevice] = {}
        self.DMX_DEVICES: List[IDMXDevice] = []
        self.FRAMEBUFFER = DMXBuffer()

        self.frameTime = 1/20.0

        self.universeLock = Lock()

    def rebuildUniverse(self):
        with self.universeLock:
            logger.debug("Reloading Configuration")
            for device in self.DMX_DEVICES:
                device.closeDevice()
            self.DMX_DEVICES.clear()
            interface_configurations = config.getValueOrDefault(config.CONFIG_KEY_DMX_INTERFACES, [])

            for device in interface_configurations:
                try:
                    dev = self.INTERFACES[device[config.CONFIG_KEY_DMX_INTERFACE_TYPE]]()
                    logger.info("Initializing Device: {}".format(device[config.CONFIG_KEY_DMX_INTERFACE_TYPE]))
                    dev.initDevice(**device)

                    self.DMX_DEVICES.append(dev)
                except Exception as ex:
                    logger.warning("Found invalid configuration: {}".format(device))
                    logger.exception(ex)
            logger.info("Loaded {} Devices".format(len(self.DMX_DEVICES)))

    def getCurrentFrameData(self):
        return self.FRAMEBUFFER.getCurrentFrameData()

    def storeExitFrame(self):
        self.FRAMEBUFFER.storeExitFrame()

    #TODO: Loop over interfaces instead of universes
    # allowing for multi-universe interfaces
    def run(self) -> None:
        startTime = time()
        while not self.shouldFinish:
            loop_start_time = time() - startTime
            with self.universeLock:
                lock_gotten_time = time() - startTime
                for device in self.DMX_DEVICES:
                    frame_start_time = time() - startTime
                    for universe_offset in range(device.universeCount()):
                        universe = device.base_universe + universe_offset
                        frame = self.FRAMEBUFFER.getNextFrame(universe)
                        got_frame_time = time() - startTime
                        try:
                            device.sendDMXFrame(universe, frame)
                            if self.SIMULATION is not None:
                                self.SIMULATION.sendDMXFrame(universe, frame)
                        except Exception as ex:
                            logger.warning("Failed to send DMX Frame")
                            logger.exception(ex)
                    device.flushDMXData()
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
