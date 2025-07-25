import struct
from threading import Thread

from dmxrelay.dmx.simulation.sender.simulationconnectionhandler import SimulationConnectionHandler
from dmxrelay.sink.net.tcp.tcpserver import TCPServer

from dmxrelay.sink.config import config

class SimulationSender(TCPServer):

    def __init__(self):
        super().__init__(config.getValueOrDefault(config.CONFIG_KEY_SIMULATION_LISTEN_ADDRESS, "0.0.0.0"),
                         config.getValueOrDefault(config.CONFIG_KEY_SIMULATION_PORT, 4500),
                         sessionHandler=SimulationConnectionHandler)

    def run(self):
        super().run()

    def requestClose(self):
        self.requestStop()

    def sendDMXFrame(self, universe, frame):
        package = bytes()
        struct.pack_into("<I", package, 0, universe)
        struct.pack_into("<512s", package, 4, frame)
        self.broadcastMessage(package)