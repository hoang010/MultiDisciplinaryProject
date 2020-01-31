from ..main import bcolors
import socket


class PC:

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port

    def connect(self):
        s = socket.socket()
        print(bcolors.BOLD +
              'Connecting to ' + self.ip_address + ':' + self.port
              + bcolors.ENDC)

        try:
            s.connect((self.ip_address, self.port))
            print(bcolors.OKGREEN +
                  'Connected to ' + self.ip_address + ':' + self.port
                  + bcolors.ENDC)

        except:
            print(bcolors.FAIL + 'Connection failed/terminated' + bcolors.ENDC)
