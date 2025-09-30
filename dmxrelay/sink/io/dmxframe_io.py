from typing import List, Tuple, Union, Optional

from dmxrelay.sink.io.filetools import writeFileBinary, readFileBinary
from dmxrelay.sink.logging import logengine
from dmxrelay.sink.tools.bytetools import putInt, getInt

logger = logengine.getLogger()


def writeDMXFrame(path, frameData: List[Tuple[int, Union[bytes, bytearray, List[int]]]]):
    universe_count = len(frameData)
    content = bytearray()
    content += b'DMXFRAME'
    putInt(content, universe_count)

    for universe in frameData:
        putInt(content, universe[0])
        putInt(content, len(universe[1]))
        content += bytearray(universe[1])

    writeFileBinary(path, content)


def readDMXFrame(path) -> Optional[List[Tuple[int, bytearray]]]:
    try:
        content = readFileBinary(path)
    except:
        return None

    if content is None:
        return None

    if content[0:8] != b'DMXFRAME':
        logger.warning("Start Bytes do not match: Expected {}, got {}".format(b'DMXFRAME', content[0:8]))

    universeCount = getInt(content, 8)
    results = []

    position = 12
    for i in range(universeCount):
        universe = getInt(content, position)
        position += 4
        universeLength = getInt(content, position)
        position += 4
        data = content[position: position+universeLength]
        position += universeLength
        results.append((universe, bytearray(data)))

    return results