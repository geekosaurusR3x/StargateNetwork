from StargateNetwork.Stargate import Stargate
import time
import sys

if __name__ == "__main__":
    choice = ""
    stargate = Stargate('', 6842)

    while choice != "Exit":
        print("--------Menu-------")
        print("Power On")
        print("Power Off")
        print("Dial")
        print("Exit")
        choice = input("what is your choice ? ")
        if(choice == "Power On"):
            stargate.powerOn()
        if(choice == "Power Off"):
            stargate.powerOff()
        if(choice == "Dial"):
            sequence = input("Sequence to dial : ")
            stargate.dial(sequence)
    stargate.powerOff()
    sys.exit(0)
