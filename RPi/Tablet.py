import bluetooth


class Tablet:

    def __init__(self, host_mac_addr, text_color, backlog=1, size=1024):
        self.host_mac_addr = host_mac_addr
        self.backlog = backlog
        self.size = size
        self.text_color = text_color
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = bluetooth.PORT_ANY

    def connect(self):
        self.server_socket.bind((self.host_mac_addr, self.port))
        self.server_socket.listen(self.backlog)

        try:
            client, clientinfo = self.server_socket.accept()
            print(self.text_color.OKGREEN +
                  'Connected to ' + self.host_mac_addr
                  + self.text_color.ENDC)

        except:
            print(self.text_color.WARNING + 'Closing socket' + self.text_color.ENDC)
            client.close()
            self.server_socket.close()

    # TODO: write function to handle data streaming from Pi to Tablet
