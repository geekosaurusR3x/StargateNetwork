from StargateNetwork.Stargate import Stargate
from _thread import start_new_thread
import time
import sys
import os


class StargateMenu():

    def __init__(self, stargate):
        self.stargate = stargate
        self.stargate.OnDialingConnection += self.DialDisplayThread
        self.stargate.OnIncomingConnection += self.IncomingDisplayThread

        self.stargate.OnDialingConnected += self.OpenVortexDisplay
        self.stargate.OnIncomingConnected += self.OpenVortexDisplay

        self.stargate.OnDialingDisconnection += self.CloseVortexDisplay
        self.stargate.OnIncomingDisconnection += self.CloseVortexDisplay

    def DialDisplayThread(self, sequence, callback):
        start_new_thread(self.SequenceDisplay,
                         ("Dialing sequence : ", sequence, callback))

    def IncomingDisplayThread(self, sequence, callback):
        os.system('cls' if os.name == 'nt' else 'clear')
        start_new_thread(self.SequenceDisplay,
                         ("Incoming travelers from : ", sequence, callback, False))

    def SequenceDisplay(self, msg, sequence, callback, dial=True):
        timeout = 3
        startTime = 0
        print(msg, end=" ")
        index = 1
        for i in sequence.split('.'):
            if index == 7 and dial:
                startTime = time.time()
                while startTime + timeout > time.time() and not self.stargate.connected:  # wait 3 second or stargate connected
                    time.sleep(0.0001)
                if not self.stargate.connected:
                    print("Not Locked")
                else:
                    print(i)
            else:
                print(i, end=" ")
            index += 1
            time.sleep(0.5)
        print("")
        callback()

    def OpenVortexDisplay(self):
        print("Vortex created")

    def CloseVortexDisplay(self):
        print("Vortex destroyed")

    def MenuLoop(self):
        choice = ""
        while choice != "Exit":
            if not self.stargate.connected:
                print(stargate)
            print("--------Menu-------")
            if self.stargate.powered:
                if not self.stargate.disablesend and not self.stargate.connected:
                    print("Dial")
                if not self.stargate.disablesend and self.stargate.connected:
                    print("Send Data")
                    print("Disconnect")
                print("Power Off")
            else:
                print("Disable Listen")
                print("Disable Call")
                print("Power On")
            print("Exit")

            choice = input("what is your choice ? ")
            if(choice == "Disable Listen" and not self.stargate.powered):
                self.stargate.disablelisten = True
            if(choice == "Disable Call" and not self.stargate.powered):
                self.stargate.disablesend = True
            if(choice == "Power On" and not self.stargate.powered):
                self.stargate.powerOn()
            if(choice == "Power Off" and self.stargate.powered):
                self.stargate.powerOff()
            if(choice == "Dial" and not self.stargate.disablesend and self.stargate.powered):
                sequence = self.displayDHD()
                self.stargate.dial(sequence)
                while not self.stargate.connected:
                    time.sleep(0.001)
            if(choice == "Disconnect" and not self.stargate.disablesend and self.stargate.powered):
                self.stargate.disconnect()
        stargate.powerOff()

    def displayDHD(self):
        for i in range(0, 39):
            if (i % 15) == 0 and i != 0:
                print("")
            print(f" {i}" if i < 10 else i, end=' | ')
        print("")
        return input("Sequence to dial : ")


if __name__ == "__main__":
    choice = ""
    stargate = Stargate('', 6842)
    stargateCli = StargateMenu(stargate)
    stargateCli.MenuLoop()
    sys.exit(0)
