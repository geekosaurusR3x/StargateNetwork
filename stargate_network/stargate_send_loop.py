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
        try:
            self.host = host
            self.port = port
            self.onOutConnectionStart.fire(host)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.activeConnection = self.socket
        except:
            self.onOutConnectionError.fire()
            return

        self.socketConnected = True
        super().start()

    def realRun(self) -> NoReturn:
        self.loopReceve()

    def stop(self) -> NoReturn:
        self.send(StargateCMDEnum.DISCONNECT)
        super().disconnect()
        super().stop()

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
