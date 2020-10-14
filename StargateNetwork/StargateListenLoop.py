from . import Helpers, EventHook
import socket
import time
import io


class StargateListenLoop (Helpers.StargateThread, Helpers.StargateSocket):
    def __init__(self, host, port, stargate):
        super().__init__()
        self.host = host
        self.port = port
        self.onIncomingConnection = EventHook.EventHook()
        self.onIncomingConnected = EventHook.EventHook()
        self.onIncomingDisconnected = EventHook.EventHook()
        self.stargate = stargate

    def configureConnection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.socket.setblocking(0)

    def realRun(self):
        try:
            self.activeConnection, addr = self.socket.accept()
            self.onIncomingConnection.fire(addr[0])
            self.activeConnection.setblocking(0)
            while not self.stargate.dialFinish:
                time.sleep(0.001)
            self.socketConnected = True
            self.send(Helpers.StargateCMDEnum.DIALSEQUENCEFINISH)
            self.onIncomingConnected.fire(addr[0])
            self.loopReceve()
        except io.BlockingIOError:
            pass
        except:
            self.disconnect()

    def stop(self):
        super().stop()
        self.disconnect()

    def disconnect(self):
        super().disconnectSocket()
        self.onIncomingDisconnected.fire()

    def msgDialSequenceFinish(self):
        pass

    def msgDatas(self, payload):
        pass

    def msgDisconnect(self):
        self.disconnect()
