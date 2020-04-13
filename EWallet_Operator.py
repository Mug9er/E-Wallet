import serial

ButeRate_list = ["1200", "2400", "4800", "9600", "14400", "19200", "38400",
                                              "56000", "576000", "115200"]


def scan_COM():
    ser = serial.Serial()
    port_name = []
    i = 1
    while i < 100:
        name = 'COM' + str(i)
        #ser.open
        try:
            ser.is_open
            ser = serial.Serial(name)
            port_name.append(name)
        except serial.serialutil.SerialException as e:
            pass
        i += 1
    return port_name


def select_port(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate)
    except serial.serialutil.SerialException:
        ser.close()
        ser = serial.Serial(port, baudrate)
    return ser


def send_message(ser, message):
    try:
        ser.write(message.encode('utf-8'))
    except Exception as e:
        print(e)