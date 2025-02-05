import configparser
import os



class Class_ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()

    def _load_config(self, config_file):
        """加载配置文件"""
        if os.path.exists(config_file):
            self.config.read(config_file)
        else:
            # 如果文件不存在，创建一个空文件
            with open(config_file, 'w') as f:
                f.write("")
            self.config.read(config_file)

    def get(self, file_name, section, option, fallback=None):
        """
        安全读取配置项
        :param file_name: 配置文件名
        :param section: 配置节
        :param option: 配置项
        :param fallback: 如果不存在返回的默认值
        :return: 配置值或默认值
        """
        self._load_config(file_name)
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def set(self, file_name, section, option=None, value=None):
        """
        安全写入配置项
        - 如果 value 为 None 或空，则删除该配置项
        - 如果某配置节下所有配置项为空，则删除该配置节
        :param file_name: 配置文件名
        :param section: 配置节
        :param option: 配置项
        :param value: 配置值，None 或空表示删除配置项
        """
        self._load_config(file_name)

        if value is None or value == "":
            # 如果 value 为空，则删除配置项
            if self.config.has_section(section) and self.config.has_option(section, option):
                self.config.remove_option(section, option)

            # 如果该配置节的所有配置项为空，删除该配置节
            if self.config.has_section(section) and not self.config.options(section):
                self.config.remove_section(section)
        else:
            # 如果 value 不为空，则写入配置项
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, option, value)

        # 保存到文件
        self._save_config(file_name)

    def _save_config(self, config_file):
        """保存配置到文件"""
        with open(config_file, 'w') as configfile:
            self.config.write(configfile)


# 示例用法
if __name__ == "__main__":
    manager = ConfigManager()

    # 写入配置
    manager.set("config.ini", "UserInfo", "bili_LoginCookies", "some_cookie_value")
    manager.set("config.ini", "UserInfo", "other_option", None)  # 清除配置项
    manager.set("config.ini", "EmptySection", "test_key", "")    # 清空配置项
    manager.set("config.ini", "EmptySection", None, None)        # 清空配置节

    # 读取配置
    cookies = manager.get("config.ini", "UserInfo", "bili_LoginCookies", fallback="default_cookie")
    print("Cookies:", cookies)
