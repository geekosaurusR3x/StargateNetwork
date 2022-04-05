"""Helpers methods for converting ip into 6 symbols for the stargate

"""

from abc import ABC, abstractmethod
import threading
import time
import socket
import io
import requests
from enum import Enum
from typing import List, Type, NoReturn


def SequenceToListInt(s: str, separator: str = '.') -> List[int]:
    """Convert '192.168.42.1' to [192,168,42,1]

    Args:
        s (str): String to convert
        separator (str, optional): Separator to use. Defaults to '.'.

    Returns:
        List[int] : List of int
    """
    return [int(item) for item in s.split(separator)]


def ListIntToSequence(l: List[int], separator: str = '.') -> str:
    """Merge [192,168,42,1] to '192.168.42.1'

    Returns:
        str: int join with sep
    """
    return separator.join(str(x) for x in l)


def ListNumbersToIntInBase(digits: List[int], base: int = 10) -> int:
    """Convert a list of digits into it's integer value into the coresponding base

    Args:
        digits (List[int]): List of digits to convert
        base (int, optional): base to convert. Defaults to 10.

    Returns:
        int: interger value of the number
    """
    val = 0
    exp = len(digits)-1
    for digit in digits:
        val += digit*pow(base, exp)
        exp -= 1
    return val


def NumberToBase(number: int, base: int = 10) -> List[int]:
    """Convert a int into it digits representation into a base

    Args:
        number (int): integer value to convert
        base (int, optional): base to convert. Defaults to 10.

    Returns:
        List[int]: List of digits
    """
    base = int(base)
    if number == 0:
        return [0]
    digits = []
    while number:
        digits.append(number % base)
        number //= base
    return digits[::-1]


def IpToStargateCode(ip: List[int]) -> List[int]:
    """Convert an ip into a stargate sequence

        The idea is converting the ip int from base 256 to base 38
        -> 39 symbols corresponding to [0 - 38] integers
        -> 38 is the earth symbole excluded from the conversion

        Algo :
        -> convert from base 256 to 38
        -> check and add 0 up to 7 digits
        -> remove the first one (look to StargateCodeToIp for rediscovering it)
        -> add earth symbol (38)
    Args:
        ip (List[int]): List int of ip digits

    Returns:
        List[int]: List int of stargate code digits
    """
    IntIP = ListNumbersToIntInBase(ip, 256)
    ListGlyphs = NumberToBase(IntIP, 38)
    while len(ListGlyphs) < 7:
        ListGlyphs.insert(0, 0)
    ListGlyphs.pop(0)
    ListGlyphs.append(38)
    return ListGlyphs


def StargateCodeToIp(sc: List[int]) -> List[int]:
    """Convert a stargate sequence to a ip

    The idea is converting the six firsts (from left) from base 38 to base 256

    Algo:
    -> remove the earth symbole (38) at the end
    -> check if the actual int from the sequence is inferior a max number :
        -> if yes add 0 to the left
        -> if no add 1 the the left
    -> convert updated sequence from base 38 to base 256
    -> check and add 0 up to 4 digits
    Args:
        sc (List[int]): List int of stargate code digits

    Returns:
        List[int]: List int of ip digits

    """
    sc = sc[:-1]
    maxintToShift = ListNumbersToIntInBase([1, 0, 0, 0, 0, 0], 38)
    actualint = ListNumbersToIntInBase(sc, 38)
    sc.insert(0, 0 if (actualint < maxintToShift) else 1)
    IntIP = ListNumbersToIntInBase(sc, 38)
    ListIP = NumberToBase(IntIP, 256)
    while len(ListIP) < 4:
        ListIP.insert(0, 0)
    return ListIP


class StargateThread(ABC, threading.Thread):
    """Helper class for stargate threads
        Abstract class
    """

    def __init__(self) -> NoReturn:
        super().__init__()
        threading.Thread.__init__(self)
        self.loop = True

    def run(self) -> NoReturn:
        """Main loop of the thread
        """
        while self.loop:
            self.realRun()
            time.sleep(0.001)

    @ abstractmethod
    def realRun(self) -> NoReturn:
        """Abstract method for implementing child loop
        """
        pass

    @ abstractmethod
    def stop(self) -> NoReturn:
        """Abstract method for stoping loop
        """
        self.loop = False

# helpers for threader into stargate


class StargateCMDEnum(Enum):
    """Enum for stargate commands
    """
    DISCONNECT = "disconnect"
    DIALSEQUENCEFINISH = "dialsequencefinish"
    DATAS = "datas"


class StargateSocket(ABC):

    """Abstract class for manipulating socket into the stargate loops
    """

    def __init__(self) -> NoReturn:
        super().__init__()
        self.socket = None
        self.bufferSize = 4096
        self.activeConnection = None
        self.socketConnected = False
        self.host = None
        self.port = None


    def getLocalAddress(self) -> str:
        """Retrun the public ip address

        Returns:
            str: Ip address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def getExternalAdress(self) -> str:
        myip = requests.get('https://www.wikipedia.org').headers['X-Client-IP']
        return myip

    def loopReceve(self) -> NoReturn:
        """Loop for receiving socket data without blocking

        Raises:
            RuntimeError: If socket suddely close
        """
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
                except:
                    self.disconnect()

            if(self.socketConnected):  # Decode only if connected
                msg = (b''.join(chunks)).decode()
                self.__interpetCommand(msg)

    @ abstractmethod
    def disconnect(self) -> NoReturn:
        """Abstract method for disconnecting loop
        """
        self.__disconnectSocket()
        pass

    def __disconnectSocket(self) -> NoReturn:
        """Close connection
        """
        self.socketConnected = False
        try:
            self.activeConnection.close()
        except:
            pass
        self.activeConnection = None

    def send(self, enumCmd: Type[StargateCMDEnum], payload: str = "") -> NoReturn:
        """Send stargate command into the socket
           concat command and payload with chr(1)

        Args:
                enumToSend(StargateCMDEnum): Type of command to send
                payload(str): payload to send (text or base64 bytes)
        """
        datas = ""+enumCmd.value+chr(1)+payload
        self.__sendDatas(datas)

    def __sendDatas(self, datas: str) -> NoReturn:
        """Send datas into the socket

        Args:
                datas(str): datas to send
        """
        totalsent = 0
        datas = datas.encode()
        sent = self.bufferSize
        while sent == self.bufferSize:
            sizeToSend = min(len(datas)-totalsent, self.bufferSize)
            sent = self.activeConnection.send(
                datas[totalsent:totalsent+sizeToSend])
            if sent == self.bufferSize:
                totalsent += self.bufferSize

    def __interpetCommand(self, msg: str) -> NoReturn:
        """Method for interpreting command

           Args:
                msg(str): command receive
        """
        msg = msg.split(chr(1))
        if msg[0] == StargateCMDEnum.DIALSEQUENCEFINISH.value:
            self.msgDialSequenceFinish()
        if msg[0] == StargateCMDEnum.DISCONNECT.value:
            self.msgDisconnect()
        if msg[0] == StargateCMDEnum.DATAS.value:
            self.msgDatas(msg[1])

    @ abstractmethod
    def msgDialSequenceFinish(self) -> NoReturn:
        """Abstract method for implementing end of dialing  sequence
        """
        pass

    @ abstractmethod
    def msgDisconnect(self) -> NoReturn:
        """Abstract method for implementing Disconnect sequence
        """
        pass

    @ abstractmethod
    def msgDatas(self, payload) -> NoReturn:
        """Abstract method for implementing receiving datas
        """
        pass
