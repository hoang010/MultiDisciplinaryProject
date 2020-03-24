import socket
import queue
import threading
import time

import cv2 as cv
import struct
import pickle

class Client:
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
        self.log_string = self.text_color.OKBLUE + \
                          "{} | Client socket: ".format(time.asctime())\
                          + self.text_color.ENDC

        # Set socket blocking to be True
        self.sock.setblocking(True)

        # Set socket to keep alive
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # Initialise variable to store thread
        self.send_thread = None
        self.recv_thread = None

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

            print(self.log_string + self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(self.rpi_ip, self.port)
                  + self.text_color.ENDC)

        except:
            raise Exception(self.log_string + "Connection to {}:{} failed".format(self.rpi_ip, self.port))

    def recv(self):
        """
        Function to receive data from PC on the channel
        :param conn_socket: Socket
                Contains Socket used for connection
        :param addr: String
                Contains IP address of connected device
        :return:
        """

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.WARNING +
              "Waiting for data to receive"
              + self.text_color.ENDC)

        # Read data from connected socket
        data = self.sock.recv(self.size)

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Data received from socket"
              + self.text_color.ENDC)

        # Display feedback whenever something is to be received
        print(self.log_string + self.text_color.BOLD +
              'Received "{}"'.format(data)
              + self.text_color.ENDC)

        return data

    def recv_images(self):

        data = b""
        payload_size = struct.calcsize(">L")

        counter = 1
        recv = False

        while True:

            while len(data) < payload_size:
                print("Recv: {}".format(len(data)))
                data += self.sock.recv(4096)

            print("Done Recv: {}".format(len(data)))
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            print("msg_size: {}".format(msg_size))

            while len(data) < msg_size:
                data += self.sock.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = cv.imdecode(frame, cv.IMREAD_COLOR)
            cv.imwrite("./Algo/images/image{}.jpg".format(counter), frame)
            counter += 1

            if(counter > 1 and data == b""):
              break

    def send(self, data):

        # Display feedback whenever something is to be sent
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format(data)
              + self.text_color.ENDC)

        # Finally, send the data to PC
        self.sock.send(data)

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Data sent"
              + self.text_color.ENDC)

    def disconnect(self):
        """
        Function to safely disconnect from Raspberry Pi
        :return:
        """
        self.send_thread.join()
        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKGREEN +
              'PC send_channel thread closed successfully'
              + self.text_color.ENDC)

        self.recv_thread.join()
        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKGREEN +
              'PC recv_channel thread closed successfully'
              + self.text_color.ENDC)

        # Shutdown socket
        self.sock.shutdown(socket.SHUT_RDWR)

        # Close the socket
        self.sock.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              'Wifi socket closed successfully'
              + self.text_color.ENDC)
