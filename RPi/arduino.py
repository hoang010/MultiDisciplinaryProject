import serial
import threading
import time


class Arduino:
    def __init__(self, arduino_name, text_color, size=1, timeout=1):
        """
        Function to create an instance of the connection with Arduino
        :param arduino_name: String
                String containing port name of Arduino device
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
        self.log_string = self.text_color.OKBLUE + \
                          "{} | Arduino Socket: ".format(time.asctime())\
                          + self.text_color.ENDC

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

        # Read data from connected socket
        data = self.arduino_serial.read(self.size)

        # Display feedback whenever something is received
        print(self.log_string + self.text_color.BOLD +
              'Received "{}"'.format(data)
              + self.text_color.ENDC)

        return data

    def send(self, msg):
        """
        Function to send data to Arduino device
        :param msg: String or int
                Data to send to arduino using serial.read()
        :return:
        """
        # Display feedback whenever something is to be sent
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format(msg)
              + self.text_color.ENDC)

        # Finally, send the data to the Arduino device
        self.arduino_serial.write(msg)

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
        """
        Function to send String to arduino to turn left
        :return:
        """
        # Send the string indicating left to the Arduino device
        # Display feedback whenever something is to be sent
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format('left')
              + self.text_color.ENDC)

        # Send left to arduino
        self.arduino_serial.write('left')

    def turn_right(self):
        """
        Function to send String to arduino to turn right
        :return:
        """
        # Send the string indicating left to the Arduino device
        # Display feedback whenever something is to be sent
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format('right')
              + self.text_color.ENDC)

        # Send right to arduino
        self.arduino_serial.write('right')

    def advance(self, num=1):
        """
        Function to send String to arduino to advance num grids
        :param num: int
                Integer to represent how much should arduino advance
        :return:
        """
        # Display feedback whenever something is to be sent
        print(self.log_string + self.text_color.BOLD +
              'Sending "{}"'.format(num)
              + self.text_color.ENDC)

        # Send the int indicating how much to move forward to the Arduino device
        self.arduino_serial.write(num)
