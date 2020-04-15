from PyQt5.QtCore import Qt, pyqtSignal, QObject
import EWallet_Operator
from UI import Ui_MainWindow


class Signals(QObject):

    Refresh_signal = pyqtSignal(Ui_MainWindow)

    Recv_signal = pyqtSignal(str, Ui_MainWindow)

    Serached_Card_signal = pyqtSignal(str, Ui_MainWindow)

    Read_kuai_signal = pyqtSignal(str, Ui_MainWindow)

    def __init__(self):
        super(Signals, self).__init__()


class Slots(QObject):

    def __int__(self):
        super(Slots, self).__int__()

    def Refresh_slot(self, ui):
        ui.COM_ComboBox.clear()
        ui.COM_ComboBox.addItems(EWallet_Operator.scan_COM())
        ui.Text.append("刷新成功")

    def Recv_slot(self, data, ui):
        ui.Text.append(data)

    def Serached_Card_slot(self, message, ui):
        ui.SerachedCard_TextEdit.setText(message)

    def Read_kuai_slot(self, message, ui):
        ui.Read_TextEdit.setText(message)