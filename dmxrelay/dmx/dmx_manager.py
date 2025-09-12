from typing import Dict, Union, Optional, List

from .interface.dmxusb512promk2.DMX512ProMKII import SERIAL_AVAILABLE
from .interface.net.udpconnector import UDPConnector
from .interface.net.wledconnector import WLEDConnector

from .interface.udmx.UDMX import USB_AVAILABLE
from .sender.dmxsender import DMXSender
from .simulation.sender.simulation_sender import SimulationSender
from ..sink.config import config
from ..sink.config.config import CONFIG_KEY_SIMULATION_ENABLE
from ..sink.logging import logengine

logger = logengine.getLogger()

INTERFACES: Dict[str, type] = {
}

if SERIAL_AVAILABLE:
    from .interface.opendmxusb.OpenDMXUSB import OpenDMXUSB
    from .interface.opendmxusb.OpenDMXUSBPro import OpenDMXUSBPro
    from .interface.dmxusb512promk2.DMX512ProMKII import DMX512ProMKII

    INTERFACES["Enttec Open DMX USB"] = OpenDMXUSB
    INTERFACES["Enttec Open DMX USB Pro"] = OpenDMXUSBPro
    INTERFACES["Eurolite USB DMX 512 Pro"] = DMX512ProMKII
    INTERFACES["Eurolite USB DMX 512 Pro MK2"] = DMX512ProMKII
    INTERFACES["DMX 485"] = DMX485

if USB_AVAILABLE:
    from .interface.udmx.UDMX import UDMXDevice
    INTERFACES["UDMX"] = UDMXDevice

INTERFACES["UDP"] = UDPConnector
INTERFACES["WLED"] = WLEDConnector

SENDER: Optional[DMXSender] = None

HAS_SIMULATION = config.getValueOrDefault(CONFIG_KEY_SIMULATION_ENABLE, default=False)

if HAS_SIMULATION:
    SIMULATION_SERVER = None

def getSupportedInterfaces() -> List[str]:
    return list(INTERFACES.keys())

def init():
    global SENDER
    SENDER = DMXSender(INTERFACES)
    SENDER.start()

    if HAS_SIMULATION:
        global SIMULATION_SERVER
        SIMULATION_SERVER = SimulationSender()
        SIMULATION_SERVER.start()

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