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
        self.sock.setblocking(True)

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

            self.sock.connect(self.rpi_ip)

            # Once connected, start a thread for sending data to Raspberry Pi
            threading.Thread(target=self.channel, args=(self.sock, self.rpi_ip)).start()

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

        if self.conn_type == 'recv':

            while True:
                # Read data from connected socket
                data = conn_socket.recv(self.size)

                # Display feedback whenever something is to be received
                print(self.log_string + self.text_color.BOLD +
                      'Received "{}" from {}'.format(data, addr)
                      + self.text_color.ENDC)

                # Finally, store data into self.have_recv_queue
                self.queue.put(data)

        else:
            while True:

                data = self.queue.get()
                # Checks if there is anything in the queue
                if data:

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
              '{} wifi socket closed successfully'.format(self.name)
              + self.text_color.ENDC)
