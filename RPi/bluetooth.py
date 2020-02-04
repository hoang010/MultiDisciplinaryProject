import bluetooth
import queue
import threading
import time


class Bluetooth:

    def __init__(self, rpi_mac_addr, text_color, backlog=1, size=1024):
        """
        Function to initialise an instance of connection with bluetooth device
        :param rpi_mac_addr: String
                String containing MAC address of Raspberry Pi
        :param text_color: Class
                Class for colourised print statements
        :param backlog: int
                Int for declaring how many device can be connected
        :param size: int
                Int to declare size of data to read when data is received
        """
        self.rpi_mac_addr = rpi_mac_addr
        self.backlog = backlog
        self.size = size
        self.text_color = text_color

        # Declare Bluetooth connection protocol
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        # Declare Bluetooth connection port
        self.port = bluetooth.PORT_ANY

        # Bind Raspberry Pi's own mac and port to the socket
        self.server_socket.bind((self.rpi_mac_addr, self.port))

        # Initialise queue to store data for sending to PC
        self.to_send_queue = queue.Queue()

        # Initialise queue to store data received from PC
        self.have_recv_queue = queue.Queue()

    def listen(self):
        """
        Function to listen for requests for bluetooth connection
        :return:
        """

        # Display feedback so that user knows this function is called
        print(self.text_color.OKGREEN +
              'Bluetooth listening on port ' + self.port
              + self.text_color.ENDC)

        # Listen for requests
        self.server_socket.listen(self.backlog)

        try:

            # Accept the connection
            client_sock, client_info = self.server_socket.accept()

            # Display feedback to let user know that a connection has been established
            print(self.text_color.OKGREEN +
                  'Connected to ' + client_info
                  + self.text_color.ENDC)

            # Once connected, start a thread for sending data to PC
            threading.Thread(target=self.send_channel, args=(client_sock, client_info)).start()

            # Once connected, start a thread for receiving data from PC
            threading.Thread(target=self.recv_channel, args=(client_sock, client_info)).start()

        except:
            raise Exception('An error occurred while establishing connection with {}'.format(client_info))

    def recv_channel(self, client_sock, client_info):
        """
        Function to receive data from tablet from the channel

        Once data is received, data is put into self.have_recv_queue
        :param client_sock: Socket
                Contains Socket used for connection
        :param client_info: String
                Contains MAC address of connected device
        :return:
        """
        while True:

            # Read data from connected socket
            data = client_sock.recv(self.size)
            print(self.text_color.OKBLUE + "{} | Bluetooth socket:".format(time.asctime()), end='')
            print(self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, client_info)
                  + self.text_color.ENDC)

            # Finally, store data into self.have_recv_queue
            self.have_recv_queue.put(data)

    def send_channel(self, client_sock, client_info):
        """
        Function to send data to tablet from the channel

        Once there is a item in self.to_send_queue, this function will send that item to the tablet
        :param client_sock: Socket
                Contains Socket used for connection
        :param client_info: String
                Contains MAC address of connected device
        :return:
        """
        while True:

            # Checks if there is anything in the queue
            if self.to_send_queue:

                # De-queue the first item
                data = self.to_send_queue.get()

                # Display feedback whenever something is to be sent
                print(self.text_color.OKBLUE + "{} | Bluetooth socket:".format(time.asctime()), end='')
                print(self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, client_info)
                      + self.text_color.ENDC)

                # Finally, send the data to PC
                client_sock.send(data)

    def disconnect(self):
        """
        Function to safely disconnect from connected tablet
        :return:
        """

        # Close the socket
        self.server_socket.close()

        # Display feedback to let user know that this function is called successfully
        print(self.text_color.OKGREEN +
              'Bluetooth socket closed successfully'
              + self.text_color.ENDC)
