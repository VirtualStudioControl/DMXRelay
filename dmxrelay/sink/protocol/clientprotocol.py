from typing import Optional, Callable, Any

from .constants import *
from .constants import _buildMessage

from ..auth.auth_utils import generateAuthBytes
from ..tools.bytetools import getInt


#region Data
RESPONSE_CALLBACKS = {

}
#endregion

#region Client

def createHello(username: str):
    return _buildMessage(CLIENT_MESSAGE_TYPE_HELLO, username.encode("utf-8"))


def createAuthenticate(authBytes: bytes):
    return _buildMessage(CLIENT_MESSAGE_TYPE_AUTHENTICATE, authBytes)


def createControl(controlBytes: bytes):
    return _buildMessage(CLIENT_MESSAGE_TYPE_CONTROL, controlBytes)


def createGet(messageID: int, valueID: int):
    return createGetSet(messageID, valueID)


def createSet(messageID: int, valueID: int, payload: bytes,
                 callback: Callable[[Any, bytes], None] = None):
    return createGetSet(messageID, valueID, payload, callback)


def createGetSet(messageID: int, valueID: int, payload: Optional[bytes] = None,
                 callback: Callable[[Any, bytes], None] = None):
    content = bytearray()
    if payload is None:
        content.append(0x00)
    else:
        content.append(0x01)
    putInt(content, messageID)
    putInt(content, valueID)

    if payload is not None:
        content += payload

    if callback is not None:
        global RESPONSE_CALLBACKS
        RESPONSE_CALLBACKS[messageID] = callback

    return _buildMessage(CLIENT_MESSAGE_TYPE_GETSET, content)


def createBroadcast(message: bytes):
    return _buildMessage(CLIENT_MESSAGE_TYPE_CONTROL, message)

#endregion


#region Message Handlers
def _handleRequestAuth(client, message):
    salt_len = message[1]
    salt = message[2: 2 + salt_len]
    challenge_len = message[2+salt_len]
    challenge = message[3+salt_len: 3+salt_len+challenge_len]
    authBytes = generateAuthBytes(client.username, client.password, salt, challenge)
    client.sendMessage(createAuthenticate(authBytes=authBytes))


def _handleAuthenticated(client, message):
    errorcode = getInt(message, 1)
    if errorcode == 0:
        logger.debug("Authentification Successful")
    else:
        logger.error("Authentification Failed, Error code {} for {}".format(errorcode, client))


def _handleResponse(client, message):
    messageID = getInt(message, 1)
    if messageID in RESPONSE_CALLBACKS:
        RESPONSE_CALLBACKS[messageID](client, message[5:])
        del RESPONSE_CALLBACKS[messageID]
    else:
        logger.debug("Got Orphaned response for Message with ID: {} for {}".format(messageID, client))


MESSAGE_HANDLERS = {
    SERVER_MESSAGE_TYPE_RequestAuth: _handleRequestAuth,
    SERVER_MESSAGE_TYPE_Authenticated: _handleAuthenticated,
    SERVER_MESSAGE_TYPE_Response: _handleResponse,
}


def handleMessage(client, message: bytes) -> Optional[bytes]:
    if message[0] in MESSAGE_HANDLERS:
        return MESSAGE_HANDLERS[message[0]](client, message)
    logger.error("Received Message with Invalid Type: {}".format(message[0]))
    return None
#endregion