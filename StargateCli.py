from stargate_network.stargate import Stargate
from _thread import start_new_thread
import time
import sys
import os


class StargateMenu():

    def __init__(self, stargate):
        self.stargate = stargate

        self.stargate.onDialingConnection += self.dialDisplayThread
        self.stargate.onIncomingConnection += self.incomingDisplayThread

        self.stargate.onDialingConnected += self.openVortexDisplay
        self.stargate.onIncomingConnected += self.openVortexDisplay

        self.stargate.onDialingDisconnection += self.closeVortexDisplay
        self.stargate.onIncomingDisconnection += self.closeVortexDisplay
        self.stargate.onIncomingDisconnection += self.printMenu

        self.stargate.onIncomingDataText += self.displayReceivedText
        self.stargate.onIncomingDataFile += self.displayReceivedFile

    def dialDisplayThread(self, sequence, callback):
        start_new_thread(self.SequenceDisplay,
                         ("Dialing sequence : ", sequence, callback))

    def incomingDisplayThread(self, sequence, callback):
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

    def openVortexDisplay(self):
        print("Vortex created")

    def closeVortexDisplay(self):
        print("Vortex destroyed")

    def displayReceivedFile(self, fileName):
        fileSize = os.path.getsize(fileName)
        print("File receive :")
        print("\t Name : {fileName}")
        print("\t Size : {fileSize}")

    def displayReceivedText(self, msg):
        print("Message received : ")
        print("\t"+msg)

    def printMenu(self):
        if not self.stargate.connected:
            print(stargate)
        print("--------Menu-------")
        if self.stargate.powered:
            if not self.stargate.disablesend and not self.stargate.connected:
                print("Dial")
            if not self.stargate.disablesend and self.stargate.connected:
                print("Send Text")
                print("Send File")
                print("Disconnect")
            print("Power Off")
        else:
            print("Disable Listen")
            print("Disable Call")
            print("Power On")
        print("Exit")

    def menuLoop(self):
        choice = ""
        while choice != "Exit":
            self.printMenu()
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
            if(choice == "Send Text" and not self.stargate.disablesend and self.stargate.powered):
                msg = input("What to send : ")
                self.stargate.sendDataText(msg)
            if(choice == "Send File" and not self.stargate.disablesend and self.stargate.powered):
                file = input("File to send (absolute path): ")
                self.stargate.sendDataFile(file)
            if(choice == "Disconnect" and not self.stargate.disablesend and self.stargate.powered):
                self.stargate.disconnect()
                while self.stargate.connected:
                    time.sleep(0.001)
        stargate.powerOff()

    def displayDHD(self):
        print("DHD")
        for i in range(0, 39):
            if (i % 15) == 0 and i != 0:
                print("")
            print(f" {i}" if i < 10 else i, end=' | ')
        print("")
        return input("Sequence to dial (dot between each symbols): ")


if __name__ == "__main__":
    choice = ""
    stargate = Stargate()
    stargateCli = StargateMenu(stargate)
    stargateCli.menuLoop()
    sys.exit(0)
