from . import StargateListenLoop, StargateSendLoop, Helpers


class Stargate():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.listenloop = StargateListenLoop.StargateListenLoop(
            self.host, self.port)

        self.listenloop.configureConnection()
        self.sendLoop = None
        print('Connected to the network')
        print(self.getAdressOnNetwork())
        self.powered = False

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
        Ip = Helpers.SequenceToListInt(self.listenloop.getAddress())
        return Helpers.IpToStargateCode(Ip)

    def dial(self, sequence):
        if not self.powered and self.sendLoop is None:
            return
        sequence = Helpers.SequenceToListInt(sequence)
        ip = Helpers.StargateCodeToIp(sequence)
        ip = Helpers.ListIntToSequence(ip)
        self.sendLoop = StargateSendLoop.StargateSendLoop()
        print(f"connecting to {ip}")
        self.sendLoop.dial(ip, self.port)

    def disconnect(self):
        if self.sendLoop is not None:
            self.sendLoop.stop()
            self.sendLoop = None
