from StargateNetwork.Stargate import Stargate
import time
import sys


if __name__ == "__main__":
    stargate = Stargate('', 6842)
    stargate.powerOn()
    stargate.powerOff()
    sys.exit(0)
