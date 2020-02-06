import socket
import threading
import queue
import time


class Server:
    def __init__(self, name, conn_type,  ip_address, port, text_color, size=1024):
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
        self.name = name
        self.conn_type = conn_type
        self.ip_address = ip_address
        self.port = port
        self.text_color = text_color
        self.size = size
        self.sock = socket.socket()
        self.lock = threading.Lock()
        self.log_string = self.text_color.OKBLUE + \
                          "{} | {} socket: ".format(time.asctime(), self.name.upper())\
                          + self.text_color.ENDC

        # Bind Raspberry Pi's own ip and port to the socket
        self.sock.bind((self.ip_address, self.port))

        # Initialise queue to store data for sending to PC
        self.queue = queue.Queue()

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
            threading.Thread(target=self.channel, args=(conn_socket, addr)).start()

        except:
            raise Exception('Connection to {} failed/terminated'.format(addr))

    def channel(self, conn_socket, addr):
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

                # Read data from connected socket
                if data:

                    # Display feedback whenever something is to be received
                    print(self.log_string + self.text_color.BOLD +
                          'Sent "{}" to {}'.format(data, addr)
                          + self.text_color.ENDC)

                    # Finally, store data into self.have_recv_queue
                    conn_socket.send(data)

    def disconnect(self):
        """
        Function to safely disconnect from connected PC
        :return:
        """

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              '{} wifi socket closed successfully'.format(self.name)
              + self.text_color.ENDC)
