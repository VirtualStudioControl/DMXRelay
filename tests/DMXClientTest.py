from time import sleep
from typing import Iterable

from dmxrelay.sink.logging import logengine
from dmxrelay.sink.net.tcp.tcpclient import TCPClient
from dmxrelay.sink.protocol import clientprotocol
from dmxrelay.sink.tools.bytetools import putInt

logger = logengine.getLogger()

def createDMXMessage(shouldAppend: bool, universe: int, frame: Iterable):
    data = bytearray()
    if shouldAppend:
        data.append(0x01)
    else:
        data.append(0x00)
    putInt(data, universe)
    data += bytearray(frame)
    return clientprotocol._buildMessage(0x04, data)


def callback(client, value):
    logger.debug(value)

DMX_FRAME = [0]*512

for i in range(8):
    DMX_FRAME[3 * i + 0] = 0x00
    DMX_FRAME[3 * i + 1] = 0x7f
    DMX_FRAME[3 * i + 2] = 0xff

if __name__ == "__main__":
    client = TCPClient(address="192.168.0.234", username="tester", password="password")
    client.setTimeout(2)
    client.start()
    sleep(.25)
    client.sendMessage(clientprotocol.createHello(client.username))
    sleep(.25)
    value = 0
    #client.sendMessage(createDMXMessage(False, 0, DMX_FRAME))
    client.sendMessage(clientprotocol.createGet(0, 0, callback=callback))
    #client.requestStop()