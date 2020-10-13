from . import StargateListenLoop, StargateSendLoop, Helpers


class Stargate():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.listenloop = StargateListenLoop.StargateListenLoop(
            self.host, self.port)

        self.listenloop.configureConnection()
        self.sendLoop = None
        print(self.getAdressOnNetwork())
        self.powered = False
        self.connected = False

        self.reservedSequences = {
            "39.39.39.39.39.39.39": "127.0.0.1"
        }

    def __str__(self):
        return f"Stargate {self.getAdressOnNetwork()} \r\n\t Power state : {self.powered}\r\n\t Connection status : {self.connected}"

    def powerOn(self):
        if(self.powered):
            return

        self.powered = True
        print('Start listening for incoming traveler')
        self.listenloop.start()

    def powerOff(self):
        if not self.powered:
            return
        self.powered = False
        print('Stop listening for incoming traveler')
        self.listenloop.stop()

    def getAdressOnNetwork(self):
        Ip = self.listenloop.getAddress()
        Ip = Helpers.SequenceToListInt(Ip)
        return Helpers.IpToStargateCode(Ip)

    def dial(self, sequence):
        if not self.powered and self.sendLoop is None:
            return

        # seach it in reserved sequences
        if(sequence in self.reservedSequences):
            ip = self.reservedSequences[sequence]
        else:
            sequence = Helpers.SequenceToListInt(sequence)
            ip = Helpers.StargateCodeToIp(sequence)
            ip = Helpers.ListIntToSequence(ip)
        self.sendLoop = StargateSendLoop.StargateSendLoop()
        print(f"connecting to {ip}")
        self.sendLoop.dial(ip, self.port)
        self.connected = True

    def disconnect(self):
        if self.sendLoop is not None:
            self.sendLoop.stop()
            self.sendLoop = None
            self.connected = False
