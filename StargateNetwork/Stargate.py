from . import StargateListenLoop, StargateSendLoop, Helpers, EventHook
import base64
import os
import tempfile


class Stargate():

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.listenloop = None
        self.sendLoop = None
        self.powered = False
        self.connected = False
        self.ipConnectedTo = None
        self.disablelisten = False
        self.disablesend = False

        self.reservedSequences = {
            "38.38.38.38.38.38.38": "127.0.0.1"
        }

        self.onDialingConnection = EventHook.EventHook()
        self.onDialingConnected = EventHook.EventHook()
        self.onDialingDisconnection = EventHook.EventHook()
        self.onIncomingConnection = EventHook.EventHook()
        self.onIncomingConnected = EventHook.EventHook()
        self.onIncomingDisconnection = EventHook.EventHook()
        self.onIncomingDataText = EventHook.EventHook()
        self.onIncomingDataFile = EventHook.EventHook()

        self.otherSequence = None
        self.dialFinish = False

    def __str__(self):
        return f"Stargate { self.getAdressOnNetwork() if self.powered and not self.disablelisten else None} \r\n\t Power state : {self.powered}\r\n\t Connection status : {self.connected} to {self.ipConnectedTo} \r\n\t Can Call : {not self.disablesend}\r\n\t Can Receve : {not self.disablelisten}"

    def powerOn(self):
        if(self.powered):
            return
        self.powered = True
        if not self.disablelisten:
            self.listenloop = StargateListenLoop.StargateListenLoop(
                self.host, self.port, self)
            self.listenloop.onIncomingConnection += self.incomingConnection
            self.listenloop.onIncomingConnected += self.incomingConnected
            self.listenloop.onIncomingDisconnected += self.incomingDisconnected
            self.listenloop.configureConnection()
            self.listenloop.start()

    def powerOff(self):
        if not self.powered:
            return
        if not self.disablelisten and self.listenloop is not None:
            self.listenloop.stop()
        if not self.disablesend and self.sendLoop is not None:
            self.sendLoop.stop()
        self.powered = False

    def getAdressOnNetwork(self):

        Ip = self.listenloop.getAddress()
        Ip = Helpers.SequenceToListInt(Ip)
        return Helpers.IpToStargateCode(Ip)

    def dial(self, sequence):
        if not self.powered or self.connected or self.sendLoop is not None:
            return

        # seach it in reserved sequences
        self.otherSequence = sequence
        if(sequence in self.reservedSequences):
            ip = self.reservedSequences[sequence]
        else:
            sequence = Helpers.SequenceToListInt(sequence)
            ip = Helpers.StargateCodeToIp(sequence)
            ip = Helpers.ListIntToSequence(ip)

        # creating the connection
        self.sendLoop = StargateSendLoop.StargateSendLoop(self)
        self.sendLoop.onOutConnectionStart += self.dialingStart
        self.sendLoop.onOutConnected += self.outConnected
        self.sendLoop.onOutConnectionError += self.outConnectionError
        self.sendLoop.onOutDisconnected += self.outDisconnected

        self.sendLoop.dial(ip, self.port)

    def disconnect(self):
        if not self.powered or not self.connected or self.sendLoop is None:
            return

        self.sendLoop.stop()
        self.sendLoop = None
        self.connected = False

    def resetConnectionInfo(self):
        self.ipConnectedTo = None
        self.connected = False

    def dialingStart(self, ip):
        self.dialFinish = False
        self.onDialingConnection.fire(
            self.otherSequence, self.DialSequenceFinish)

    def DialSequenceFinish(self):
        self.dialFinish = True

    def outConnected(self, ip):
        self.ipConnectedTo = ip
        self.connected = True
        self.onDialingConnected.fire()

    def outConnectionError(self):
        self.resetConnectionInfo()

    def outDisconnected(self):
        self.resetConnectionInfo()
        self.onDialingDisconnection.fire()

    def incomingConnection(self, ip):
        if(ip in self.reservedSequences.values()):
            sequence = list(self.reservedSequences.keys())[list(
                self.reservedSequences.values()).index(ip)]
        else:
            ip = Helpers.SequenceToListInt(ip)
            sequence = Helpers.IpToStargateCode(ip)
            sequence = Helpers.ListIntToSequence(sequence)
        self.dialFinish = False
        self.onIncomingConnection.fire(sequence, self.DialSequenceFinish)

    def incomingConnected(self, ip):
        self.connected = True
        self.ipConnectedTo = ip
        self.onIncomingConnected.fire()

    def incomingDisconnected(self):
        self.resetConnectionInfo()
        self.onIncomingDisconnection.fire()

    def sendDataText(self, msg):
        if not self.powered or not self.connected or self.sendLoop is None:
            return
        self.sendLoop.sendTroughGate("text.tp", msg)

    def receiveDataText(self, msg):
        self.onIncomingDataText.fire(msg)

    def sendDataFile(self, fileName):
        if not self.powered or not self.connected or self.sendLoop is None:
            return
        try:
            file = open(fileName, "rb")
            datas = file.read()
            file.close()
            datas = (base64.b64encode(datas)).decode('ascii')
            fileName = os.path.basename(fileName)
            self.sendLoop.sendTroughGate(fileName, datas)
        except Exception as e:
            print(e)
            pass

    def receiveDataFile(self, fileName, payload):
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
