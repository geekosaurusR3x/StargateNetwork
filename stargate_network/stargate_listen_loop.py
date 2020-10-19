from .helpers import StargateCMDEnum, StargateThread, StargateSocket
from .event_hook import EventHook
import socket
import time
import io
from typing import Type, NoReturn


class StargateListenLoop (StargateThread, StargateSocket):
    """Loop for Listening incoming travelers
       Extend Thread and Sockets
    """

    def __init__(self, stargate) -> NoReturn:
        super().__init__()
        self.onIncomingConnection = EventHook()
        self.onIncomingConnected = EventHook()
        self.onIncomingDisconnected = EventHook()
        self.__stargate = stargate
        self.host = self.__stargate.host
        self.port = self.__stargate.port

    def configureConnection(self) -> NoReturn:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.socket.setblocking(0)

    def realRun(self) -> NoReturn:
        try:
            self.activeConnection, addr = self.socket.accept()
            self.onIncomingConnection.fire(addr[0])
            self.activeConnection.setblocking(0)
            while not self.__stargate.dialFinish:
                time.sleep(0.001)
            self.socketConnected = True
            self.send(StargateCMDEnum.DIALSEQUENCEFINISH)
            self.onIncomingConnected.fire(addr[0])
            self.loopReceve()
        except io.BlockingIOError:
            pass
        except:
            self.disconnect()

    def stop(self) -> NoReturn:
        super().stop()
        self.disconnect()

    def disconnect(self) -> NoReturn:
        super().disconnect()
        self.onIncomingDisconnected.fire()

    def msgDialSequenceFinish(self) -> NoReturn:
        pass

    def msgDatas(self, payload) -> NoReturn:
        file = payload.split(chr(2))
        if(file[0] == "text.tp"):
            self.__stargate.receiveDataText(file[1])
        else:
            self.__stargate.receiveDataFile(file[0], file[1])

    def msgDisconnect(self) -> NoReturn:
        self.disconnect()
