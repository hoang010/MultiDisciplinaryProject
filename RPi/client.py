import socket
import queue
import threading
import time


class Client:
    def __init__(self, name, conn_type, rpi_ip, port, text_color, size=1024):
        """
        Function to create an intance of connection with Raspberry Pi
        :param name: String
                Name of connection
        :param conn_type: String
                Type of connection
        :param rpi_ip: String
                String containing Raspberry Pi IP address to connect to
        :param port: int
                Int containing port number to be used for the connection
        :param text_color: Class
                Class for colourised print statements
        :param size: int
                Int to declare size of data to read when data is received
        """
        self.name = name
        self.conn_type = conn_type
        self.rpi_ip = rpi_ip
        self.port = port
        self.text_color = text_color
        self.size = size
        self.sock = socket.socket()
        self.queue = queue.Queue()
        self.log_string = self.text_color.OKBLUE + \
                          "{} | {} socket: ".format(time.asctime(), self.name.upper())\
                          + self.text_color.ENDC

        # Set socket blocking to be True
        self.sock.setblocking(True)

        # Set socket to keep alive
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # Initialise variable to store thread
        self.queue_thread = None

    def connect(self):
        """
        Function to connect to Raspberry Pi

        Will create a thread to handle queue upon successful connection
        :return:
        """
        try:
            print(self.log_string + self.text_color.BOLD +
                  'Connecting to {}:{}'.format(self.rpi_ip, self.port)
                  + self.text_color.ENDC)

            self.sock.connect((self.rpi_ip, self.port))

            # Once connected, create a thread for sending data to Raspberry Pi
            self.queue_thread = threading.Thread(target=self.channel, args=(self.sock, self.rpi_ip))

            # Start the thread
            self.queue_thread.start()

            print(self.log_string + self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(self.rpi_ip, self.port)
                  + self.text_color.ENDC)

        except:
            raise Exception(self.log_string + "Connection to {}:{} failed".format(self.rpi_ip, self.port))

    def channel(self, conn_socket, addr):
        """
        Function to receive data from PC on the channel
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """

        # Print message to show that thread is started
        print(self.log_string + self.text_color.OKBLUE +
              "Thread for PC {} started".format(self.name.upper())
              + self.text_color.ENDC)

        if self.conn_type == 'recv':

            while True:

                time.sleep(1)

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Thread for PC {} alive".format(self.name.upper())
                      + self.text_color.ENDC)

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
                self.queue.put(data)

        else:
            while True:

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Thread for PC {} alive".format(self.name.upper())
                      + self.text_color.ENDC)

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.WARNING +
                      "Waiting for data to send"
                      + self.text_color.ENDC)

                time.sleep(1)

                if not self.queue.empty():
                    data = self.queue.get()

                    # Print message to show that thread is alive
                    print(self.log_string + self.text_color.OKBLUE +
                          "Data received from queue"
                          + self.text_color.ENDC)

                    # Display feedback whenever something is to be sent
                    print(self.log_string + self.text_color.BOLD +
                          'Sending "{}" to {}'.format(data, addr)
                          + self.text_color.ENDC)

                    # Finally, send the data to PC
                    conn_socket.send(data)

                    # Print message to show that thread is alive
                    print(self.log_string + self.text_color.OKBLUE +
                          "Data sent"
                          + self.text_color.ENDC)

    def disconnect(self):
        """
        Function to safely disconnect from Raspberry Pi
        :return:
        """
        self.queue_thread.join()
        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKGREEN +
              'PC {} thread closed successfully'.format(self.name.upper())
              + self.text_color.ENDC)

        # Shutdown socket
        self.sock.shutdown(socket.SHUT_RDWR)

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              '{} wifi socket closed successfully'.format(self.name)
              + self.text_color.ENDC)
