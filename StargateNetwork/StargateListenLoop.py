from . import Helpers, EventHook
import socket
import time
import io


class StargateListenLoop (Helpers.StargateThread):
    def __init__(self, host, port, stargate):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.onIncomingConnection = EventHook.EventHook()
        self.onIncomingConnected = EventHook.EventHook()
        self.onIncomingDisconnected = EventHook.EventHook()
        self.activeConnection = None
        self.stargate = stargate
        self.connected = False

    def configureConnection(self):

        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.socket.setblocking(0)

    def realRun(self):
        try:
            self.activeConnection, addr = self.socket.accept()
            self.onIncomingConnection.fire(addr[0])
            self.activeConnection.setblocking(0)
            self.connected = True
            self.onIncomingConnected.fire(addr[0])
            self.loopReceve()
        except io.BlockingIOError:
            pass
        except Exception as e:
            print(e)

    def stop(self):
        super().stop()

    def loopReceve(self):
        bytes_recd = 0
        bufferSize = 4096

        while self.connected:
            bytes_recd = bufferSize
            chunks = []
            while bytes_recd == bufferSize:
                try:
                    chunk = self.activeConnection.recv(bufferSize)
                    bytes_recd = len(chunk)
                    if chunk == b'':
                        raise RuntimeError("socket connection broken")
                    chunks.append(chunk)
                except io.BlockingIOError:
                    pass
                except Exception as e:
                    print(e)

            msg = (b''.join(chunks)).decode()
            self.interpetCommand(msg)

    def interpetCommand(self, msg):
        if msg == "disconnect":
            self.connected = False
            self.activeConnection.close()
            self.onIncomingConnected.fire()

    def sendDatas(self, datas):
        bufferSize = 4096
        totalsent = 0
        sent = bufferSize
        while sent == bufferSize:
            sizeToSend = min(len(datas)-totalsent, bufferSize)
            sent = self.activeConnection.send(
                datas[totalsent:totalsent+sizeToSend])
            if sent == bufferSize:
                totalsent += bufferSize

    def getAddress(self):
        return socket.gethostbyname(socket.gethostname())
