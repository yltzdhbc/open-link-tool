# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from qfluentwidgets import FluentIcon, setFont, InfoBarIcon

# from view.Ui_FocusInterface import Ui_FocusInterface
from resource.ui.Ui_FirmwareConfigInterface import Ui_FirmwareConfigInterface

from view.myConfig import userConfig

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "lineEdit": "glazer-maker-main-app-v10.0.0.1",
    "lineEdit_2": "glazer-maker-main-app-v10.0.0.1",
    "lineEdit_3": "glazer-maker-main-app-v10.0.0.1",
}


class FirmwareConfigInterface(Ui_FirmwareConfigInterface, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.__config = userConfig()

        # 加载配置
        self.load_config()
        # 连接信号
        self.lineEdit.textChanged.connect(self.save_config)
        self.lineEdit_2.textChanged.connect(self.save_config)
        self.lineEdit_3.textChanged.connect(self.save_config)

    def save_config(self):
        print("config changed, save file")
        self.__config.config.set("Settings", "fw_path_light", str(self.lineEdit.text()))
        self.__config.config.set("Settings", "fw_path_main", str(self.lineEdit_2.text()))
        self.__config.config.set("Settings", "fw_path_bottom", str(self.lineEdit_3.text()))
        self.__config.config_save()

    def load_config(self):
        test1 = self.__config.config.get("Settings", "fw_path_light", fallback="None")
        test2 = self.__config.config.get("Settings", "fw_path_bottom", fallback="None")
        test3 = self.__config.config.get("Settings", "fw_path_main", fallback="None")

        self.lineEdit.setText(test1)
        self.lineEdit_2.setText(test2)
        self.lineEdit_3.setText(test3)
