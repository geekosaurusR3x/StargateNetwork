from . import Helpers, EventHook

import socket
import time
import io


class StargateSendLoop (Helpers.StargateThread):
    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.onConnectionStart = EventHook.EventHook()
        self.onConnected = EventHook.EventHook()
        self.onConnectionError = EventHook.EventHook()
        self.onDisconnectionStart = EventHook.EventHook()
        self.onDisconnected = EventHook.EventHook()

    def dial(self, host, port):
        self.onConnectionStart.fire()
        try:
            self.socket.connect((host, port))
            self.onConnected.fire()
        except:
            self.onConnectionError.fire()

    def realRun(self):
        try:
            c, addr = self.socket.accept()
        except io.BlockingIOError:
            pass
        except Exception as e:
            print(e)

    def stop(self):
        self.onDisconnectStart.fire()
        self.socket.shutdown()
        self.socket.close()
        super().stop()
        self.onDisconnected.fire()
