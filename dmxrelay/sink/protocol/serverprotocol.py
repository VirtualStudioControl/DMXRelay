from typing import Optional, Any, Callable

from .constants import _buildMessage
from ..config.config import getValueOrDefault, CONFIG_KEY_REQUIRE_AUTH
from ..auth.auth_utils import generateAuthBytesFromSaltedPassword
from ..logging import logengine
from ..tools.bytetools import *

from .constants import *

logger = logengine.getLogger()

#region Message Creators


def createRequestAuth(salt: bytes, challenge: bytes):
    content = bytearray()
    content.append(len(salt) & 0xff)
    content += salt
    content.append(len(challenge) & 0xff)
    content += challenge
    return _buildMessage(SERVER_MESSAGE_TYPE_RequestAuth, content)


def createAuthenticated(responseCode: int):
    content = bytearray()
    putInt(content, responseCode)
    return _buildMessage(SERVER_MESSAGE_TYPE_Authenticated, content)


def createResponse(messageID: int, payload: Optional[bytes] = None):
    content = bytearray()
    putInt(content, messageID)
    content += payload
    return _buildMessage(SERVER_MESSAGE_TYPE_Response, content)


def createBroadcastServer(message: bytes):
    return _buildMessage(SERVER_MESSAGE_TYPE_ServerBroadcast, message)


def createBroadcastClient(message: bytes):
    return _buildMessage(SERVER_MESSAGE_TYPE_ClientBroadcast, message)

#endregion


#region Message Type Handlers

def __handleMessageHello(sessionHandler, message: bytes) -> Optional[bytes]:
    username = message[1:].decode("utf-8")
    logger.info("User Connected: {}".format(username))
    sessionHandler.username = username
    if getValueOrDefault(CONFIG_KEY_REQUIRE_AUTH, True):
        user = sessionHandler.authManager.getUserByName(username)
        return createRequestAuth(user.salt, sessionHandler.challenge)

    sessionHandler.authenticated = True
    return createAuthenticated(AUTH_SUCCESS)

def __handleMessageAuthenticate(sessionHandler, message: bytes) -> Optional[bytes]:
    auth_string = message[1:]
    username = sessionHandler.username

    if username is not None:
        user = sessionHandler.authManager.getUserByName(username)
        referenceString = generateAuthBytesFromSaltedPassword(username, user.passwd_hash, sessionHandler.challenge)
        if referenceString == auth_string:
            sessionHandler.authenticated = True
            logger.info("User Authenticated: {}".format(username))
            return createAuthenticated(AUTH_SUCCESS)
    logger.info("User Authentification Failed: {}".format(username))

    return createAuthenticated(AUTH_FAIL)


def __handleMessageControl(sessionHandler, message: bytes) -> Optional[bytes]:
    key = bytesToKey(message[1:])
    if key in CONTROL_FUNCTIONS:
        CONTROL_FUNCTIONS[key](sessionHandler)
        return None
    logger.error("Received Message with Invalid Control Sequence: {} from {}".format(message[1:], sessionHandler.username))
    return None


def __handleMessageGetSet(sessionHandler, message: bytes) -> Optional[bytes]:
    flags = message[1]
    msg_identifier = getInt(message, 2)
    val_identifier = getInt(message, 6)

    if flags & 0x01 != 0:
        payload = message[10:]
        if val_identifier in DATA_SET:
            DATA_SET[val_identifier](sessionHandler, payload)
            return None
        logger.error(
            "Received Message with Invalid Setter ID: {} from {}".format(val_identifier, sessionHandler.username))
        return None
    else:
        if val_identifier in DATA_GET:
            response = DATA_GET[val_identifier](sessionHandler)
            return createResponse(msg_identifier, response)
        logger.error(
            "Received Message with Invalid Setter ID: {} from {}".format(val_identifier, sessionHandler.username))
        return None


def __handleMessageBroadcast(sessionHandler, message: bytes) -> Optional[bytes]:
    sessionHandler.server.broadcastMessage(createBroadcastClient(message[1:]))
    return None


DATA_GET = {

}

DATA_SET = {

}

CONTROL_FUNCTIONS = {

}

MESSAGE_HANDLERS = {
    CLIENT_MESSAGE_TYPE_HELLO: __handleMessageHello,
    CLIENT_MESSAGE_TYPE_AUTHENTICATE: __handleMessageAuthenticate,
    CLIENT_MESSAGE_TYPE_CONTROL: __handleMessageControl,
    CLIENT_MESSAGE_TYPE_GETSET: __handleMessageGetSet,
    CLIENT_MESSAGE_TYPE_BROADCAST: __handleMessageBroadcast
}


def handleMessage(sessionHandler, message: bytes) -> Optional[bytes]:
    if message[0] in MESSAGE_HANDLERS:
        return MESSAGE_HANDLERS[message[0]](sessionHandler, message)
    logger.error("Received Message with Invalid Type: {} from {}".format(message[0], sessionHandler.username))
    return None


#region

def setMessageHandler(messageType: int, handler: Callable[[Any, bytes], Optional[bytes]]):
    global MESSAGE_HANDLERS
    MESSAGE_HANDLERS[messageType] = handler


def setControlSequenceHandler(controlBytes: bytes, handler: Callable[[Any], None]):
    global CONTROL_FUNCTIONS
    CONTROL_FUNCTIONS[bytesToKey(key=controlBytes)] = handler


def setDataGetter(valueIdentifier: int, getter: Callable[[Any], Optional[bytes]]):
    global DATA_GET
    DATA_GET[valueIdentifier] = getter


def setDataSetter(valueIdentifier: int, setter: Callable[[Any, bytes], None]):
    global DATA_SET
    DATA_SET[valueIdentifier] = setter


def setDataGetterSetter(valueIdentifier: int, getter: Callable[[Any], Optional[bytes]],
                        setter: Callable[[Any, bytes], None]):
    setDataGetter(valueIdentifier, getter)
    setDataSetter(valueIdentifier, setter)


def bytesToKey(key: bytes):
    return key


#endregion

#endregion