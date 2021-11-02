from time import sleep
from typing import Iterable

from dmxrelay.sink.net.tcp.tcpclient import TCPClient
from dmxrelay.sink.protocol import clientprotocol
from dmxrelay.sink.tools.bytetools import putInt


def createDMXMessage(shouldAppend: bool, universe: int, frame: Iterable):
    data = bytearray()
    if shouldAppend:
        data.append(0x01)
    else:
        data.append(0x00)
    putInt(data, universe)
    data += bytearray(frame)
    return clientprotocol._buildMessage(0x04, data)


DMX_FRAME = [0]*512


if __name__ == "__main__":
    client = TCPClient(address="192.168.0.234", username="tester", password="password")
    client.start()
    sleep(.25)
    client.sendMessage(clientprotocol.createHello(client.username))
    sleep(.25)
    value = 0
    for i in range(0x1ff):
        DMX_FRAME[0] = value
        DMX_FRAME[4] = value
        DMX_FRAME[8] = value
        DMX_FRAME[9] = value
        DMX_FRAME[13] = value
        DMX_FRAME[17] = value
        DMX_FRAME[18] = value
        DMX_FRAME[22] = value
        client.sendMessage(createDMXMessage(False, 0, DMX_FRAME))
        value += 1
        value = (value &0xff)
    client.requestStop()