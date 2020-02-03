import serial
import queue
import threading


class Arduino:
    def __init__(self, arduino_name, text_color, size=1, timeout=1):
        self.arduino_name = arduino_name
        self.text_color = text_color
        self.size = size
        self.to_send_queue = queue.Queue()
        self.have_recv_queue = queue.Queue()

        try:
            self.arduino_serial = serial.Serial(self.arduino_name, timeout)
            threading.Thread(target=self.recv_channel)
            threading.Thread(target=self.send_channel)

        except serial.SerialException:
            print(self.text_color.FAIL +
                  'Connection failed, check connection with Arduino!'
                  + self.text_color.ENDC)

        except ValueError:
            print(self.text_color.FAIL +
                  'Connection failed, check parameter values!'
                  + self.text_color.ENDC)

    def recv_channel(self):
        while True:
            data = self.arduino_serial.read(self.size)
            print(self.text_color.BOLD +
                  'Received "{}" from {}'.format(data, self.arduino_name)
                  + self.text_color.ENDC)
            if data:
                self.have_recv_queue.put(data)

    def send_channel(self):
        while True:
            if self.to_send_queue:
                data = self.to_send_queue.get()
                print(self.text_color.BOLD +
                      'Sending "{}" to {}'.format(data, self.arduino_name)
                      + self.text_color.ENDC)
                self.arduino_serial.write(data)
