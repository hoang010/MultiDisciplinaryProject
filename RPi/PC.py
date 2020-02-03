import socket
import threading
import queue
import time


class PC:

    def __init__(self, ip_address, port, text_color, size=1024):
        self.ip_address = ip_address
        self.port = port
        self.text_color = text_color
        self.size = size
        self.sock = socket.socket()
        self.sock.bind((self.ip_address, self.port))
        self.to_send_queue = queue.Queue()
        self.have_recv_queue = queue.Queue()

    def listen(self):
        print(self.text_color.BOLD +
              'Listening on port {}'.format(self.port)
              + self.text_color.ENDC)
        self.s.listen()

        try:
            conn_socket, addr = self.sock.accept()
            print(self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(addr, self.port)
                  + self.text_color.ENDC)
            threading.Thread(target=self.send_channel, args=(conn_socket, addr)).start()
            threading.Thread(target=self.recv_channel, args=(conn_socket, addr)).start()
            return conn_socket, addr

        except:
            raise Exception('Connection to {} failed/terminated'.format(addr))

    def recv_channel(self, conn_socket, addr):
        while True:
            data = conn_socket.recv(self.size)
            print(self.text_color.OKBLUE + "{} | PC Socket:".format(time.asctime()), end='')
            print(self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, addr)
                  + self.text_color.ENDC)
            if data:
                self.have_recv_queue.put(data)

    def send_channel(self, conn_socket, addr):
        while True:
            if self.to_send_queue:
                data = self.to_send_queue.get()
                print(self.text_color.OKBLUE + "{} | PC Socket:".format(time.asctime()), end='')
                print(self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, addr)
                      + self.text_color.ENDC)
                conn_socket.send(data)

    def disconnect(self):
        self.sock.close()
        print(self.text_color.OKGREEN +
              'Wifi socket closed successfully'
              + self.text_color.ENDC)
