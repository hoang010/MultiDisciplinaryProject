from ..main import bcolors
import bluetooth


class Tablet:

    def __init__(self, host_mac_addr, backlog=1, size=1024):
        self.host_mac_addr = host_mac_addr
        self.backlog = backlog
        self.size = size

    def connect(self):
        server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = bluetooth.PORT_ANY
        server_socket.bind((self.host_mac_addr, port))
        server_socket.listen(self.backlog)

        try:
            client, clientinfo = server_socket.accept()
            print(bcolors.OKGREEN +
                  'Connected to ' + self.host_mac_addr
                  + bcolors.ENDC)

        except:
            print(bcolors.WARNING + 'Closing socket' + bcolors.ENDC)
            client.close()
            server_socket.close()
