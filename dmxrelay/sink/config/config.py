from typing import Any

from ..io.filetools import readJSON, writeJSON

CONFIG_PATH = "config.json"
CONFIG_VALUES = {}


#region Config Keys

CONFIG_KEY_REQUIRE_AUTH = "requireAuth"
CONFIG_KEY_USER_DB = "user_db"
CONFIG_KEY_DMX_SCENE = "dmx_scene"

CONFIG_KEY_DMX_INTERFACES = "dmx_interfaces"
CONFIG_KEY_DMX_INTERFACE_PORT = "port"

CONFIG_KEY_DMX_INTERFACE_USB_VENDOR_ID = "usb_vendor_id"
CONFIG_KEY_DMX_INTERFACE_USB_PRODUCT_ID = "usb_product_id"
CONFIG_KEY_DMX_INTERFACE_USB_BUS_ID = "usb_bus"
CONFIG_KEY_DMX_INTERFACE_USB_ADDRESS_ID = "usb_address"

CONFIG_KEY_DMX_INTERFACE_TYPE = "type"
CONFIG_KEY_DMX_INTERFACE_UNIVERSE = "universe"

CONFIG_KEY_DMX_INTERFACE_AVAIL_TYPES = "interface_types"
#endregion


def loadConfig():
    global CONFIG_VALUES
    CONFIG_VALUES = readJSON(CONFIG_PATH)


def saveConfig():
    writeJSON(CONFIG_PATH, CONFIG_VALUES)


def getValueOrDefault(key, default: Any = None):

    if isinstance(key, (list, tuple)):
        return __getValue_list(key, default)

    return __getValue_direct(key, default)


def __getValue_direct(key, default: Any = None):
    if key in CONFIG_VALUES:
        return CONFIG_VALUES[key]
    return default


def __getValue_list(key, default: Any = None):
    result = CONFIG_VALUES
    for subkey in key:
        if subkey not in result:
            return default
        else:
            result = result[subkey]
    return result


def setValue(key, value):
    """
    Sets the value of the given Key in data. All keys in data not defined in value are discarded
    :param data:
    :param key:
    :param value:
    :return:
    """
    if isinstance(key, (list, tuple)):
        __setValue_list(key, value)
        return

    __setValue_direct(key, value)
    saveConfig()


def __setValue_direct(key, value):
    CONFIG_VALUES[key] = value


def __setValue_list(key, value):
    result = CONFIG_VALUES

    for subkey in key[:-1]:
        if subkey not in result:
            result[subkey] = {}
            result = result[subkey]
        else:
            result = result[subkey]

    result[key[-1]] = value
