import os
import yaml
import logging
import logging.handlers
from typing import Dict, Any, Optional

# 配置日志
def setup_logging():
    # 确保日志目录存在
    log_dir = os.path.join(get_data_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器 - 按日期轮换
    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        when='midnight',
        backupCount=7
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 为各个模块创建日志记录器
    for module in ["api", "auth", "pages", "utils"]:
        logger = logging.getLogger(module)
        logger.setLevel(logging.INFO)
    
    return root_logger

# 获取数据目录
def get_data_dir() -> str:
    """获取或创建数据目录"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

# 获取配置文件路径
def get_config_path() -> str:
    """获取配置文件路径"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")

# 读取配置文件
def read_config() -> Dict[str, Any]:
    """读取配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        # 如果配置文件不存在，返回默认配置并创建文件
        default_config = get_default_config()
        update_config(default_config)
        return default_config
    except Exception as e:
        logging.error(f"读取配置文件失败: {str(e)}")
        return {}

# 更新配置文件
def update_config(config: Dict[str, Any]) -> bool:
    """更新配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        logging.error(f"更新配置文件失败: {str(e)}")
        return False

# 获取默认配置
def get_default_config() -> Dict[str, Any]:
    """获取默认配置"""
    return {
        "app": {
            "name": "All-in-One Scripts",
            "version": "1.0.0"
        },
        "server": {
            "host": "0.0.0.0",
            "port": 8000,
            "username": "ilovefirefly",
            "password": "ilovefirefly",
            "is_new": True
        },
        "bot": {
            "type": "onebot",
            "protocol": "ws",
            "enabled": False
        },
        "ui": {
            "background": {
                "type": "RINGS",
                "color": "#1b1b1b",
                "background_color": "#000000",
                "speed": 1.0
            }
        }
    }

# 获取默认背景配置
def get_default_background_config():
    return {
        "type": "rings",
        "options": {
            "mouseControls": True,
            "touchControls": True,
            "gyroControls": False,
            "minHeight": 200.00,
            "minWidth": 200.00,
            "scale": 1.00,
            "scaleMobile": 1.00
        }
    }

# 初始化配置
def init_config():
    config = get_config()
    
    # 如果配置不存在或为空，创建默认配置
    if not config:
        config = {
            "application": {
                "name": "firefly",
                "version": "1.0.0",
                "description": "A simple and cute QQ bot deployment script",
                "bot": "zhenxun",
                "agreements": "napcat"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "username": "ilovefirefly",
                "password": "ilovefirefly",
                "is_new": True
            },
            "project": {
                "bot": {
                    "zhenxun": {
                        "name": "zhenxun",
                        "version": "1.0.0",
                        "description": "A QQ bot project"
                    }
                },
                "agreements": {
                    "napcat": {
                        "name": "napcat",
                        "version": "1.0.0",
                        "description": "A QQ bot project by napcat"
                    }
                }
            },
            "ui": {
                "background": get_default_background_config()
            }
        }
        update_config(config)
    
    # 确保UI配置存在
    if "ui" not in config:
        config["ui"] = {"background": get_default_background_config()}
        update_config(config)
    elif "background" not in config["ui"]:
        config["ui"]["background"] = get_default_background_config()
        update_config(config)
    
    return config