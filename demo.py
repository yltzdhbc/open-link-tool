# coding:utf-8
import sys
import time

from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
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


class Window(myFluentWindow):
    ui_update_info_sig = pyqtSignal(list)
    ui_update_state_sig = pyqtSignal(str)
    ui_update_btn_sig = pyqtSignal(int, str)
    ui_update_selected_state_sig = pyqtSignal(int, str)
    
    WORK_MODE_IDLE = 0
    WORK_MODE_QUERY = 1
    WORK_MODE_DOWNLOAD = 2

    def __init__(self):
        super().__init__()
        loglevel = logging.DEBUG
        logging.basicConfig(level=loglevel, format="%(message)s", datefmt="%S")
        self.userConfig = userConfig()
        machine_name, self.module_number, addr_list, name_list = self.userConfig.get_all_module_info_ofMachine(0)

        self._selected_port = None  # 私有变量用于存储选中的串口
        self.serial = None  # 串口对象
        # create sub interface
        self.firmwareConfigInterface = FirmwareConfigInterface(self)
        self.firmwareUpgradeInterface = FirmwareUpgradeInterface(self)
        self.firmwareUpgradeInterface.createModuleTree(machine_name, self.module_number, name_list)

        self.initNavigation()
        self.initWindow()
        self.comboBoxSerial.activated.connect(self.select_port)
        self.pushButtonSerial.clicked.connect(self.open_or_close_serial)  # 连接激活信号以选择串口

        # 轮询串口，更新到串口选择器中
        self.update_serial_ports(first_init=True)
        self.select_port()
        self.work_thread_start()

    def work_thread_start(self):
        self._work_mode = self.WORK_MODE_IDLE
        self.firmwareUpgradeInterface.node.button_download_signal.connect(self.start_download)
        self.ui_update_info_sig.connect(self.update_module_lists)
        self.ui_update_state_sig.connect(self.upload_info_str_set)
        self.ui_update_btn_sig.connect(self.firmwareUpgradeInterface.node.set_button_state)
        self.ui_update_selected_state_sig.connect(self.firmwareUpgradeInterface.node.set_selected_state)
        self.baud = "921600"
        self.erase_num = None
        self.modules = None
        self.selected_module_idx = 0
        self.selected_module_addr = None
        # 创建一个新线程
        self.thread = QThread()
        self.thread.run = self.work_thread_run
        self.thread.start()  # 启动线程

    def work_mode_change(self, mode):
        print(f"work mode change to:{mode}")
        self._work_mode = mode

    def work_thread_run(self):
        while True:
            if self._work_mode == self.WORK_MODE_IDLE:
                # print("WORK_MODE_IDLE")
                self.update_serial_ports()
                for j in range(self.module_number):
                    self.ui_update_btn_sig.emit(j, "off")
                    self.ui_update_selected_state_sig.emit(j, "off")
            elif self._work_mode == self.WORK_MODE_QUERY:
                # print("WORK_MODE_QUERY")
                self.modules = self.to_query()
                self.ui_update_info_sig.emit(self.modules)
            elif self._work_mode == self.WORK_MODE_DOWNLOAD:
                # print("WORK_MODE_DOWNLOAD")
                self.to_download()
                self.work_mode_change(self.WORK_MODE_QUERY)
            time.sleep(1)

    def to_query(self):
        try:
            proto = OpenProto(self._selected_port, self.baud, LOCAL_ADDR, logging)
            upgrade = Upgrade(proto, logging)
            modules = upgrade.query_ver()
            logging.debug("Upgrade: %d Module has been queried", len(modules))
            return modules
        except Exception as e:
            logging.exception("An exception occurred.")
            return False

    def to_download(self):
        self.ui_update_btn_sig.emit(self.selected_module_idx, "off")
        module = None
        for temp_module in self.modules:
            if temp_module.addr == self.selected_module_addr:
                print(f"selected_module_addr : {hex(self.selected_module_addr)}")
                print(f"selected_module_idx : {hex(self.selected_module_idx)}")
                module = temp_module
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

        if not isinstance(self.dst_addr, int):
            logging.debug("dst_addr error")
        if self.dst_addr < 0 or self.dst_addr > 0xFFFF:
            logging.debug("dst_addr out range")
        if not os.path.exists(self.fw_path):
            logging.debug("no firmware")
        try:
            proto = OpenProto(self._selected_port, self.baud, LOCAL_ADDR, logging)
            # 查版本
            self.ui_update_state_sig.emit('查询版本')
            self.upgrade = Upgrade(proto, logging)
            self.upgrade.download_info_signal.connect(self.upload_info_str_set)
            self.upgrade.upgrade_progress_signal.connect(self.upload_progress_val_set)
            module = ModuleInfoStruct(0, 0, self.hwid, self.sn, self.dst_addr)
            self.ui_update_state_sig.emit('下载中')
            # 下载固件
            self.upgrade.load_firmware(self.fw_path)
            self.upgrade.erase_num = self.erase_num
            ret, err = self.upgrade.download(module)
            if ret == True:
                self.ui_update_state_sig.emit('升级成功')
            else:
                self.ui_update_state_sig.emit('升级失败')
        except Exception as e:
            logging.exception("An exception occurred.")
            return

        self.download_enable = False

    def get_module_fw_path(self, board_type):
        fw_path = self.userConfig.get_module_fwPath_by_moduleIdx(0, board_type)
        fw_path = "./firmwares/" + fw_path + ".bin"
        print(f"get fw_path: {fw_path}")
        return fw_path

    @pyqtSlot(float)
    def upload_progress_val_set(self, float_val):
        """子线程接收主线程的信号并处理"""
        int_val = int(float_val * 100)
        print(f"固件发送进度: {int_val}")
        self.firmwareUpgradeInterface.node.set_progress(self.selected_module_idx, int(float_val * 100))

    @pyqtSlot(str)
    def upload_info_str_set(self, str):
        self.firmwareUpgradeInterface.node.set_upgrade_state_str(self.selected_module_idx, str)

    @pyqtSlot(str)
    def start_download(self, message):
        print(f"start_download: {message}")
        self.selected_module_idx = 0
        self.userConfig = userConfig()
        machine_name, module_number, addr_list, name_list = self.userConfig.get_all_module_info_ofMachine(0)
        target_idx = int(message)
        self.selected_module_idx = target_idx
        self.selected_module_addr = addr_list[self.selected_module_idx]
        print(f"target_idx: {target_idx}")
        print(f"selected_module_idx: {self.selected_module_idx}")
        print(f"selected_module_addr: {self.selected_module_addr}")
        self.work_mode_change(self.WORK_MODE_DOWNLOAD)

    def update_module_lists(self, modules):
        num_of_modules = len(modules)
        machine_name, module_number, addr_list, name_list = self.userConfig.get_all_module_info_ofMachine(0)
        print(f"num_of_modules: {num_of_modules}, module_number: {module_number}")
        module_state = list(0 for _ in range(module_number))
        for i in range(num_of_modules):
            for j in range(module_number):
                print(f"i: {i}, j: {j}, modules[i].addr: {modules[i].addr}, addr_list[j]: {addr_list[j]}")
                if modules[i].addr == addr_list[j]:
                    module_state[j] = 1
        print(f"module_state: {module_state}")
        for j in range(module_number):
            if module_state[j] == 1:
                self.firmwareUpgradeInterface.node.set_button_state(j, "on")
                self.firmwareUpgradeInterface.node.set_info(
                    j, modules[i].app_ver, modules[i].loader_ver, modules[i].hw_id, modules[i].sn
                )
            else:
                self.firmwareUpgradeInterface.node.set_button_state(j, "off")

    def open_or_close_serial(self):
        if self.pushButtonSerial.text() == "打开":  # 按下打开串口
            if self.check_serial_port():
                self.pushButtonSerial.setText("关闭")  # 打开成功，设置按钮文字为“关闭”
                self.work_mode_change(self.WORK_MODE_QUERY)
        else:  # 按下关闭串口
            self.pushButtonSerial.setText("打开")
            self.work_mode_change(self.WORK_MODE_IDLE)
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
