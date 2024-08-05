from typing import Dict, Union, Optional, List

from .interface.abstract.IDMXDevice import IDMXDevice
from .interface.dmxusb512promk2.DMX512ProMKII import SERIAL_AVAILABLE
from .interface.net.udpconnector import UDPConnector

from .interface.udmx.UDMX import USB_AVAILABLE
from .sender.dmx_buffer import DMXBuffer
from .sender.dmxsender import DMXSender
from ..sink.config import config
from ..sink.logging import logengine

logger = logengine.getLogger()

INTERFACES: Dict[str, type] = {
}

if SERIAL_AVAILABLE:
    from .interface.opendmxusb.OpenDMXUSB import OpenDMXUSB
    from .interface.dmxusb512promk2.DMX512ProMKII import DMX512ProMKII

    INTERFACES["Enttec Open DMX USB"] = OpenDMXUSB
    INTERFACES["Eurolite USB DMX 512 Pro MK2"] = DMX512ProMKII

if USB_AVAILABLE:
    from .interface.udmx.UDMX import UDMXDevice
    INTERFACES["UDMX"] = UDMXDevice

INTERFACES["UDP"] = UDPConnector

SENDER: Optional[DMXSender] = None


def getSupportedInterfaces() -> List[str]:
    return list(INTERFACES.keys())


def init():
    global SENDER
    SENDER = DMXSender(INTERFACES)
    SENDER.start()


def getCurrentFrameData():
    return SENDER.getCurrentFrameData()


def rebuildDMXUniverse():
    if SENDER is None:
        init()
    SENDER.rebuildUniverse()

def storeExitFrame():
    if SENDER is not None:
        SENDER.storeExitFrame()

def sendDMXFrame(appendFrame: bool, universe: int, frameData: Union[list, bytearray, bytes]):
    if appendFrame:
        SENDER.FRAMEBUFFER.appendFrame(universe, frameData)
    else:
        SENDER.FRAMEBUFFER.setFrame(universe, frameData)