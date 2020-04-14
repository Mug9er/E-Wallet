import sys, serial
import SignalandSlot
import re
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from UI import Ui_MainWindow
import EWallet_Operator
import threading
import os


class EWallet(object):
    def __init__(self, master):
        self.parent = master
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.parent)
        self.signal = SignalandSlot.Signals()
        self.slot = SignalandSlot.Slots()
        self.ser = serial.Serial()
        self.exit = True
        self.run()

    def run(self):
        self.ui.COM_ComboBox.addItem('串口号')
        self.ui.ButaRate_ComboBox.addItems(EWallet_Operator.ButeRate_list)
        self.ui.ButaRate_ComboBox.setCurrentIndex(3)
        self.ui.Refresh_PushButton.clicked.connect(lambda: self.slot.Refresh_slot(self.ui))
        self.ui.OpenCom_PushButton.clicked.connect(self.open_port)
        self.ui.Close_PushButton.clicked.connect(self.close_port)
        self.ui.Refresh_PushButton.clicked.emit()
        self.ui.RequestAll_PushButton.clicked.connect(self.request_all_card)
        self.signal.Recv_signal.connect(self.slot.Recv_slot)

    def open_port(self):
        if self.ser.isOpen():
            self.ui.Text.append('端口 %s 已经打开, 请不要重复打开\n如果要打开其他串口,请关闭当前串口' % self.ser.portstr)
            return
        current_com = self.ui.COM_ComboBox.currentText()
        current_buterate = self.ui.ButaRate_ComboBox.currentText()
        if len(re.findall(r'COM.*?', current_com)):
            self.ser = EWallet_Operator.select_port(current_com, current_buterate)
            if self.ser.isOpen():
                self.ui.Text.append('%s 已经打开' % current_com)
                self.exit = True
            else:
                self.ui.Text.append('%s 打开失败' % current_com)
        else:
            self.ui.Text.append("请选择正确的端口号")

    def close_port(self, event):
        self.ser.close()
        com = self.ser.portstr
        if self.ser.isOpen():
            self.ui.Text.append('%s 关闭失败' % com)
        else:
            self.ui.Text.append('%s 关闭成功' % com)
            self.exit = False

    def request_all_card(self):
        data = "EECC01030000010100000D0A"
        EWallet_Operator.send_message(self.ser, data)
        threading.Thread(target=EWallet_Operator.recv_message, args=(self.ser, self.signal, self)).start()
        #if receive_message != 'None':
          #  self.ui.Text.append(receive_message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    Ewallet = EWallet(MainWindow)
    MainWindow.show()
    if app.exec() == 0:
        os._exit(0)
   # sys.exit(app.exec_())
