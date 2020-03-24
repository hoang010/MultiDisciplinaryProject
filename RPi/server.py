import socket
import threading
import queue
import time

import cv2 as cv
import numpy as np
import glob
import pickle
import struct

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
        self.conn_socket = None

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
            self.conn_socket, addr = self.sock.accept()

            # Display feedback to let user know that a connection has been established
            print(self.log_string + self.text_color.OKGREEN +
                  'Connected to {}:{}'.format(addr[0], self.port)
                  + self.text_color.ENDC)

        except:
            raise Exception('Connection to {} failed/terminated'.format(addr))

    def recv(self):
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

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.WARNING +
              "Waiting for data to receive"
              + self.text_color.ENDC)

        # Read data from connected socket
        data = self.conn_socket.recv(self.size)

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Data received from socket"
              + self.text_color.ENDC)

        # Display feedback whenever something is to be received
        print(self.log_string + self.text_color.BOLD +
              'Received "{}" '.format(data)
              + self.text_color.ENDC)

        # Finally, store data into self.have_recv_queue
        return data

    def send(self, data):

        # Display feedback whenever something is to be received
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format(data)
              + self.text_color.ENDC)

        # Finally, store data into self.have_recv_queue
        self.conn_socket.send(data)

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Data sent"
              + self.text_color.ENDC)

    def send_images(self):

        filepath = "./Algo/images/*.jpg"
        images = np.asarray([cv.imread(file) for file in glob.glob(filepath)])

        img_counter = 1
        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]

        for image in images:
            result, frame = cv.imencode('.jpg', image, encode_param)
            data = pickle.dumps(frame, 0)
            size = len(data)

            print("{}: {}".format(img_counter, size))
            self.conn_socket.sendall(struct.pack(">L", size) + data)

            img_counter += 1

    def send_image(self, num):

        filepath = "./Algo/images/img{}.jpg".format(str(num))
        image = np.asarray(cv.imread(filepath))
        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]

        result, frame = cv.imencode('.jpg', image, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)

        print("{}: {}".format(str(num), size))
        self.conn_socket.sendall(struct.pack(">L", size) + data)


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
