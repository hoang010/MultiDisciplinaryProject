import socket
import threading
import queue
import time


class Wifi:

    def __init__(self, ip_address, port, text_color, size=1024):
        """
        Function to create an instance of connection with PC
        :param ip_address: String
                String containing Raspberry Pi IP address
        :param port: int
                Int containing port number to be used for the connection
        :param text_color: Class
                Class for colourised print statements
        :param size: int
                Int to declare size of data to read when data is received
        """
        self.ip_address = ip_address
        self.port = port
        self.text_color = text_color
        self.size = size
        self.sock = socket.socket()
        self.lock = threading.Lock()
        self.log_string = self.text_color.OKBLUE + "{} | Wifi Socket: ".format(time.asctime()) + self.text_color.ENDC

        # Bind Raspberry Pi's own ip and port to the socket
        self.sock.bind((self.ip_address, self.port))

        # Initialise queue to store data for sending to PC
        self.to_send_queue = queue.Queue()

        # Initialise queue to store data received from PC
        self.have_recv_queue = queue.Queue()

        # Initialise queue to store stream received from PC
        self.to_stream_queue = queue.Queue()

    def listen(self):
        """
        Function to listen for requests for wifi connection
        :return:
        """
        # Display feedback so that user knows this function is called
        print(self.log_string + self.text_color.BOLD +
              'Wifi listening on port {}'.format(self.port)
              + self.text_color.ENDC)

        # Listen to requests for connecting
        self.sock.listen()

        try:

            # Accept the request for connection
            conn_socket, addr = self.sock.accept()

            # Display feedback to let user know that a connection has been established
            print(self.log_string + self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(addr, self.port)
                  + self.text_color.ENDC)

            # Once connected, start a thread for sending data to PC
            threading.Thread(target=self.send_channel, args=(conn_socket, addr)).start()

            # Once connected, start a thread for receiving data from PC
            threading.Thread(target=self.recv_channel, args=(conn_socket, addr)).start()

            # Once connected, start a thread for streaming data to PC
            threading.Thread(target=self.send_stream_channel, args=(conn_socket, addr)).start()

        except:
            raise Exception('Connection to {} failed/terminated'.format(addr))

    def recv_channel(self, conn_socket, addr):
        """
        Function to receive data from PC on the channel

        Once data is received, data is put into self.have_recv_queue
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """
        while True:

            while not self.lock.acquire(blocking=True):
                pass

            # Read data from connected socket
            data = conn_socket.recv(self.size)

            # Display feedback whenever something is to be received
            print(self.log_string + self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, addr)
                  + self.text_color.ENDC)

            # Finally, store data into self.have_recv_queue
            self.have_recv_queue.put(data)

            self.lock.release()

    def send_channel(self, conn_socket, addr):
        """
        Function to send data to PC on the channel

        Once there is a item in self.to_send_queue, this function will send that item to the PC
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """
        while True:

            # Checks if there is anything in the queue
            if self.to_send_queue:

                while not self.lock.acquire(blocking=True):
                    pass

                # De-queue the first item
                data = self.to_send_queue.get()

                # Display feedback whenever something is to be sent
                print(self.log_string + self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, addr)
                      + self.text_color.ENDC)

                # Finally, send the data to PC
                conn_socket.send(data)

                self.lock.release()

    def send_stream_channel(self, conn_socket, addr):
        """
        Function to send stream to PC on the channel

        Once there is a item in self.to_send_queue, this function will send that item to the PC
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """
        while True:

            # Checks if there is anything in the queue
            if self.to_stream_queue:

                while not self.lock.acquire(blocking=True):
                    pass

                # De-queue the first item
                data = self.to_stream_queue.get()

                # Finally, send the data to PC
                conn_socket.send(data)

                self.lock.release()

    def disconnect(self):
        """
        Function to safely disconnect from connected PC
        :return:
        """

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              'Wifi socket closed successfully'
              + self.text_color.ENDC)
