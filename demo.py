# coding:utf-8
import sys
import time

from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import setTheme, Theme, FluentTranslator


from view.firmware_config_interface import FirmwareConfigInterface
from view.firmware_upgrade_interface import FirmwareUpgradeInterface
from view.myFluentWindows import myFluentWindow
import serial.tools.list_ports

import logging, serial
from lib_open_protocol.open_protocol import OpenProto
from lib_open_protocol.upgrade import Upgrade, ModuleInfoStruct
import os
from view.myConfig import userConfig

LOCAL_ADDR = 0x0103


class WorkerThread(QThread):
    update_signal = pyqtSignal(list)
    set_upgrade_state_signal = pyqtSignal(int, str)

    def __init__(self, firmwareUpgradeInterface):
        super().__init__()
        loglevel = logging.DEBUG
        logging.basicConfig(level=loglevel, format="%(message)s", datefmt="%S")
        self.port = None
        self.baud = "921600"
        self.fw_path = None
        self.dst_addr = None
        self.erase_num = None
        self.hwid = 0
        self.sn = 0
        self.upgrade_t = None
        self.upgrade_monitor_flag = 0
        self.query_enable = False
        self.download_enable = False
        self.modules = None
        self.selected_module_idx = 0
        self.selected_module_message = None
        self.selected_module_addr = None
        self.selected_module = None
        self.firmwareUpgradeInterface = firmwareUpgradeInterface

    def run(self):
        while True:
            if self.query_enable:
                self.serial_query_module()
                time.sleep(1)
            elif self.download_enable == True:
                self.download()
            time.sleep(1)

    def to_query(self):
        try:
            proto = OpenProto(self.port, self.baud, LOCAL_ADDR, logging)
            upgrade = Upgrade(proto, logging)
            modules = upgrade.query_ver()
            logging.debug("Upgrade: %d Module has been queried", len(modules))
            return modules
        except Exception as e:
            logging.debug("Error", "Queried Faild")
            return False

    def show_download_info(self, str):
        self.set_upgrade_state_signal.emit(self.selected_module_idx, str)

    def to_upgrade(self):
        if not isinstance(self.dst_addr, int):
            logging.debug("dst_addr error")
        if self.dst_addr < 0 or self.dst_addr > 0xFFFF:
            logging.debug("dst_addr out range")
        if not os.path.exists(self.fw_path):
            logging.debug("no firmware")
        try:
            proto = OpenProto(self.port, self.baud, LOCAL_ADDR, logging)
            # 查版本
            self.set_upgrade_state_signal.emit(self.selected_module_idx, "查询版本")
            self.upgrade = Upgrade(proto, logging)
            self.upgrade.download_info_signal.connect(self.show_download_info)
            # 绑定upgrade内的信号到本类中的函数，设置进度条
            self.upgrade.upgrade_progress_signal.connect(self.recv_progress_val)
            module = ModuleInfoStruct(0, 0, self.hwid, self.sn, self.dst_addr)
            self.set_upgrade_state_signal.emit(self.selected_module_idx, "下载中")
            # 下载固件
            self.upgrade.load_firmware(self.fw_path)
            self.upgrade.erase_num = self.erase_num
            self.upgrade_monitor_flag = 1
            ret = self.upgrade.download(module)
            self.set_upgrade_state_signal.emit(self.selected_module_idx, "下载完成")
            # 重启
            proto.open()
            proto.send_pack(module.addr, 0x0001, None, need_ack=False)
            proto.close()
            print("重启完成")

            # 等待1S后重新开启查询
            time.sleep(1)
            self.query_enable = True

            self.set_upgrade_state_signal.emit(self.selected_module_idx, "升级成功")

            if ret[0]:
                self.upgrade_monitor_flag = 255
            else:
                self.upgrade_monitor_flag = -1
        except Exception as e:
            self.upgrade_monitor_flag = -1
            return

    def download(self):
        module = None
        for temp_module in self.modules:
            if temp_module.addr == self.selected_module_addr:
                print(f"selected_module_addr : {hex(self.selected_module_addr)}")
                print(f"selected_module_idx : {hex(self.selected_module_idx)}")
                module = temp_module

        # module = self.selected_module
        # logging.debug("Upgrade: Select module %d/%d" % (self.selected_module_idx + 1, len(self.modules)))
        logging.debug(
            "Upgrade: Select Addr:0x%04x, APP:0x%08x, BL:0x%08x, HWID:%s,%s, "
            % (module.addr, module.app_ver, module.loader_ver, module.hw_id, module.sn)
        )
        self.fw_path = self.get_module_fw_path(self.selected_module_idx)
        if self.fw_path == None:
            return
        self.hwid = module.hw_id
        self.sn = module.sn
        self.dst_addr = module.addr
        self.to_upgrade()
        self.download_enable = False

    def get_module_fw_path(self, board_type):
        config = userConfig()
        if board_type == 0:
            fw_path = config.config.get("Settings", "fw_path_light")
        if board_type == 1:
            fw_path = config.config.get("Settings", "fw_path_main")
        if board_type == 2:
            fw_path = config.config.get("Settings", "fw_path_bottom")
        fw_path = "./firmwares/" + fw_path + ".bin"
        print(f"get fw_path: {fw_path}")
        return fw_path

    def serial_query_module(self):
        print("update_module_list")
        self.modules = self.to_query()
        if len(self.modules):
            self.update_signal.emit(self.modules)

    @pyqtSlot(str)
    def send_serial_port(self, message):
        """子线程接收主线程的信号并处理"""
        print(f"子线程 send_serial_port 收到消息: {message}")
        self.port = message

    @pyqtSlot(str)
    def start_or_stop_query(self, message):
        print(f"子线程收到消息: {message}")
        if message == "start":
            self.query_enable = True
        else:
            self.query_enable = False

    @pyqtSlot(str)
    def start_download(self, message):
        print(f"子线程收到消息: {message}")
        self.selected_module_message = message
        self.selected_module_idx = 0
        if message == "Glazer-Module-1":
            self.selected_module_idx = 0
            self.selected_module_addr = 0x0102
        elif message == "Glazer-Module-2":
            self.selected_module_idx = 1
            self.selected_module_addr = 0x0100
        else:
            self.selected_module_idx = 2
            self.selected_module_addr = 0x0101
        self.query_enable = False
        self.download_enable = True

    @pyqtSlot(float)
    def recv_progress_val(self, float_val):
        """子线程接收主线程的信号并处理"""
        int_val = int(float_val * 100)
        print(f"固件发送进度: {int_val}")
        self.firmwareUpgradeInterface.node.set_progress(self.selected_module_idx, int(float_val * 100))


