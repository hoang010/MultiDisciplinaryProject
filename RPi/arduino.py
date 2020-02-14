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
        self.lock = threading.Lock()
        self.log_string = self.text_color.OKBLUE + \
                          "{} | Arduino Socket: ".format(time.asctime())\
                          + self.text_color.ENDC

        try:

            # Display feedback so that user knows this function is called
            print(self.log_string + self.text_color.BOLD +
                  'Connecting via {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

            # Try to connect to the Arduino device
            self.arduino_serial = serial.Serial(self.arduino_name, timeout)

            # Display feedback
            print(self.log_string + self.text_color.BOLD +
                  'Connected to {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

            # Once connected, start a thread for sending data to Arduino
            threading.Thread(target=self.recv_channel).start()

            # Once connected, start a thread for receiving data from Arduino
            threading.Thread(target=self.send_channel()).start()

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
        :return:
        """
        while True:

            # Check buffer if there is any data there
            buf_size = self.arduino_serial.inWaiting()

            # If there is
            if buf_size:

                # Get the lock
                self.lock.acquire()

                # Read all data from connected socket
                data = self.arduino_serial.read(buf_size)

                # Display feedback whenever something is received
                print(self.log_string + self.text_color.BOLD +
                      'Received "{}"'.format(data)
                      + self.text_color.ENDC)

                # Put into queue
                self.have_recv_queue.put(data)

                # Release lock
                self.lock.release()

    def send_channel(self):
        """
        Function to send data to Arduino device
        :return:
        """
        while True:
            # Get data from queue
            data = self.to_send_queue.get()

            # If there is data
            if data:

                # Get the lock
                self.lock.acquire()

                # Display feedback whenever something is to be sent
                print(self.log_string + self.text_color.BOLD +
                      'Sending "{}"'.format(data)
                      + self.text_color.ENDC)

                # Send the data to the Arduino device
                self.arduino_serial.write(data)

                # Release the lock
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
