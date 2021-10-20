from typing import Union


def putInt(array: Union[bytearray], value: int, start: int = 0, append: bool = False):
    if append:
        array.append((value >>  0) & 0xff)
        array.append((value >>  8) & 0xff)
        array.append((value >> 16) & 0xff)
        array.append((value >> 24) & 0xff)
    else:
        array[start + 0] = (value >>  0) & 0xff
        array[start + 1] = (value >>  8) & 0xff
        array[start + 2] = (value >> 16) & 0xff
        array[start + 3] = (value >> 24) & 0xff

    return array


def getInt(array: Union[bytearray, bytes], start: int = 0):
    value = (array[start + 0] << 0) | (array[start + 1] << 8) | (array[start + 2] << 16) | (array[start + 3] << 24)

    return value