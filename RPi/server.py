import socket
import threading
import queue
import time


class Server:
    def __init__(self, ip_address, port, text_color, size=1024):
        """
        Function to create an instance of connection with PC
        :param name: String
                Name of connection
        :param conn_type: String
                Type of connection
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
        self.log_string = self.text_color.OKBLUE + \
                          "{} | Server socket: ".format(time.asctime())\
                          + self.text_color.ENDC

        # Bind Raspberry Pi's own ip and port to the socket
        self.sock.bind((self.ip_address, self.port))

        # Initialise queue to store data for sending to PC
        self.to_send_queue = queue.Queue()
        self.have_recv_queue = queue.Queue()

        # Set socket to be blocking while listening
        self.sock.setblocking(True)

        # Set socket to keep alive
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # Initialise variable for threads
        self.send_thread = None
        self.recv_thread = None

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
        self.sock.listen(1)

        try:

            # Accept the request for connection
            conn_socket, addr = self.sock.accept()

            # Display feedback to let user know that a connection has been established
            print(self.log_string + self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(addr[0], self.port)
                  + self.text_color.ENDC)

            # Once connected, create a thread for sending data to PC
            self.send_thread = threading.Thread(target=self.send_channel, args=(conn_socket, addr))
            self.recv_thread = threading.Thread(target=self.recv_channel, args=(conn_socket, addr))

            # Start the thread
            self.send_thread.start()
            self.recv_thread.start()

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
        :param conn_type: String
                Contains name of type of connection
        :return:
        """
        # Print message to show that thread is started
        print(self.log_string + self.text_color.OKBLUE +
              "Thread for RPi recv_channel started"
              + self.text_color.ENDC)

        while True:

            # Print message to show that thread is alive
            print(self.log_string + self.text_color.WARNING +
                  "Waiting for data to receive"
                  + self.text_color.ENDC)

            # Read data from connected socket
            data = conn_socket.recv(self.size)

            # Print message to show that thread is alive
            print(self.log_string + self.text_color.OKBLUE +
                  "Data received from socket"
                  + self.text_color.ENDC)

            # Display feedback whenever something is to be received
            print(self.log_string + self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, addr)
                  + self.text_color.ENDC)

            # Finally, store data into self.have_recv_queue
            self.have_recv_queue.put(data)

    def send_channel(self, conn_socket, addr):
        # Print message to show that thread is started
        print(self.log_string + self.text_color.OKBLUE +
              "Thread for RPi send_channel started"
              + self.text_color.ENDC)

        while True:

            if not self.to_send_queue.empty():
                # Get data from socket
                data = self.to_send_queue.get()

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Data received from queue"
                      + self.text_color.ENDC)

                # Display feedback whenever something is to be received
                print(self.log_string + self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, addr)
                      + self.text_color.ENDC)

                # Finally, store data into self.have_recv_queue
                conn_socket.send(data)

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Data sent"
                      + self.text_color.ENDC)

    def disconnect(self):
        """
        Function to safely disconnect from connected PC
        :return:
        """

        self.send_thread.join()
        print(self.log_string + self.text_color.OKGREEN +
              'RPi send_channel thread closed successfully'
              + self.text_color.ENDC)

        self.recv_thread.join()
        print(self.log_string + self.text_color.OKGREEN +
              'RPi recv_channel thread closed successfully'
              + self.text_color.ENDC)

        # Shutdown socket
        self.sock.shutdown(socket.SHUT_RDWR)

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              'Wifi socket closed successfully'
              + self.text_color.ENDC)
