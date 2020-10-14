from . import StargateListenLoop, StargateSendLoop, Helpers, EventHook


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

        self.OnDialingConnection = EventHook.EventHook()
        self.OnDialingConnected = EventHook.EventHook()
        self.OnDialingDisconnection = EventHook.EventHook()
        self.OnIncomingConnection = EventHook.EventHook()
        self.OnIncomingConnected = EventHook.EventHook()
        self.OnIncomingDisconnection = EventHook.EventHook()
        self.otherSequence = None
        self.dialFinish = False

    def __str__(self):
        return f"Stargate { self.getAdressOnNetwork() if self.powered and not self.disablelisten else None} \r\n\t Power state : {self.powered}\r\n\t Connection status : {self.connected} to {self.ipConnectedTo} \r\n\t Can Call : {not self.disablesend}\r\n\t Can Receve : {not self.disablelisten}"

    def powerOn(self):
        if(self.powered):
            return
        self.powered = True
        if not self.disablelisten:
            print('Start listening for incoming traveler')
            self.listenloop = StargateListenLoop.StargateListenLoop(
                self.host, self.port, self)
            self.listenloop.onIncomingConnection += self.onIncomingConnection
            self.listenloop.onIncomingConnected += self.onIncomingConnected
            self.listenloop.onIncomingDisconnected += self.onIncomingDisconnected
            self.listenloop.configureConnection()
            self.listenloop.start()

    def powerOff(self):
        if not self.powered:
            return
        if not self.disablelisten:
            self.listenloop.stop()
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
        self.sendLoop.onOutConnectionStart += self.onDialingStart
        self.sendLoop.onOutConnected += self.onOutConnected
        self.sendLoop.onOutConnectionError += self.onOutConnectionError
        self.sendLoop.onOutDisconnected += self.onOutDisconnected

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

    def onDialingStart(self, ip):
        self.dialFinish = False
        self.OnDialingConnection.fire(
            self.otherSequence, self.DialSequenceFinish)

    def DialSequenceFinish(self):
        self.dialFinish = True

    def onOutConnected(self, ip):
        self.ipConnectedTo = ip
        self.connected = True
        self.OnDialingConnected.fire()

    def onOutConnectionError(self):
        self.resetConnectionInfo()

    def onOutDisconnected(self):
        self.resetConnectionInfo()
        self.OnDialingDisconnection.fire()

    def onIncomingConnection(self, ip):
        if(ip in self.reservedSequences.values()):
            sequence = list(self.reservedSequences.keys())[list(
                self.reservedSequences.values()).index(ip)]
        else:
            ip = Helpers.SequenceToListInt(ip)
            sequence = Helpers.IpToStargateCode(ip)
            sequence = Helpers.ListIntToSequence(sequence)
        self.dialFinish = False
        self.OnIncomingConnection.fire(sequence, self.DialSequenceFinish)

    def onIncomingConnected(self, ip):
        self.connected = True
        self.ipConnectedTo = ip
        self.OnIncomingConnected.fire()

    def onIncomingDisconnected(self):
        self.resetConnectionInfo()
        self.OnIncomingDisconnection.fire()
