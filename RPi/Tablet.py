import bluetooth
import queue
import threading


class Tablet:

    def __init__(self, rpi_mac_addr, text_color, backlog=1, size=1024):
        self.rpi_mac_addr = rpi_mac_addr
        self.backlog = backlog
        self.size = size
        self.text_color = text_color
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = bluetooth.PORT_ANY
        self.server_socket.bind((self.rpi_mac_addr, self.port))
        self.to_send_queue = queue.Queue()
        self.have_recv_queue = queue.Queue()

    def listen(self):
        self.server_socket.listen(self.backlog)

        try:
            client_sock, client_info = self.server_socket.accept()
            print(self.text_color.OKGREEN +
                  'Connected to ' + client_info
                  + self.text_color.ENDC)
            threading.Thread(target=self.send_channel, args=(client_sock, client_info)).start()
            threading.Thread(target=self.recv_channel, args=(client_sock, client_info)).start()
            return client_sock, client_info

        except:
            raise Exception('An error occurred while establishing connection with {}'.format(client_info))

    def recv_channel(self, client_sock, client_info):
        while True:
            data = client_sock.recv(self.size)
            print(self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, client_info)
                  + self.text_color.ENDC)
            if data:
                self.have_recv_queue.put(data)

    def send_channel(self, client_sock, client_info):
        while True:
            if self.to_send_queue:
                data = self.to_send_queue.get()
                print(self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, client_info)
                      + self.text_color.ENDC)
                client_sock.send(data)

    def disconnect(self):
        self.server_socket.close()
        print(self.text_color.OKGREEN +
              'Bluetooth socket closed successfully'
              + self.text_color.ENDC)
