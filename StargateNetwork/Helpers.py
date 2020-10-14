from abc import ABC, abstractmethod
import threading
import time
import socket
import io
from enum import Enum

# helpers for translate ip to stargate glyph


def SequenceToListInt(s):
    lst = [int(item) for item in s.split('.')]
    return lst


def ListIntToSequence(l):
    return '.'.join(str(x) for x in l)


def ListNumbersToIntInBase(l, b):
    val = 0
    exp = len(l)-1
    for digit in l:
        val += digit*pow(b, exp)
        exp -= 1
    return val


def NumberToBase(n, b):
    b = int(b)
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(n % b)
        n //= b
    return digits[::-1]


def IpToStargateCode(ip):
    IntIP = ListNumbersToIntInBase(ip, 256)
    ListGlyphs = NumberToBase(IntIP, 38)
    while len(ListGlyphs) < 7:
        ListGlyphs.insert(0, 0)
    ListGlyphs.pop(0)
    ListGlyphs.append(38)
    return ListGlyphs


def StargateCodeToIp(sc):
    sc = sc[:-1]
    maxintToShift = ListNumbersToIntInBase([1, 0, 0, 0, 0, 0], 38)
    actualint = ListNumbersToIntInBase(sc, 38)
    sc.insert(0, 0 if (actualint < maxintToShift) else 1)
    IntIP = ListNumbersToIntInBase(sc, 38)
    ListIP = NumberToBase(IntIP, 256)
    while len(ListIP) < 4:
        ListIP.insert(0, 0)
    return ListIP


# helpers for threader into stargate
class StargateThread(ABC, threading.Thread):
    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)
        self.loop = True

    def run(self):
        while self.loop:
            self.realRun()
            time.sleep(0.001)

    @abstractmethod
    def realRun(self):
        pass

    @abstractmethod
    def stop(self):
        self.loop = False

# helpers for threader into stargate


class StargateSocket(ABC):
    def __init__(self):
        super().__init__()
        self.socket = None
        self.bufferSize = 4096
        self.activeConnection = None
        self.socketConnected = False
        self.host = None
        self.port = None

    def getAddress(self):
        return socket.gethostbyname(socket.gethostname())

    def loopReceve(self):
        bytes_recd = 0
        bufferSize = 4096

        while self.socketConnected:
            bytes_recd = bufferSize
            chunks = []
            while bytes_recd == bufferSize and self.socketConnected:
                try:
                    chunk = self.activeConnection.recv(bufferSize)
                    bytes_recd = len(chunk)
                    if chunk == b'':
                        raise RuntimeError("socket connection broken")
                    chunks.append(chunk)
                except io.BlockingIOError:
                    pass
                except Exception as e:
                    self.disconnect()

            if(self.socketConnected):  # Decode only if connected
                msg = (b''.join(chunks)).decode()
                self.interpetCommand(msg)

    @abstractmethod
    def disconnect(self):
        pass

    def disconnectSocket(self):
        self.socketConnected = False
        try:
            self.activeConnection.close()
        except:
            pass
        self.activeConnection = None

    def send(self, enumToSend, payload=""):
        datas = ""+enumToSend.value+chr(1)+payload
        self.sendDatas(datas)

    def sendDatas(self, datas):
        totalsent = 0
        datas = datas.encode()
        sent = self.bufferSize
        while sent == self.bufferSize:
            sizeToSend = min(len(datas)-totalsent, self.bufferSize)
            sent = self.activeConnection.send(
                datas[totalsent:totalsent+sizeToSend])
            if sent == self.bufferSize:
                totalsent += self.bufferSize

    def interpetCommand(self, msg):
        msg = msg.split(chr(1))
        if msg[0] == StargateCMDEnum.DIALSEQUENCEFINISH.value:
            self.msgDialSequenceFinish()
        if msg[0] == StargateCMDEnum.DISCONNECT.value:
            self.msgDisconnect()
        if msg[0] == StargateCMDEnum.DATAS.value:
            self.msgDatas(msg[1])

    @abstractmethod
    def msgDialSequenceFinish(self):
        pass

    @abstractmethod
    def msgDisconnect(self):
        pass

    @abstractmethod
    def msgDatas(self, payload):
        pass


class StargateCMDEnum(Enum):
    DISCONNECT = "disconnect"
    DIALSEQUENCEFINISH = "dialsequencefinish"
    DATAS = "datas"
