import serial
import time
port = "COM5"
ser = serial.Serial("COM5",115200)
ser.flushInput()


while True:
    tdata = ser.read()
    time.sleep(1)
    data_left = ser.inWaiting()
    tdata += ser.read(data_left)
    print("Data read: ")
    print(bytes.decode(tdata))
    try:
        cmd = input("Enter command: ")
        ser.write(str.encode(cmd))
    except:
        ser.write('0')
