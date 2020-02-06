import serial
port = "COM5"
ser = serial.Serial("COM5",9600)
ser.flushInput()



while True:
    if ser.inWaiting() >0:
        inputValue = ser.readline()
        print(inputValue)
    try:
        cmd = input("Enter command: ")
        ser.write(str.encode(cmd))
    except:
        ser.write('0')