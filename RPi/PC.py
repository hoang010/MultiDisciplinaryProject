import socket


class PC:

    def __init__(self, ip_address, port, text_color):
        self.ip_address = ip_address
        self.port = port
        self.text_color = text_color
        self.s = socket.socket()

    def connect(self):
        self.s.bind((self.ip_address, self.port))
        print(self.text_color.BOLD +
              'Listening on port: {}'.format(self.port)
              + self.text_color.ENDC)
        self.s.listen()

        try:
            conn_socket, addr = self.s.accept()
            print(self.text_color.OKGREEN +
                  'Connected to ' + addr
                  + self.text_color.ENDC)
            return conn_socket, addr

        except:
            print(self.text_color.FAIL + 'Connection failed/terminated' + self.text_color.ENDC)

    # TODO: write function to handle streaming data from Pi camera to PC
    # TODO: write function to handle retrieving data from PC to Pi
