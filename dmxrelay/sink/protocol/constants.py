from ..logging import logengine
from ..tools.bytetools import putInt

logger = logengine.getLogger()


#region Constants

CLIENT_MESSAGE_TYPE_HELLO = 0x00
CLIENT_MESSAGE_TYPE_AUTHENTICATE = 0x01
CLIENT_MESSAGE_TYPE_CONTROL = 0x02
CLIENT_MESSAGE_TYPE_GETSET = 0x03

CLIENT_MESSAGE_TYPE_BROADCAST = 0xFF

SERVER_MESSAGE_TYPE_RequestAuth = 0x00
SERVER_MESSAGE_TYPE_Authenticated = 0x01
SERVER_MESSAGE_TYPE_Response = 0x02

SERVER_MESSAGE_TYPE_ServerBroadcast = 0xfe
SERVER_MESSAGE_TYPE_ClientBroadcast = 0xff

AUTH_SUCCESS = 0x00
AUTH_FAIL = 0x01
#endregion


#region Message Creators

def _buildMessage(type: int, payload: bytes):
    length = len(payload) + 1
    message = bytearray()
    putInt(message, length)
    message.append(type & 0xff)
    message += payload
    return message