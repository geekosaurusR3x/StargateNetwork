from StargateNetwork.Stargate import Stargate
import time
import sys
from signal import signal, SIGINT

stargate = Stargate()


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    stargate.powerOff()
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    print('Starting the stargate')
    stargate.powerOn()
