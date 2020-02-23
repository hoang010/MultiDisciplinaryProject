import serial
import time
import queue
import threading


class Arduino:
    def __init__(self, arduino_name, text_color):
        """
        Function to create an instance of the connection with Arduino
        :param arduino_name: String
                String containing port name of Arduino device
        :param text_color: Class
                Class for colourised print statements
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
            self.arduino_serial = serial.Serial(self.arduino_name, 115200)

            # Flush input in the buffer
            self.arduino_serial.flushInput()

            # Display feedback
            print(self.log_string + self.text_color.BOLD +
                  'Connected to {}'.format(self.arduino_name)
                  + self.text_color.ENDC)

            # Once connected, create a thread for sending data to Arduino
            self.recv_thread = threading.Thread(target=self.recv_channel)

            # Once connected, create a thread for receiving data from Arduino
            self.send_thread = threading.Thread(target=self.send_channel())

            # Start the threads
            self.recv_thread.start()
            self.send_thread.start()

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
        # Print message to show that thread is started
        print(self.log_string + self.text_color.OKBLUE +
              "Thread for {} recv_channel started".format(self.arduino_name)
              + self.text_color.ENDC)

        while True:

            # Print message to show that thread is alive
            print(self.log_string + self.text_color.OKBLUE +
                  "Thread for {} recv_channel alive".format(self.arduino_name)
                  + self.text_color.ENDC)

            # Print message to show that thread is alive
            print(self.log_string + self.text_color.WARNING +
                  "Checking buffer size"
                  + self.text_color.ENDC)

            # Check buffer if there is any data there
            buf_size = self.arduino_serial.inWaiting()

            # If there is
            if buf_size:

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Reading data from serial buffer"
                      + self.text_color.ENDC)

                # Read all data from connected socket
                data = self.arduino_serial.read(buf_size)

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Data received from serial buffer"
                      + self.text_color.ENDC)

                # Display feedback whenever something is received
                print(self.log_string + self.text_color.BOLD +
                      'Received "{}"'.format(data)
                      + self.text_color.ENDC)

                # Put into queue
                self.have_recv_queue.put(data)

    def send_channel(self):
        """
        Function to send data to Arduino device
        :return:
        """

        # Print message to show that thread is started
        print(self.log_string + self.text_color.OKBLUE +
              "Thread for {} recv_channel started".format(self.arduino_name)
              + self.text_color.ENDC)

        while True:

            # Print message to show that thread is alive
            print(self.log_string + self.text_color.OKBLUE +
                  "Thread for {} send_channel alive".format(self.arduino_name)
                  + self.text_color.ENDC)

            # If there is data
            if not self.to_send_queue.empty():

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.WARNING +
                      "Reading data from queue"
                      + self.text_color.ENDC)

                # Get data from queue
                data = self.to_send_queue.get()

                # Print message to show that thread is alive
                print(self.log_string + self.text_color.OKBLUE +
                      "Data received from queue"
                      + self.text_color.ENDC)

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

        # Close thread for recv channel
        self.recv_thread.join()
        print(self.log_string + self.text_color.OKGREEN +
              'Arduino serial recv thread closed successfully'
              + self.text_color.ENDC)

        # Close thread for send channel
        self.send_thread.join()
        print(self.log_string + self.text_color.OKGREEN +
              'Arduino serial send thread closed successfully'
              + self.text_color.ENDC)

        # Close the serial
        self.arduino_serial.close()

        # Display feedback to let user know that this function is called successfully
        print(self.log_string + self.text_color.OKGREEN +
              'Arduino serial closed successfully'
              + self.text_color.ENDC)
