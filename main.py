from dmxrelay.dmx import protocol, dmx_manager
from dmxrelay.sink.auth.auth_manager import AuthManager
from dmxrelay.sink.net.tcp.tcpserver import TCPServer
from dmxrelay.sink.config import config

if __name__ == "__main__":

    config.loadConfig()
    config.setValue(config.CONFIG_KEY_REQUIRE_AUTH, True)

    dmx_manager.rebuildDMXUniverse()
    protocol.setup()

    authManager = AuthManager()
    authManager.createUser("tester", "password")

    server = TCPServer(listenAddress="", authManager=authManager)
    server.run()