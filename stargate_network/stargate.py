from typing import List, NoReturn
from _thread import start_new_thread
import time
import tempfile
import os
import base64
from .stargate_listen_loop import StargateListenLoop
from .stargate_send_loop import StargateSendLoop
from .helpers import *
from .event_hook import EventHook


class Stargate():
    """Class for representing a stargate on internet

        Must be powered on before sending of receiving call

        This expose those events :
            - self.onDialingConnection = Start connecting to a stargate
            - self.onDialingConnected = If connection is ok
            - self.onDialingDisconnection = If connection is ko
            - self.onIncomingConnection = Start receiving from a stargate
            - self.onIncomingConnected = Connected from a stargate
            - self.onIncomingDisconnection = Disconnected from a stargate
            - self.onIncomingDataText = Text received from a stargate
            - self.onIncomingDataFile = File received from a stargate
    """

    def __init__(self, host: str = '', port: int = 24801) -> NoReturn:
        self.host = host
        self.port = port

        self.__listenloop = None
        self.__sendLoop = None
        self.__TimerLoop = None
        self.powered = False
        self.connected = False
        self.ipConnectedTo = None
        self.disablelisten = False
        self.disablesend = False

        self.reservedSequences = {
            "38.38.38.38.38.38.38": "127.0.0.1"
        }

        self.onDialingConnection = EventHook()
        self.onDialingConnected = EventHook()
        self.onDialingDisconnection = EventHook()
        self.onIncomingConnection = EventHook()
        self.onIncomingConnected = EventHook()
        self.onIncomingDisconnection = EventHook()
        self.onIncomingDataText = EventHook()
        self.onIncomingDataFile = EventHook()

        self.otherSequence = None
        self.dialFinish = False

    def __str__(self) -> str:
        return f"Stargate { self.getAddressOnNetwork() if self.powered and not self.disablelisten else None} \r\n\t Power state : {self.powered}\r\n\t Connection status : {self.connected} to {self.ipConnectedTo} \r\n\t Can Call : {not self.disablesend}\r\n\t Can Receve : {not self.disablelisten}"

    def powerOn(self) -> NoReturn:
        """Power On the stargate

            Instantiate ListenLoop Thread and configure the events
        """
        if(self.powered):
            return
        self.powered = True
        if not self.disablelisten:
            self.__listenloop = StargateListenLoop(self)
            self.__listenloop.onIncomingConnection += self.incomingConnection
            self.__listenloop.onIncomingConnected += self.incomingConnected
            self.__listenloop.onIncomingDisconnected += self.incomingDisconnected
            self.__listenloop.configureConnection()
            self.__listenloop.start()

    def powerOff(self) -> NoReturn:
        """Power Off the stargate

            Close and delete Listen and Send threads
        """
        if not self.powered:
            return
        if not self.disablelisten and self.__listenloop is not None:
            self.__listenloop.stop()
            self.__listenloop = None
        if not self.disablesend and self.__sendLoop is not None:
            self.__sendLoop.stop()
            self.__sendLoop = None
        self.powered = False

    def getAddressOnNetwork(self) -> List[int]:
        """Return the int sequence for this gate over the network

        Returns:
            List[int]: The stargate sequence
        """
        Ip = self.__listenloop.getAddress()
        Ip = SequenceToListInt(Ip)
        return IpToStargateCode(Ip)

    def dial(self, sequence: str) -> NoReturn:
        """Dial sequence.
        If ok -> connect to another stargate

        Args:
            sequence (str): the stargate sequence to dial
        """
        if not self.powered or self.connected or self.__sendLoop is not None:
            return

        # seach it in reserved sequences
        self.otherSequence = sequence
        if(sequence in self.reservedSequences):
            ip = self.reservedSequences[sequence]
        else:
            sequence = SequenceToListInt(sequence)
            ip = StargateCodeToIp(sequence)
            ip = ListIntToSequence(ip)

        # creating the connection
        self.__sendLoop = StargateSendLoop(self)
        self.__sendLoop.onOutConnectionStart += self.dialingStart
        self.__sendLoop.onOutConnected += self.outConnected
        self.__sendLoop.onOutConnectionError += self.outConnectionError
        self.__sendLoop.onOutDisconnected += self.outDisconnected

        self.__sendLoop.dial(ip, self.port)

    def disconnect(self) -> NoReturn:
        """Disconnect from another stargate
        """
        if not self.powered or not self.connected or self.__sendLoop is None:
            return

        self.__sendLoop.stop()
        self.__sendLoop = None
        self.connected = False

    def __resetConnectionInfo(self) -> NoReturn:
        """Reset connection infos
        """
        self.ipConnectedTo = None
        self.connected = False

    def dialingStart(self, sequence: str) -> NoReturn:
        """When dialing start

        Args:
            sequence (str): sequence to dial
        """
        self.dialFinish = False
        self.onDialingConnection.fire(
            self.otherSequence, self.dialSequenceFinish)

    def dialSequenceFinish(self) -> NoReturn:
        """Callback for when the dial sequence is finish
        """
        self.dialFinish = True

    def outConnected(self, sequence: str) -> NoReturn:
        """When out connected

        Args:
            sequence (str): sequence to dial
        """
        self.ipConnectedTo = sequence
        self.connected = True
        self.onDialingConnected.fire()
        start_new_thread(self.__timerClose, ())

    def outConnectionError(self) -> NoReturn:
        """When out fail to connect

        """
        self.__resetConnectionInfo()

    def outDisconnected(self) -> NoReturn:
        """When out disconnect
        """
        self.__resetConnectionInfo()
        self.onDialingDisconnection.fire()

    def incomingConnection(self, sequence) -> NoReturn:
        """When in connect

        Args:
            sequence (str): sequence from dial
        """
        if(sequence in self.reservedSequences.values()):
            sequence = list(self.reservedSequences.keys())[list(
                self.reservedSequences.values()).index(sequence)]
        else:
            sequence = SequenceToListInt(sequence)
            sequence = IpToStargateCode(sequence)
            sequence = ListIntToSequence(sequence)
        self.dialFinish = False
        self.onIncomingConnection.fire(sequence, self.dialSequenceFinish)

    def incomingConnected(self, sequence) -> NoReturn:
        """"When in connected

        Args:
            sequence (str): sequence from dial
        """
        self.connected = True
        self.ipConnectedTo = sequence
        self.onIncomingConnected.fire()

    def incomingDisconnected(self) -> NoReturn:
        """When out disconnect
        """
        self.__resetConnectionInfo()
        self.onIncomingDisconnection.fire()

    def sendDataText(self, msg: str) -> NoReturn:
        """Send text

        Args:
            msg (str): text to send

        """
        if not self.powered or not self.connected or self.__sendLoop is None:
            return
        self.__sendLoop.sendTroughGate("text.tp", msg)

    def sendDataFile(self, fileName: str) -> NoReturn:
        """Send file in base64 encoding

        Args:
            fileName (str): file name in absolute path

        """
        if not self.powered or not self.connected or self.__sendLoop is None:
            return
        try:
            file = open(fileName, "rb")
            datas = file.read()
            file.close()
            datas = (base64.b64encode(datas)).decode('ascii')
            fileName = os.path.basename(fileName)
            self.__sendLoop.sendTroughGate(fileName, datas)
        except Exception as e:
            print(e)
            pass

    def receiveDataText(self, msg: str) -> NoReturn:
        """Receive text

        Args:
            msg (str): the text received
        """
        self.onIncomingDataText.fire(msg)

    def receiveDataFile(self, fileName: str, payload: str) -> NoReturn:
        """Receive file

        Args:
            fileName (str): name of the file
            payload (str): contend in base64 encoding
        """
        path = os.path.join(os.getcwd(), "Gate Room")
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            file = open(os.path.join(path, fileName), "wb")
            datas = base64.b64decode(payload.encode('ascii'))
            file.write(datas)
            file.close()
            self.onIncomingDataFile.fire(fileName)
        except:
            pass

    def __timerClose(self) -> NoReturn:
        """Timer for 38 minuts disconnection
        """
        delay = 2280  # (38*60 seconds)
        startTime = time.time()
        while startTime + delay > time.time() and self.connected:
            time.sleep(1)
        if(self.connected):
            self.disconnect()
