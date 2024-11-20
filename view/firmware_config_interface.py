# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from qfluentwidgets import FluentIcon, setFont, InfoBarIcon
from resource.ui.Ui_FirmwareConfigInterface import Ui_FirmwareConfigInterface
from view.myConfig import userConfig


class FirmwareConfigInterface(Ui_FirmwareConfigInterface, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self._config = userConfig()
        self.load_config()
        self.lineEdit_0.textChanged.connect(self.text_change)
        self.lineEdit_1.textChanged.connect(self.text_change)
        self.lineEdit_2.textChanged.connect(self.text_change)
        self.lineEdit_3.textChanged.connect(self.text_change)
        self.lineEdit_4.textChanged.connect(self.text_change)
        self.pushButton_saveConfig.clicked.connect(self.save_config)

    def text_change(self):
        print("text_change")
        self._config.config.set("MACHINE-0", "module0_fw_path", str(self.lineEdit_0.text()))
        self._config.config.set("MACHINE-0", "module1_fw_path", str(self.lineEdit_1.text()))
        self._config.config.set("MACHINE-0", "module2_fw_path", str(self.lineEdit_2.text()))
        self._config.config.set("MACHINE-0", "module3_fw_path", str(self.lineEdit_3.text()))
        self._config.config.set("MACHINE-0", "module4_fw_path", str(self.lineEdit_4.text()))

    def save_config(self):
        print("save_config")
        self._config.config_save()

    def load_config(self):
        test1 = self._config.config.get("MACHINE-0", "module0_fw_path", fallback="None")
        test2 = self._config.config.get("MACHINE-0", "module1_fw_path", fallback="None")
        test3 = self._config.config.get("MACHINE-0", "module2_fw_path", fallback="None")
        test4 = self._config.config.get("MACHINE-0", "module3_fw_path", fallback="None")
        test5 = self._config.config.get("MACHINE-0", "module4_fw_path", fallback="None")
        self.lineEdit_0.setText(test1)
        self.lineEdit_1.setText(test2)
        self.lineEdit_2.setText(test3)
        self.lineEdit_3.setText(test4)
        self.lineEdit_4.setText(test5)
        machine_name, module_number, addr_list, name_list = self._config.get_all_module_info_ofMachine(0)
        self.label_module_0.setText(name_list[0])
        self.label_module_1.setText(name_list[1])
        self.label_module_2.setText(name_list[2])
        self.label_module_3.setText(name_list[3])
        self.label_module_4.setText(name_list[4])
        self.label_0.setText(machine_name)
