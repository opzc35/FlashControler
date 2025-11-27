"""
配置管理
"""
import json
import os

class Config:
    """配置类"""

    # 默认配置
    DEFAULT_CONFIG = {
        "server": {
            "host": "0.0.0.0",
            "port": 9999,
            "password": "flashcontrol123"
        },
        "client": {
            "last_host": "",
            "last_port": 9999,
            "auto_reconnect": True
        },
        "update": {
            "check_on_startup": True,
            "update_url": "https://api.github.com/repos/yourname/FlashControler/releases/latest",
            "current_version": "1.0.0"
        },
        "terminal": {
            "shell": "/bin/bash",
            "encoding": "utf-8"
        }
    }

    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    return config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get(self, section, key, default=None):
        """获取配置项"""
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """设置配置项"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
