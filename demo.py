# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import setTheme, Theme, FluentTranslator


from view.firmware_config_interface import FirmwareConfigInterface
from view.firmware_upgrade_interface import FirmwareUpgradeInterface
from view.myFluentWindows import myFluentWindow
import serial.tools.list_ports


# class Window(SplitFluentWindow):
class Window(myFluentWindow):

    def __init__(self):
        super().__init__()
        self._selected_port = None  # 私有变量用于存储选中的串口
        self.serial = None  # 串口对象
        # create sub interface
        self.firmwareConfigInterface = FirmwareConfigInterface(self)
        self.firmwareUpgradeInterface = FirmwareUpgradeInterface(self)
        # 定义一下串口打开相关的逻辑
        self.comboBoxSerial.clicked.connect(self.select_port)  # 连接激活信号以选择串口
        # 定义打开串口的按钮的信号
        self.pushButtonSerial.clicked.connect(
            self.open_or_close_serial
        )  # 连接激活信号以选择串口
        self.initNavigation()
        self.initWindow()
        self.timer = QTimer()  # 创建定时器
        self.timer.timeout.connect(self.send_query)  # 连接定时器的超时信号
        # 轮询串口，更新到串口选择器中
        self.timer_serial_list = QTimer()  # 创建定时器
        self.timer_serial_list.timeout.connect(
            self.update_serial_ports
        )  # 连接定时器的超时信号
        self.timer_serial_list.start(1000)

    def send_query(self):
        if self.serial and self.serial.is_open:
            query_command = b"QUERY\n"  # 替换为你的查询指令
            try:
                self.serial.write(query_command)
                print("发送查询指令:", query_command)
            except serial.SerialException as e:
                print(f"发送指令失败，关闭串口: {e}")
                self.serial.close()  # 关闭之前的串口
                self.pushButtonSerial.setText("打开")
                self.serial = None

    def open_or_close_serial(self):
        if self.serial:
            self.serial.close()  # 关闭之前的串口
        if self.pushButtonSerial.text() == "打开":  # 按下打开串口
            try:
                self.serial = serial.Serial(
                    self._selected_port, baudrate=9600, timeout=1
                )
                self.pushButtonSerial.setText("关闭")  # 打开成功，设置按钮文字为“关闭”
                print(f"成功打开串口")
                # 如果查询定时器没有打开的话，打开查询定时器，每一段时间查询串口
                if not self.timer.isActive():
                    self.timer.start(2000)  # 每2秒发送一次查询指令
            except serial.SerialException as e:
                print(f"无法打开串口: {e}")  # 如果打开失败，显示错误信息
        else:  # 按下关闭串口
            if self.serial:
                self.serial.close()  # 关闭之前的串口
            self.pushButtonSerial.setText("打开")
            self.timer.stop()  # 停止定时器
            print(f"已关闭串口")

    def select_port(self):
        self._selected_port = self.comboBoxSerial.currentText()  # 获取当前选中的串口
        print(f"已选择串口: {self._selected_port}")  # 更新标签显示选中的串口

    def update_serial_ports(self):
        self.comboBoxSerial.clear()  # 清空现有选项
        ports = serial.tools.list_ports.comports()  # 获取串口列表
        for port in ports:
            self.comboBoxSerial.addItem(port.device)  # 将串口号添加到 ComboBox
        if ports:  # 判断 ports 是否不为空
            self.select_port()  # 自动选择第一个串口
        print("串口列表已更新")  # 更新标签提示

    def initNavigation(self):
        # add sub interface
        self.addSubInterface(self.firmwareConfigInterface, FIF.SETTING, "固件配置")
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.firmwareUpgradeInterface, FIF.DOWNLOAD, "固件升级")
        self.navigationInterface.addSeparator()
        # 设置导航栏宽度
        self.navigationInterface.setExpandWidth(150)
        # 导航栏不可收缩
        self.navigationInterface.setCollapsible(False)
        # 返回按钮可见
        self.navigationInterface.setReturnButtonVisible(True)
        # 菜单按钮不可见
        self.navigationInterface.setMenuButtonVisible(False)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle("OPEN-LINK TOOL")

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = Window()
    w.show()
    app.exec_()
