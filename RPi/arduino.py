import serial
import queue
import threading
import time


class Arduino:
    def __init__(self, arduino_name, text_color, size=1, timeout=1):
        """
        Function to create an instance of the connection with Arduino
        :param arduino_name: String
                String containing name of Arduino device
        :param text_color: Class
                Class for colourised print statements
        :param size: int
                Size of data for Serial instance to read at a time
        :param timeout: int
                Timeout before connection gets cut by Raspberry Pi
        """
        self.arduino_name = arduino_name
        self.text_color = text_color
        self.size = size
        self.lock = threading.Lock()
        self.log_string = self.text_color.OKBLUE + "{} | Arduino Socket: ".format(time.asctime()) + self.text_color.ENDC

        # Initialise a queue to store data for sending to Arduino device
        self.to_send_queue = queue.Queue()

        # Initialise a queue to store data received from Arduino device
        self.have_recv_queue = queue.Queue()

        try:

            # Display feedback so that user knows this function is called
            print(self.log_string + self.text_color.BOLD +
                  'Connecting to {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

            # Try to connect to the Arduino device
            self.arduino_serial = serial.Serial(self.arduino_name, timeout)

            # Display feedback
            print(self.log_string + self.text_color.BOLD +
                  'Connected to {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

            # Once connected, start a thread for receiving data from the Arduino device
            threading.Thread(target=self.recv_channel)

            # Once connected, start a thread for sending data to Arduino device
            threading.Thread(target=self.send_channel)

        except serial.SerialException:
            print(self.log_string + self.text_color.FAIL +
                  'Connection failed, check connection with Arduino!'
                  + self.text_color.ENDC)

        except ValueError:
            print(self.log_string + self.text_color.FAIL +
                  'Connection failed, check parameter values!'
                  + self.text_color.ENDC)

    def recv_channel(self):
        """
        Function to receive data from Arduino device

        Once data is received, data is put into self.have_recv_queue
        :return:
        """
        while True:

            while not self.lock.acquire(blocking=True):
                pass

            # Read data from connected socket
            data = self.arduino_serial.read(self.size)

            # Display feedback whenever something is received
            print(self.log_string + self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, self.arduino_name)
                  + self.text_color.ENDC)

            # Finally, store received data into self.have_recv_queue
            self.have_recv_queue.put(data)

            self.lock.release()

    def send_channel(self):
        """
        Function to send data to Arduino device

        Once there is a item in self.to_send_queue, this function will send that item to the Arduino device
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
                      'Sending "{}" to {}'.format(data, self.arduino_name)
                      + self.text_color.ENDC)

                # Finally, send the data to the Arduino device
                self.arduino_serial.write([data])

                self.lock.release()

    def disconnect(self):
        """
        Function to close Arduino serial
        :return:
        """

        # Close the serial
        self.arduino_serial.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              'Arduino serial closed successfully'
              + self.text_color.ENDC)

    def turn_left(self):
        self.to_send_queue.put('left')

    def turn_right(self):
        self.to_send_queue.put('right')

    def advance(self, num=1):
        self.to_send_queue.put(num)
