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
        self.config.read(self.config_file)
        self.update_display()

    def ensure_config_exists(self):
        """确保配置文件存在，且有必需的节和选项。"""
        # 如果配置文件不存在，创建并写入默认值
        if not self.config.read(self.config_file):
            print(f"{self.config_file} 不存在，正在创建默认配置文件。")
            self.config.add_section("Settings")
            self.config.set("Settings", "com_name", "COM1")
            self.config.set("Settings", "fw_path_light", "none")
            self.config.set("Settings", "fw_path_main", "none")
            self.config.set("Settings", "fw_path_bottom", "none")

            # 创建一个默认的 User 部分
            self.config.add_section("User")
            self.config.set("User", "username", "admin")
            self.config.set("User", "password", "secret")
            # 保存创建的配置文件
            with open(self.config_file, "w") as configfile:
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
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)
        # 更新显示
        self.update_display()

    def config_set(self, section, option, value=None):
        self.config.set(section, option, value=None)

    def config_read(self):
        self.config.read(self.config_file)

    def config_save(self):
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)
