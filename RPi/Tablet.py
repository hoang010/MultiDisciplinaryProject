import bluetooth


class Tablet:

    def __init__(self, rpi_mac_addr, text_color, backlog=1, size=1024):
        self.rpi_mac_addr = rpi_mac_addr
        self.backlog = backlog
        self.size = size
        self.text_color = text_color
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = bluetooth.PORT_ANY

    def connect(self):
        self.server_socket.bind((self.rpi_mac_addr, self.port))
        self.server_socket.listen(self.backlog)

        try:
            client_sock, client_info = self.server_socket.accept()
            print(self.text_color.OKGREEN +
                  'Connected to ' + client_info
                  + self.text_color.ENDC)
            return client_sock, client_info

        except:
            print(self.text_color.WARNING + 'Closing bluetooth connection' + self.text_color.ENDC)
            client_sock.close()
            self.server_socket.close()

    def receive_data(self, client_sock):
        data = client_sock.recv(self.size)
        print(self.text_color.OKGREEN + 'Data "{}" received'.format(data) + self.text_color.ENDC)
        return data

    def send_data(self, client_sock, client_info, data):
        print(self.text_color.OKGREEN +
              'Sending data {} to {}'.format(data, client_info)
              + self.text_color.ENDC)

        try:
            client_sock.send(data)
            print(self.text_color.OKGREEN +
                  'Data {} successfully sent to {}'.format(data, client_info)
                  + self.text_color.ENDC)
            return True

        except:
            print(self.text_color.FAIL +
                  'Data failed to send'
                  + self.text_color.ENDC)
            return False
