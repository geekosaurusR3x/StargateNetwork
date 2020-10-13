from StargateNetwork.Stargate import Stargate
import time
import sys


def DialDisplay(sequence):
    print("Dialing symbols", end=" ")
    for i in sequence.split('.'):
        print(i, end=" ")
        time.sleep(0.5)
    print("")


def DialDisplayError(sequence):
    print("Dialing symbols", end=" ")
    for i in sequence.split('.'):
        print(i, end=" ")
        time.sleep(0.5)
    print("")


def IncomingDisplay(sequence):
    print("\033c", end="")
    print("Imcomning travelers from : ", end=" ")
    for i in sequence.split('.'):
        print(i, end=" ")
        time.sleep(0.5)
    print("")


def OpenVortexDisplay():
    print("Vortex created")


def CloseVortexDisplay():
    print("Vortex destroyed")


if __name__ == "__main__":
    choice = ""
    stargate = Stargate('', 6842)
    stargate.OnDialingConnection += DialDisplay
    stargate.OnIncomingConnection += IncomingDisplay

    stargate.OnDialingConnected += OpenVortexDisplay
    stargate.OnDialingDisconnection += CloseVortexDisplay

    stargate.OnIncomingConnected += OpenVortexDisplay
    stargate.OnIncomingDisconnection += CloseVortexDisplay

    while choice != "Exit":
        if not stargate.connected:
            print(stargate)
        print("--------Menu-------")
        if stargate.powered:
            if not stargate.disablesend and not stargate.connected:
                print("Dial")
            if not stargate.disablesend and stargate.connected:
                print("Send Data")
                print("Disconnect")
            print("Power Off")
            print("Exit")
        else:
            print("Disable Listen")
            print("Disable Call")
            print("Power On")
        choice = input("what is your choice ? ")
        if(choice == "Disable Listen"):
            stargate.disablelisten = True
        if(choice == "Disable Call"):
            stargate.disablesend = True
        if(choice == "Power On"):
            stargate.powerOn()
        if(choice == "Power Off"):
            stargate.powerOff()
        if(choice == "Dial" and not stargate.disablesend):
            sequence = input("Sequence to dial : ")
            stargate.dial(sequence)
        if(choice == "Disconnect" and not stargate.disablesend):
            stargate.disconnect()
    stargate.powerOff()
    sys.exit(0)
