from . import Helpers
import socket
import time
import io


class StargateListenLoop (Helpers.StargateThread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def configureConnection(self):

        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.socket.setblocking(0)

    def realRun(self):
        try:
            c, addr = self.socket.accept()
        except io.BlockingIOError:
            pass
        except Exception as e:
            print(e)

    def stop(self):
        super().stop()

    def getAddress(self):
        return socket.gethostbyname(socket.gethostname())
