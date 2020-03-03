import serial
import time
port = "COM5"
ser = serial.Serial("COM5",115200)
ser.flushInput()
#command list
#1. Check connection
#2. Retrieve Sensor Values
#Format is: Comma seperated, beginning with X_SENDDATA:
#e.g.: X_SENDDATA: {TopRight:14.00; TopLeft:8.00; RightSide:6.00; LeftSide:26.00; TopCenter:16.00}
#3. Move Forward
#4. Turn Left
#5. Turn Right
#6. Move Backward

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
