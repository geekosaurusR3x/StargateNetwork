from .helpers import StargateCMDEnum, StargateThread, StargateSocket
from .event_hook import EventHook
import socket
import time
import io
from typing import Type, NoReturn


class StargateSendLoop (StargateThread, StargateSocket):
    """Loop for Listening incoming travelers
       Extend Thread and Sockets
    """

    def __init__(self, stargate) -> NoReturn:
        super().__init__()
        self.onOutConnectionStart = EventHook()
        self.onOutConnected = EventHook()
        self.onOutConnectionError = EventHook()
        self.onOutDisconnected = EventHook()

    def dial(self, host, port) -> NoReturn:
        self.host = host
        self.port = port
        super().start()

    def realRun(self) -> NoReturn:
        if(not self.socketConnected):
            if(not self.host is None and not self.port is None):
                try:
                    self.onOutConnectionStart.fire(self.host)
                    print("1")
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("2")
                    self.socket.connect((self.host, self.port))
                    print("3")
                    self.activeConnection = self.socket
                    print("4")
                    self.socketConnected = True
                    print("5")
                except Exception as err:
                    print(err)
                    self.onOutConnectionError.fire()
                    super().stop()
                    return
        else:
            self.loopReceve()

    def stop(self) -> NoReturn:
        self.send(StargateCMDEnum.DISCONNECT)
        super().disconnect()
        super().stop()
        self.host = None
        self.port = None

    def disconnect(self) -> NoReturn:
        super().disconnect()
        self.onOutDisconnected.fire()

    def sendTroughGate(self, filename, content) -> NoReturn:
        payload = filename+chr(2)+content
        self.send(StargateCMDEnum.DATAS, payload)

    def msgDialSequenceFinish(self) -> NoReturn:
        self.onOutConnected.fire(self.host)

    def msgDisconnect(self) -> NoReturn:
        self.onOutDisconnected.fire()

    def msgDatas(self, payload) -> NoReturn:
        pass
