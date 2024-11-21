# coding:utf-8
import configparser


class userConfig:
    def __init__(self):
        super().__init__()
        # 配置文件路径
        self.config_file = "config.ini"
        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.ensure_config_exists()
        self.config.read(self.config_file, encoding="utf-8")
        self.update_display()

    def ensure_config_exists(self):
        """确保配置文件存在，且有必需的节和选项。"""
        # 如果配置文件不存在，创建并写入默认值
        if not self.config.read(self.config_file, encoding="utf-8"):
            print(f"{self.config_file} 不存在，正在创建默认配置文件。")
            self.config.add_section("Settings")
            self.config.set("Settings", "com_name", "COM1")

            self.config.add_section("User")
            self.config.set("User", "username", "admin")
            self.config.set("User", "password", "12345678")

            self.config.add_section("MACHINE-0")
            self.config.set("MACHINE-0", "machine_name", "Galzer-Maker")
            self.config.set("MACHINE-0", "module_number", "5")
            self.config.set("MACHINE-0", "module0_addr", "0x0100")
            self.config.set("MACHINE-0", "module0_name", "ESP32")
            self.config.set("MACHINE-0", "module0_path", "None")
            self.config.set("MACHINE-0", "module1_addr", "0x0200")
            self.config.set("MACHINE-0", "module1_name", "灯板")
            self.config.set("MACHINE-0", "module1_path", "None")
            self.config.set("MACHINE-0", "module2_addr", "0x0300")
            self.config.set("MACHINE-0", "module2_name", "主板")
            self.config.set("MACHINE-0", "module2_path", "None")
            self.config.set("MACHINE-0", "module3_addr", "0x0400")
            self.config.set("MACHINE-0", "module3_name", "底板")
            self.config.set("MACHINE-0", "module3_path", "None")
            self.config.set("MACHINE-0", "module4_addr", "0x0500")
            self.config.set("MACHINE-0", "module4_name", "步进")
            self.config.set("MACHINE-0", "module4_path", "None")

            # 保存创建的配置文件
            with open(self.config_file, "w", encoding="utf-8") as configfile:
                self.config.write(configfile)
            print(f"已创建默认配置文件：{self.config_file}")

    def update_display(self):
        # 从配置中读取并显示参数
        com_name = self.config.get("Settings", "com_name", fallback="Not Set")
        # print(display_text)

    def modify_config(self, com_name):
        # 检查 com_name 是否存在，如果不存在则添加
        if not self.config.has_option("Settings", "com_name"):
            print("com_name 不存在，正在添加 com_name = COM1")
            self.config.set("Settings", "com_name", "COM1")
        # 修改 param1 的值
        self.config.set("Settings", "com_name", com_name)
        # 保存配置文件
        with open(self.config_file, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)
        # 更新显示
        self.update_display()

    def config_set(self, section, option, value=None):
        self.config.set(section, option, value=None)

    def config_read(self):
        self.config.read(self.config_file, encoding="utf-8")

    def config_save(self):
        with open(self.config_file, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def get_machine_info_by_machineIdx(self, machineIdx):
        SECTION_NAME = "MACHINE-" + str(machineIdx)
        machine_name = self.config.get(SECTION_NAME, "machine_name", fallback=None)
        module_number_str = self.config.get(SECTION_NAME, "module_number", fallback=None)
        module_number = int(module_number_str)
        return machine_name, module_number

    def get_module_info_by_moduleIdx(self, machineIdx, moduleIdx):
        SECTION_NAME = "MACHINE-" + str(machineIdx)
        ARRD = "module" + str(moduleIdx) + "_addr"
        NAME = "module" + str(moduleIdx) + "_name"
        addr = int(self.config.get(SECTION_NAME, ARRD, fallback=None), 16)
        name = self.config.get(SECTION_NAME, NAME, fallback=None)
        return addr, name

    def get_all_module_info_ofMachine(self, machineIdx):
        SECTION_NAME = "MACHINE-" + str(machineIdx)
        machine_name, module_number = self.get_machine_info_by_machineIdx(machineIdx)
        addr_list = []
        name_list = []
        for i in range(module_number):
            addr, name = self.get_module_info_by_moduleIdx(machineIdx, i)
            # 将值加入各自的列表
            addr_list.append(addr)
            name_list.append(name)
        print(f"machine_name: {machine_name}")
        print(f"module_number: {module_number}")
        print("addr_list:", addr_list)
        print("name_list:", name_list)
        return machine_name, module_number, addr_list, name_list

    def get_module_fwPath_by_moduleIdx(self, machineIdx, moduleIdx):
        SECTION_NAME = "MACHINE-" + str(machineIdx)
        PATH = "module" + str(moduleIdx) + "_fw_path"
        path = self.config.get(SECTION_NAME, PATH, fallback=None)
        return path
