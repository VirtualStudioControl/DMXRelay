import json
from typing import List
SERIAL_AVAILABLE = False
try:
    from serial.tools import list_ports
    SERIAL_AVAILABLE = True
except:
    SERIAL_AVAILABLE = False


from . import dmx_manager
from ..sink.config import config
from ..sink.io import filetools
from ..sink.net.tcp.tcpsessionhandler import TCPSessionHandler
from ..sink.protocol.serverprotocol import *

CLIENT_MESSAGE_TYPE_DMX = 0x04


GET_INTERFACE_NAMES = 0x00000000
GET_INTERFACE_CONFIGURATION = 0x00000001
GET_AVAILABLE_PORTS = 0x00000002
GET_CURRENT_DMX_FRAME = 0x00000003
GET_CURRENT_DMX_SCENE = 0x00000004

#region Message Handlers

def __handleMessageDMX(sessionHandler: TCPSessionHandler, message: bytes) -> Optional[bytes]:
    if sessionHandler.authenticated:
        dmx_manager.sendDMXFrame(message[1]&0x01 == 0x01, getInt(message, 2), message[6:])
    return None

#endregion


#region Getters & Setters

def getInterfaceNames(sessionHandler: TCPSessionHandler) -> bytes:
    interfaces: List[str] = dmx_manager.getSupportedInterfaces()
    result = bytearray()
    for interface in interfaces:
        result += interface.encode("utf-8")
        result.append(0x00)
    return result


def getInterfaceConfiguration(sessionHandler: TCPSessionHandler) -> bytes:
    interfaceConfig = config.getValueOrDefault(config.CONFIG_KEY_DMX_INTERFACES, {})
    content = json.dumps(interfaceConfig, indent=2, sort_keys=True).encode("utf-8")
    return content


def setInterfaceConfiguration(sessionHandler: TCPSessionHandler, value: bytes) -> None:
    content = json.loads(value.decode("utf-8"))
    config.setValue(config.CONFIG_KEY_DMX_INTERFACES, content)
    dmx_manager.rebuildDMXUniverse()


def getSerialPorts(sessionHandler: TCPSessionHandler) -> bytes:
    if SERIAL_AVAILABLE:
        ports = list_ports.comports(True)
        result = bytearray()
        for info in ports:
            if info.manufacturer is not None or info.product is not None:
                result += info.device.encode("utf-8")
                result.append(0x00)

        return result
    return bytearray([0x00,])

def getCurrentDMXFrames(sessionHandler: TCPSessionHandler) -> bytes:
    return dmx_manager.getCurrentFrameData()


def getDMXScene(sessionHandler: TCPSessionHandler) -> bytes:
    return filetools.readFileBinary(config.getValueOrDefault(config.CONFIG_KEY_DMX_SCENE, "dmxscene.json"))

#endregion


def setup():
    setMessageHandler(CLIENT_MESSAGE_TYPE_DMX, __handleMessageDMX)

    setDataGetter(GET_INTERFACE_NAMES, getInterfaceNames)
    setDataGetterSetter(GET_INTERFACE_CONFIGURATION, getInterfaceConfiguration, setInterfaceConfiguration)
    setDataGetter(GET_AVAILABLE_PORTS, getSerialPorts)
    setDataGetter(GET_CURRENT_DMX_FRAME, getCurrentDMXFrames)
    setDataGetter(GET_CURRENT_DMX_SCENE, getDMXScene)
