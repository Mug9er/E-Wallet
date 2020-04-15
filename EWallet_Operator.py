import serial
import time
import SignalandSlot

ButeRate_list = ["1200", "2400", "4800", "9600", "14400", "19200", "38400",
                                              "56000", "576000", "115200"]


def scan_COM():
    ser = serial.Serial()
    port_name = []
    i = 1
    while i < 100:
        name = 'COM' + str(i)
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


def send_message(ser, cmd, data):
    length = int(len(data) / 2)
    len_high = str(hex(int(length/256))).replace("0x", "")
    if len(len_high) != 2:
        len_high = '0' + len_high
    len_low = str(hex(int(length%256))).replace("0x", "")
    if len(len_low) != 2:
        len_low = '0' + len_low
    data_len = len_high + len_low
    message = "EECC00" + cmd + data_len + data + "00000D0A"
    try:
        ser.write(message.encode('utf-8'))
    except Exception as e:
        print(e)


def recv_message(ser, signals, parent):
    while parent.exit:
        _exit = parent.exit
        data = ser.read_all()
        if data != b'':
            data = data.decode('utf-8')
            if data[0:4] == 'EECC' and data[-8:] == '00000D0A' and data[8:10] == '03':
                analysis_rec_message(data, signals, parent.ui)
            else:
                signals.Recv_signal.emit("检测到无法识别的卡", parent.ui)

        time.sleep(1)
"""


回应
begin     status   CMD  type   len    data   end
EECC       00       03    03    0002   0400   00000D0A
           默认   
上位机
        CMD   type  select  len  data        end
EECC     01  03     00     0001  01      00000D0A
"""


def to_hex(data):
    value = 0
    for i in range(0, 4):
        value = value * 16
        if ord(data[i]) >= ord('a'):
            value += ord(data[i]) - ord('A') + 10
        else:
            value += ord(data[i]) - ord('0')
    return value


def analysis_rec_message(data, signals, ui):
    data_len = to_hex(data[10:14])
    message_data = data[14:14+data_len*2]
    cmd = data[6:8]
    status_code = data[4:6]
    if status_code == '10' or status_code == '11' or status_code == '12':
        signals.Recv_signal.emit("命令失败", ui)
    else:
        if cmd == '01':
            if status_code == '00':
                signals.Recv_signal.emit("请求卡类型成功: 返回值 %s" % message_data, ui)
            else:
                signals.Recv_signal.emit("请求卡类型失败", ui)
        elif cmd == '02':
            if status_code == '00':
                signals.Recv_signal.emit("寻卡成功: 卡号为 %s" % message_data, ui)
                signals.Serached_Card_signal.emit(message_data, ui)
                if len(message_data) < 8:
                    signals.Recv_signal.emit("卡号长度不足8位", ui)
            else:
                signals.Recv_signal.emit("寻卡失败", ui)
        elif cmd == '03':
            if status_code == '00':
                signals.Recv_signal.emit("选择卡片成功: 返回值位 %s" % message_data, ui)
            else:
                signals.Recv_signal.emit("选择卡片失败", ui)
        elif cmd == '04':
            if status_code == '00':
                signals.Recv_signal.emit("密钥认证成功", ui)
            else:
                signals.Recv_signal.emit("密钥认证失败", ui)
        elif cmd == '05':
            if status_code == '00':
                signals.Read_kuai_signal.emit(message_data, ui)
                if len(message_data) < 32:
                    signals.Recv_signal.emit("块数据长度不足16byte", ui)
        elif cmd == '07':
            if status_code == '00':
                signals.Recv_signal.emit("卡片休眠成功", ui)
            else:
                signals.Recv_signal.emit("卡片休眠失败", ui)
        elif cmd == '08':
            if status_code == '00':
                signals.Recv_signal.emit("卡片充值成功", ui)
            else:
                signals.Recv_signal.emit("卡片充值失败", ui)
        elif cmd == '09':
            if status_code == '00':
                signals.Recv_signal.emit("卡片扣费成功", ui)
            else:
                signals.Recv_signal.emit("卡片扣费失败", ui)
        elif cmd == '0A':
            if status_code == '00':
                signals.Recv_signal.emit("当前余额为: %s" % message_data, ui)
            else:
                signals.Recv_signal.emit("余额查询失败", ui)
        else:
            signals.Recv_signal.emit("检测到无法识别的卡", ui)


"""
卡号：
EECC00020300040400000000000D0A
读块
EECC0005030010000102030405060708090A0B0C0D0E0F00000D0A

"""