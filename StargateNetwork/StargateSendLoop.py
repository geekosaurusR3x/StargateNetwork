from . import Helpers
import socket
import time
import io


class StargateSendLoop (Helpers.StargateThread):
    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def dial(self, host, port):
        self.socket.connect((host, port))
        print("Connected to gate")

    def realRun(self):
        try:
            c, addr = self.socket.accept()
        except io.BlockingIOError:
            pass
        except Exception as e:
            print(e)

    def stop(self):
        self.socket.shutdown()
        self.socket.close()
        super().stop()
