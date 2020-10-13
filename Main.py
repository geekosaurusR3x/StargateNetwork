from StargateNetwork.Stargate import Stargate
import time

if __name__ == "__main__":
    sg = Stargate('', 6842)
    sg.waitForConnection()
    time.sleep(5)
    sg.stop()
