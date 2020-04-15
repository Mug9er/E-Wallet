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
        self.signal.Serached_Card_signal.connect(self.slot.Serached_Card_slot)
        self.signal.Read_kuai_signal.connect(self.slot.Read_kuai_slot)
        self.ui.RequestAwake_PushButton.clicked.connect(self.request_awake_card)
        self.ui.SerachCard_PushButton.clicked.connect(self.search_card)
        self.ui.Choose_PushButton.clicked.connect(self.chooce_card)
        self.ui.PasswordA_PushButton.clicked.connect(self.password_a)
        self.ui.PasswordB_PushButton.clicked.connect(self.password_b)
        self.ui.Read_PushButton.clicked.connect(self.Read_kuai)
        self.ui.Write_PushButton.clicked.connect(self.Write_kuai)
        self.ui.Sleep_PushButton.clicked.connect(self.sleep_card)
        self.ui.RechargeAccept_PushButton.clicked.connect(self.Recharge_card)
        self.ui.DeductionAccept_PushButton.clicked.connect(self.Deduction_card)
        self.ui.BalanceRequest_PushButton.clicked.connect(self.Balance_card)

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
                threading.Thread(target=EWallet_Operator.recv_message, args=(self.ser, self.signal, self)).start()
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
        EWallet_Operator.send_message(self.ser, "01", "01")

    def request_awake_card(self):
        EWallet_Operator.send_message(self.ser, "01", "00")

    def search_card(self):
        EWallet_Operator.send_message(self.ser, '02', '00')

    def chooce_card(self):
        card_number = self.ui.SerachedCard_TextEdit.toPlainText()
        if len(card_number) < 8:
            self.ui.Text.append("卡号长度不足8位")
            return
        EWallet_Operator.send_message(self.ser, '03', card_number)

    def password_a(self):
        password = self.ui.PasswordA_TextEdit.toPlainText()
        kuai = self.ui.KuaiAcess_TextEdit.toPlainText()
        if kuai == "":
            self.ui.Text.append("块地址位空，请输入块地址")
            return
        card_number = self.ui.SerachedCard_TextEdit.toPlainText()
        if len(card_number) < 8:
            self.ui.Text.append("卡号长度不足8位")
            return
        EWallet_Operator.send_message(self.ser, '03', "00" + kuai + password + card_number)

    def password_b(self):
        password = self.ui.PasswordB_TextEdit.toPlainText()
        kuai = self.ui.KuaiAcess_TextEdit.toPlainText()
        if kuai == "":
            self.ui.Text.append("块地址位空，请输入块地址")
            return
        card_number = self.ui.SerachedCard_TextEdit.toPlainText()
        if len(card_number) < 8:
            self.ui.Text.append("卡号长度不足8位")
            return
        EWallet_Operator.send_message(self.ser, '03', "01" + kuai + password + card_number)

    def Read_kuai(self):
        kuai = self.ui.KuaiAcess_TextEdit.toPlainText()
        if kuai == "":
            self.ui.Text.append("块地址位空，请输入块地址")
            return
        EWallet_Operator.send_message(self.ser, '05', kuai)

    def Write_kuai(self):
        kuai = self.ui.KuaiAcess_TextEdit.toPlainText()
        if kuai == "":
            self.ui.Text.append("块地址位空，请输入块地址")
            return
        kuai_data = self.ui.Write_TextEdit.toPlainText()
        if len(kuai_data) < 32:
            self.ui.Text.append('块数据长度不足16byte')
            return
        EWallet_Operator.send_message(self.ser, '06', kuai+kuai_data)

    def sleep_card(self):
        EWallet_Operator.send_message(self.ser, '07', '00')

    def Recharge_card(self):
        recharge_money = self.ui.Recharge_TextEdit.toPlainText()
        if recharge_money == "":
            self.ui.Text.append('充值数额不能为空')
            return
        recharge_money = str(hex(int(recharge_money))).replace("0x", "")
        length = len(recharge_money)
        recharge_money = '0' * (8-length) + recharge_money
        EWallet_Operator.send_message(self.ser, '08', recharge_money)

    def Deduction_card(self):
        deduction_money = self.ui.Deduction_TextEdit.toPlainText()
        if deduction_money == "":
            self.ui.Text.append('扣费数额不能为空')
            return
        deduction_money = str(hex(int(deduction_money))).replace("0x", "")
        length = len(deduction_money)
        deduction_money = '0' * (8 - length) + deduction_money
        EWallet_Operator.send_message(self.ser, '08', deduction_money)

    def Balance_card(self):
        EWallet_Operator.send_message(self.ser, '09', '00')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    Ewallet = EWallet(MainWindow)
    MainWindow.show()
    if app.exec() == 0:
        os._exit(0)
   # sys.exit(app.exec_())
