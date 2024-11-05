# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect
from qfluentwidgets import FluentIcon, setFont, InfoBarIcon

# from view.Ui_FocusInterface import Ui_FocusInterface
from resource.ui.Ui_FirmwareConfigInterface import Ui_FirmwareConfigInterface
import json

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

        # 加载配置
        self.load_config()
        # 连接信号
        self.lineEdit.textChanged.connect(self.save_config)
        self.lineEdit_2.textChanged.connect(self.save_config)
        self.lineEdit_3.textChanged.connect(self.save_config)

    def save_config(self):
        print("config changed, save file")
        config = {
            "lineEdit": self.lineEdit.text(),
            "lineEdit_2": self.lineEdit_2.text(),
            "lineEdit_3": self.lineEdit_3.text(),
        }
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(config, config_file)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as config_file:
                config = json.load(config_file)
                self.lineEdit.setText(config.get("path", ""))
        except FileNotFoundError:
            print("no config file")
            # 文件未找到时，创建新文件并写入默认参数
            with open(CONFIG_FILE, "w") as config_file:
                json.dump(DEFAULT_CONFIG, config_file)
            self.lineEdit.setText(DEFAULT_CONFIG["path"])  # 设置为默认路径

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as config_file:
                config = json.load(config_file)
                self.lineEdit.setText(config.get("lineEdit", ""))
                self.lineEdit_2.setText(config.get("lineEdit_2", ""))
                self.lineEdit_3.setText(config.get("lineEdit_3", ""))
        except FileNotFoundError:
            # 文件未找到时，创建新文件并写入默认参数
            with open(CONFIG_FILE, "w") as config_file:
                json.dump(DEFAULT_CONFIG, config_file)
            self.lineEdit.setText(DEFAULT_CONFIG["lineEdit"])
            self.lineEdit_2.setText(DEFAULT_CONFIG["lineEdit_2"])
            self.lineEdit_3.setText(DEFAULT_CONFIG["lineEdit_3"])