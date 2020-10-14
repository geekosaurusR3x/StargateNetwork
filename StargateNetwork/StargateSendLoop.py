from . import Helpers, EventHook

import socket
import time
import io


class StargateSendLoop (Helpers.StargateThread, Helpers.StargateSocket):
    def __init__(self, stargate):
        super().__init__()
        self.onOutConnectionStart = EventHook.EventHook()
        self.onOutConnected = EventHook.EventHook()
        self.onOutConnectionError = EventHook.EventHook()
        self.onOutDisconnected = EventHook.EventHook()
        self.stargate = stargate

    def dial(self, host, port):
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

    def realRun(self):
        self.loopReceve()

    def stop(self):
        self.send(Helpers.StargateCMDEnum.DISCONNECT)
        self.socketConnected = False
        self.socket.close()
        super().stop()

    def disconnect(self):
        super().disconnectSocket()
        self.onOutDisconnected.fire()

    def msgDialSequenceFinish(self):
        self.onOutConnected.fire(self.host)

    def msgDatas(self, payload):
        pass

    def msgDisconnect(self):
        self.onOutDisconnected.fire()
