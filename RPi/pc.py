import socket
import queue
import threading
import time


class PC:
    def __init__(self, rpi_ip, port, text_color, size=1024):
        """
        Function to create an intance of connection with Raspberry Pi
        :param rpi_ip: String
                String containing Raspberry Pi IP address to connect to
        :param port: int
                Int containing port number to be used for the connection
        :param text_color: Class
                Class for colourised print statements
        :param size: int
                Int to declare size of data to read when data is received
        """
        self.rpi_ip = rpi_ip
        self.port = port
        self.text_color = text_color
        self.size = size
        self.sock = socket.socket()
        self.to_send_queue = queue.Queue()
        self.have_recv_queue = queue.Queue()
        self.log_string = self.text_color.OKBLUE + "{} | PC Socket: ".format(time.asctime()) + self.text_color.ENDC

    def connect(self):
        try:
            print(self.log_string + self.text_color.BOLD +
                  'Connecting to ' + self.rpi_ip + ':' + self.port
                  + self.text_color.ENDC)

            self.sock.connect((self.rpi_ip, self.port))

            print(self.log_string + self.text_color.OKGREEN +
                  'Connected to ' + self.rpi_ip + ':' + self.port
                  + self.text_color.ENDC)

            # Once connected, start a thread for sending data to PC
            threading.Thread(target=self.send_channel, args=(self.sock, self.rpi_ip)).start()

            # Once connected, start a thread for receiving data from PC
            threading.Thread(target=self.recv_channel, args=(self.sock, self.rpi_ip)).start()

        except:
            raise Exception(self.log_string + "Connection to {}:{} failed".format(self.rpi_ip, self.port))

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
            print(self.log_string + self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, addr)
                  + self.text_color.ENDC)

            # Finally, store data into self.have_recv_queue
            self.have_recv_queue.put(data)

    def send_channel(self, conn_socket, addr):
        """
        Function to send data to Raspberry Pi on the channel
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
                print(self.log_string + self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, addr)
                      + self.text_color.ENDC)

                # Finally, send the data to PC
                conn_socket.send(data)

    def disconnect(self):
        """
        Function to safely disconnect from Raspberry Pi
        :return:
        """

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              'Wifi socket closed successfully'
              + self.text_color.ENDC)
