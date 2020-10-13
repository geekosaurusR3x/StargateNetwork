from . import Helpers
import socket
import time
import threading


class Stargate (threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def waitForConnection(self):

        self.socket.bind((self.host, self.port))
        self.loop = True
        self.socket.listen(1)
        print('Start listening for incoming traveler')
        self.start()

    def run(self):
        while self.loop:
            try:
                c, addr = self.socket.accept()
                print(f'Got connection from {addr}')

                # send a thank you message to the client.
                c.send('Thank you for connecting')

                # Close the connection with the client
                c.close()
            except socket.timeout:
                pass

            time.sleep(0.01)

    def stop(self):
        self.loop = False
        print('Stop listening for incoming traveler')

    def getAdress(self):
        Ip = socket.gethostbyname(socket.gethostname())
        Ip = Helpers.SequenceToListInt(Ip)
        return Helpers.IpToStargateCode(Ip)