class Window(myFluentWindow):
    # 创建信号
    send_serial_port_signal = pyqtSignal(str)
    start_stop_query_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.userConfig = userConfig()
        
        self._selected_port = None  # 私有变量用于存储选中的串口
        self.serial = None  # 串口对象
        self.serial_is_open = None  # 串口对象
        # create sub interface
        self.firmwareConfigInterface = FirmwareConfigInterface(self)
        self.firmwareUpgradeInterface = FirmwareUpgradeInterface(self)
        self.initNavigation()
        self.initWindow()
        self.comboBoxSerial.activated.connect(self.select_port)
        self.pushButtonSerial.clicked.connect(self.open_or_close_serial)  # 连接激活信号以选择串口

        # 初始化工作线程
        self.worker_thread = None
        self.start_task()
        self.firmwareUpgradeInterface.node.button_download_signal.connect(self.worker_thread.start_download)
        # 轮询串口，更新到串口选择器中
        self.update_serial_ports(first_init=True)
        self.select_port()
        self.timer_serial_list = QTimer()  # 创建定时器
        self.timer_serial_list.timeout.connect(self.update_serial_ports)  # 连接定时器的超时信号
        self.timer_serial_list.start(1000)

    def start_task(self):
        """启动工作线程"""
        if self.worker_thread is None or not self.worker_thread.isRunning():
            self.worker_thread = WorkerThread(self.firmwareUpgradeInterface)
            # 连接子线程的信号到主线程的槽函数
            self.worker_thread.update_signal.connect(self.update_module_lists)  # 连接信号
            self.worker_thread.set_upgrade_state_signal.connect(
                self.firmwareUpgradeInterface.node.set_upgrade_state_str
            )
            # 连接主线程的信号到子线程的槽函数
            self.send_serial_port_signal.connect(self.worker_thread.send_serial_port)
            self.start_stop_query_signal.connect(self.worker_thread.start_or_stop_query)
            self.worker_thread.start()  # 启动线程

    def stop_task(self):
        """停止工作线程"""
        if self.worker_thread:
            self.worker_thread.terminate()  # 强制结束线程（谨慎使用）
            self.worker_thread = None

    def update_module_lists(self, modules):
        num_of_modules = len(modules)
        print(f"num_of_modules: {num_of_modules}")
        for i in range(num_of_modules):
            if modules[i].addr == 0x0100:
                self.firmwareUpgradeInterface.node.set_selected_state(1)
                self.firmwareUpgradeInterface.node.set_info(
                    1, modules[i].app_ver, modules[i].loader_ver, modules[i].hw_id, modules[i].sn
                )
            elif modules[i].addr == 0x0101:
                self.firmwareUpgradeInterface.node.set_selected_state(2)
                self.firmwareUpgradeInterface.node.set_info(
                    2, modules[i].app_ver, modules[i].loader_ver, modules[i].hw_id, modules[i].sn
                )

    def open_or_close_serial(self):
        if self.pushButtonSerial.text() == "打开":  # 按下打开串口
            if self.check_serial_port():
                self.serial_is_open = True
                self.pushButtonSerial.setText("关闭")  # 打开成功，设置按钮文字为“关闭”
                self.start_stop_query_signal.emit("start")
        else:  # 按下关闭串口
            self.serial_is_open = False
            self.pushButtonSerial.setText("打开")
            self.start_stop_query_signal.emit("stop")
            print(f"已关闭串口")

    def check_serial_port(self):
        """检查串口是否可用"""
        try:
            serial_test = serial.Serial(self._selected_port)
            serial_test.close()
            return True
        except serial.SerialException:
            return False

    def select_port(self):
        self._selected_port = self.comboBoxSerial.currentText()  # 获取当前选中的串口
        self.send_serial_port_signal.emit(self._selected_port)
        self.userConfig.modify_config(self._selected_port)
        print(f"_selected_port: {self._selected_port}")

    def update_serial_ports(self, first_init=False):
        ports = serial.tools.list_ports.comports()  # 获取串口列表
        # 记录当前选中的串口值
        current_selection = self.comboBoxSerial.currentText()
        if first_init == True:
            com_name = self.userConfig.config.get("Settings", "com_name", fallback="Not Set")
            current_selection = str(com_name)
        else:
            # 清空原来的项
            self.comboBoxSerial.clear()
        # print(f"current_selection: {current_selection}")

        for port in ports:
            self.comboBoxSerial.addItem(port.device)  # 将串口号添加到 ComboBox
        # 如果当前选中的串口仍然存在列表中，保持选中状态
        if current_selection in [self.comboBoxSerial.itemText(i) for i in range(self.comboBoxSerial.count())]:
            index = self.comboBoxSerial.findText(current_selection)
            self.comboBoxSerial.setCurrentIndex(index)
        else:
            # 如果当前选中的串口不在新的列表中，清空选中项或设置为默认项
            self.comboBoxSerial.setCurrentIndex(-1)  # 设置为没有选中的状态，或者可以设置为一个默认串口

    def initNavigation(self):
        self.addSubInterface(self.firmwareUpgradeInterface, FIF.DOWNLOAD, "固件升级")
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.firmwareConfigInterface, FIF.SETTING, "固件配置")
        self.navigationInterface.addSeparator()
        self.navigationInterface.setExpandWidth(150)  # 设置导航栏宽度
        self.navigationInterface.setCollapsible(False)  # 导航栏不可收缩
        self.navigationInterface.setReturnButtonVisible(True)  # 返回按钮可见
        self.navigationInterface.setMenuButtonVisible(False)  # 菜单按钮不可见

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle("OPEN-LINK TOOL")
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
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
