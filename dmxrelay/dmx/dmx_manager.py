from typing import Dict, Union, Optional

from .interface.abstract.IDMXDevice import IDMXDevice
from .interface.dmxusb512promk2.DMX512ProMKII import DMX512ProMKII
from .interface.opendmxusb.OpenDMXUSB import OpenDMXUSB
from .sender.dmx_buffer import DMXBuffer
from .sender.dmxsender import DMXSender
from ..sink.config import config
from ..sink.logging import logengine

logger = logengine.getLogger()

INTERFACES = {
    "Enttec Open DMX USB": OpenDMXUSB,
    "Eurolite USB DMX 512 Pro MK2": DMX512ProMKII
}

SENDER: Optional[DMXSender] = None


def getSupportedInterfaces():
    return list(INTERFACES.keys())


def init():
    global SENDER
    SENDER = DMXSender(INTERFACES)
    SENDER.start()


def rebuildDMXUniverse():
    if SENDER is None:
        init()
    SENDER.rebuildUniverse()


def sendDMXFrame(appendFrame: bool, universe: int, frameData: Union[list, bytearray, bytes]):
    if appendFrame:
        SENDER.FRAMEBUFFER.appendFrame(universe, frameData)
    else:
        SENDER.FRAMEBUFFER.setFrame(universe, frameData)