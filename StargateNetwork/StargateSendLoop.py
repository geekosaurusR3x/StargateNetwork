from . import Helpers, EventHook

import socket
import time
import io


class StargateSendLoop (Helpers.StargateThread):
    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.onOutConnectionStart = EventHook.EventHook()
        self.onOutConnected = EventHook.EventHook()
        self.onOutConnectionError = EventHook.EventHook()
        self.onOutDisconnected = EventHook.EventHook()

    def dial(self, host, port):
        try:
            self.socket.connect((host, port))
            self.onOutConnectionStart.fire(host)
            self.onOutConnected.fire(host)
        except:
            self.onOutConnectionError.fire()
        self.sendDatas("test")

    def realRun(self):
        try:
            c, addr = self.socket.accept()
        except io.BlockingIOError:
            pass
        except Exception as e:
            print(e)

    def stop(self):
        self.sendDatas("disconnect")
        self.socket.close()
        super().stop()
        self.onOutDisconnected.fire()

    def sendDatas(self, datas):
        bufferSize = 4096
        totalsent = 0
        sent = bufferSize
        datas = datas.encode()
        while sent == bufferSize:
            sizeToSend = min(len(datas)-totalsent, bufferSize)
            sent = self.socket.send(datas[totalsent:totalsent+sizeToSend])
            if sent == bufferSize:
                totalsent += bufferSize
