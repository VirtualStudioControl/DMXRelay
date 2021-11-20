from typing import List, Union, Dict

from threading import Lock

from dmxrelay.sink.config import config
from dmxrelay.sink.io import dmxframe_io
from dmxrelay.sink.tools.bytetools import putInt


class DMXBuffer():

    def __init__(self, defaultFrame=None):
        if defaultFrame is None:
            defaultFrame = [0]*512
        self.defaultFrame = defaultFrame
        self.buffers: Dict[int, List[Union[bytes, bytearray, List[int]]]] = {}
        self.frameLock = Lock()

        with self.frameLock:
            frameData = dmxframe_io.readDMXFrame(config.getValueOrDefault(config.CONFIG_KEY_DMX_PERSISTENT_FRAME,
                                                               "persistent.dmxframe"))
            if frameData is not None:
                for d in frameData:
                    self.buffers[d[0]] = [d[1]]


    def getNextFrame(self, universe):
        with self.frameLock:
            if universe not in self.buffers or len(self.buffers[universe]) < 1:
                return self.defaultFrame
            result = self.buffers[universe][0]
            if len(self.buffers[universe]) > 1:
                del self.buffers[universe][0]
            return result

    def getCurrentFrameData(self) -> bytes:
        content = bytearray()
        putInt(content, len(self.buffers))

        with self.frameLock:
            for universe in self.buffers:
                putInt(content, universe)
                putInt(content, len(self.buffers[universe][0]))
                content += bytearray(self.buffers[universe][0])

        return content

    def appendFrame(self, universe, frame):
        with self.frameLock:
            if universe not in self.buffers:
                self.buffers[universe] = []
            self.buffers[universe].append(frame)

    def setFrame(self, universe, frame):
        with self.frameLock:
            self.buffers[universe] = [frame]

    def storeExitFrame(self):
        frameData = []
        for universe in self.buffers:
            frameData.append((universe, self.buffers[universe][0]))

        dmxframe_io.writeDMXFrame(config.getValueOrDefault(config.CONFIG_KEY_DMX_PERSISTENT_FRAME,
                                                           "persistent.dmxframe"), frameData)
