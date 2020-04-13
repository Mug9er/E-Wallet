from PyQt5.QtCore import Qt, pyqtSignal
import EWallet_Operator


class Signals(object):

    Refresh_signal = pyqtSignal()

    def __init__(self):
        super(Signals, self).__init__()


class Slots(object):

    def __int__(self):
        super(Slots, self).__int__()

    def Refresh_slot(self, ui):
        ui.COM_ComboBox.clear()
        ui.COM_ComboBox.addItems(EWallet_Operator.scan_COM())
        ui.Text.append("刷新成功")

