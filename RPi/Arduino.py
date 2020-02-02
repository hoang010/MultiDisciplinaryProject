import serial


class Arduino:
    def __init__(self, arduino_name, text_color, timeout=1):
        self.text_color = text_color

        try:
            self.s = serial.Serial(arduino_name, timeout)

        except serial.SerialException:
            print(self.text_color.FAIL +
                  'Connection failed, check connection with Arduino!'
                  + self.text_color.ENDC)

        except ValueError:
            print(self.text_color.FAIL +
                  'Connection failed, check parameter values!'
                  + self.text_color.ENDC)

    def send_data(self, data):
        try:
            self.s.write(data)
            print(self.text_color.OKGREEN +
                  'Data "{}" sent'.format(data)
                  + self.text_color.ENDC)

        except serial.SerialTimeoutException:
            print(self.text_color.FAIL +
                  'Time out exceeded!'
                  + self.text_color.ENDC)
