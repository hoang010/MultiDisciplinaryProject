import serial
import time
import queue
import threading


class Arduino:
    def __init__(self, arduino_name, text_color, timeout=1):
        """
        Function to create an instance of the connection with Arduino
        :param arduino_name: String
                String containing port name of Arduino device
        :param text_color: Class
                Class for colourised print statements
        :param timeout: int
                Timeout before connection gets cut by Raspberry Pi
        """
        self.arduino_name = arduino_name
        self.text_color = text_color
        self.have_recv_queue = queue.Queue()
        self.to_send_queue = queue.Queue()
        self.log_string = self.text_color.OKBLUE + \
                          "{} | Arduino Socket: ".format(time.asctime())\
                          + self.text_color.ENDC

        try:

            # Display feedback so that user knows this function is called
            print(self.log_string + self.text_color.BOLD +
                  'Connecting via {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

            # Try to connect to the Arduino device
            self.arduino_serial = serial.Serial(self.arduino_name, 9600)

            # Flush input in the buffer
            self.arduino_serial.flushInput()

            # Display feedback
            print(self.log_string + self.text_color.BOLD +
                  'Connected to {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

        except serial.SerialException:
            print(self.log_string + self.text_color.FAIL +
                  'Connection failed, check connection with Arduino!'
                  + self.text_color.ENDC)

        except ValueError:
            print(self.log_string + self.text_color.FAIL +
                  'Connection failed, check parameter values!'
                  + self.text_color.ENDC)

    def recv(self):
        """
        Function to receive data from Arduino device
        :return:
        """

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Reading data from serial buffer"
              + self.text_color.ENDC)

        # Read all data from connected socket
        data = self.arduino_serial.readline()

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Data received from serial buffer"
              + self.text_color.ENDC)

        # Display feedback whenever something is received
        print(self.log_string + self.text_color.BOLD +
              'Received "{}"'.format(data)
              + self.text_color.ENDC)

        return data

    def send(self, data):
        """
        Function to send data to Arduino device
        :return:
        """

        # Display feedback whenever something is to be sent
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format(data)
              + self.text_color.ENDC)

        # Send the data to the Arduino device
        self.arduino_serial.write(data)

        # Print message to show that thread is alive
        print(self.log_string + self.text_color.OKBLUE +
              "Data sent"
              + self.text_color.ENDC)

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
