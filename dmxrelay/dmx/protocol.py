from . import dmx_manager
from ..sink.net.tcp.tcpsessionhandler import TCPSessionHandler
from ..sink.protocol.serverprotocol import *

CLIENT_MESSAGE_TYPE_DMX = 0x04


def __handleMessageDMX(sessionHandler: TCPSessionHandler, message: bytes) -> Optional[bytes]:
    if sessionHandler.authenticated:
        dmx_manager.sendDMXFrame(message[1]&0x01 == 0x01, getInt(message, 2), message[6:])
    return None


def setup():
    setMessageHandler(CLIENT_MESSAGE_TYPE_DMX, __handleMessageDMX)

