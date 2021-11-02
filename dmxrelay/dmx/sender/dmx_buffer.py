from typing import List, Union, Dict

from threading import Lock

class DMXBuffer():

    def __init__(self, defaultFrame=None):
        if defaultFrame is None:
            defaultFrame = [0]*512
        self.defaultFrame = defaultFrame
        self.buffers: Dict[int, List[Union[bytes, bytearray, List[int]]]] = {}
        self.frameLock = Lock()

    def getNextFrame(self, universe):
        with self.frameLock:
            if universe not in self.buffers or len(self.buffers[universe]) < 1:
                return self.defaultFrame
            result = self.buffers[universe][0]
            if len(self.buffers[universe]) > 1:
                del self.buffers[universe][0]
            return result

    def appendFrame(self, universe, frame):
        with self.frameLock:
            if universe not in self.buffers:
                self.buffers[universe] = []
            self.buffers[universe].append(frame)

    def setFrame(self, universe, frame):
        with self.frameLock:
            self.buffers[universe] = [frame]
