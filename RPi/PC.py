import socket
import threading
import queue
import time


class PC:

    def __init__(self, ip_address, port, text_color, size=1024):
        """
        Function to create an instance of PC connection
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

        # Bind Raspberry Pi's own ip and port to the socket
        self.sock.bind((self.ip_address, self.port))

        # Initialise queue to store data for sending to PC
        self.to_send_queue = queue.Queue()

        # Initialise queue to store data received from PC
        self.have_recv_queue = queue.Queue()

    def listen(self):
        """
        Function to simulate listening for requests for connection
        :return:
        """
        # Display feedback so that user knows this function is called
        print(self.text_color.BOLD +
              'Listening on port {}'.format(self.port)
              + self.text_color.ENDC)

        # Listen to requests for connecting
        self.sock.listen()

        try:

            # Accept the request for connection
            conn_socket, addr = self.sock.accept()

            # Display feedback to let user know that a connection has been established
            print(self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(addr, self.port)
                  + self.text_color.ENDC)

            # Once connected, start a thread for sending data to PC
            threading.Thread(target=self.send_channel, args=(conn_socket, addr)).start()

            # Once connected, start a thread for receiving data from PC
            threading.Thread(target=self.recv_channel, args=(conn_socket, addr)).start()

        except:
            raise Exception('Connection to {} failed/terminated'.format(addr))

    def recv_channel(self, conn_socket, addr):
        """
        Function to receive data from PC on the channel
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """
        while True:
            # Read data from connected socket
            data = conn_socket.recv(self.size)

            # Display feedback whenever something is to be received
            print(self.text_color.OKBLUE + "{} | PC Socket:".format(time.asctime()), end='')
            print(self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, addr)
                  + self.text_color.ENDC)

            # Finally, store data into self.have_recv_queue
            self.have_recv_queue.put(data)

    def send_channel(self, conn_socket, addr):
        """
        Function to send data to PC on the channel
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """
        while True:

            # Checks if there is anything in the queue
            if self.to_send_queue:
                # De-queue the first item
                data = self.to_send_queue.get()

                # Display feedback whenever something is to be sent
                print(self.text_color.OKBLUE + "{} | PC Socket:".format(time.asctime()), end='')
                print(self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, addr)
                      + self.text_color.ENDC)

                # Finally, send the data to PC
                conn_socket.send(data)

    def disconnect(self):
        """
        Function to safely disconnect from connected PC
        :return:
        """

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.text_color.OKGREEN +
              'Wifi socket closed successfully'
              + self.text_color.ENDC)
