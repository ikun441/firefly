# -- coding: utf-8 --
import os
import json
import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth import get_current_user
from .utils import read_config, update_config, get_data_dir

router = APIRouter(prefix="/api")
logger = logging.getLogger("api")

# 模型定义
class ConfigUpdateModel(BaseModel):
    path: str
    value: Any

class PasswordUpdateModel(BaseModel):
    current_password: str
    new_password: str

class BackgroundSettingsModel(BaseModel):
    type: str
    color: str
    background_color: str
    speed: float

class BotActionModel(BaseModel):
    action: str  # "start" or "stop"

# 递归更新嵌套字典
def update_nested_dict(d: Dict, path: str, value: Any) -> Dict:
    keys = path.split('.')
    current = d
    
    # 遍历路径中的所有键，除了最后一个
    for i, key in enumerate(keys[:-1]):
        # 如果键不存在或者值不是字典，创建一个新字典
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    # 设置最后一个键的值
    current[keys[-1]] = value
    return d

@router.get("/config")
async def get_config(current_user: Dict = Depends(get_current_user)):
    """获取当前配置"""
    try:
        config = read_config()
        # 移除敏感信息
        if "server" in config and "password" in config["server"]:
            config["server"]["password"] = "*****"
        return {"success": True, "config": config}
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        return {"success": False, "message": f"获取配置失败: {str(e)}"}

@router.post("/config/update")
async def update_config_item(item: ConfigUpdateModel, current_user: Dict = Depends(get_current_user)):
    """更新配置项"""
    try:
        config = read_config()
        
        # 使用递归更新嵌套字典
        update_nested_dict(config, item.path, item.value)
        
        # 保存更新后的配置
        update_config(config)
        
        return {"success": True, "message": "配置已更新"}
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        return {"success": False, "message": f"更新配置失败: {str(e)}"}

@router.post("/config/complete-setup")
async def complete_setup(current_user: Dict = Depends(get_current_user)):
    """完成初始设置，将is_new设置为False"""
    try:
        config = read_config()
        if "server" not in config:
            config["server"] = {}
        
        config["server"]["is_new"] = False
        update_config(config)
        
        return {"success": True, "message": "设置已完成"}
    except Exception as e:
        logger.error(f"完成设置失败: {str(e)}")
        return {"success": False, "message": f"完成设置失败: {str(e)}"}

@router.post("/update-password")
async def update_password(model: PasswordUpdateModel, current_user: Dict = Depends(get_current_user)):
    """更新用户密码"""
    try:
        config = read_config()
        
        # 验证当前密码
        if config["server"]["password"] != model.current_password:
            return {"success": False, "message": "当前密码不正确"}
        
        # 更新密码
        config["server"]["password"] = model.new_password
        update_config(config)
        
        return {"success": True, "message": "密码已更新"}
    except Exception as e:
        logger.error(f"更新密码失败: {str(e)}")
        return {"success": False, "message": f"更新密码失败: {str(e)}"}

@router.post("/update-background")
async def update_background(settings: BackgroundSettingsModel, current_user: Dict = Depends(get_current_user)):
    """更新背景设置"""
    try:
        config = read_config()
        
        # 确保背景设置存在
        if "ui" not in config:
            config["ui"] = {}
        if "background" not in config["ui"]:
            config["ui"]["background"] = {}
        
        # 更新背景设置
        config["ui"]["background"]["type"] = settings.type
        config["ui"]["background"]["color"] = settings.color
        config["ui"]["background"]["background_color"] = settings.background_color
        config["ui"]["background"]["speed"] = settings.speed
        
        update_config(config)
        
        return {"success": True, "message": "背景设置已更新"}
    except Exception as e:
        logger.error(f"更新背景设置失败: {str(e)}")
        return {"success": False, "message": f"更新背景设置失败: {str(e)}"}

@router.get("/recent-logs")
async def get_recent_logs(current_user: Dict = Depends(get_current_user)):
    """获取最近的日志"""
    try:
        # 这里模拟返回一些日志数据
        # 实际应用中，应该从日志文件或数据库中读取
        logs = [
            {"timestamp": time.time() - 3600, "type": "info", "message": "系统启动成功"},
            {"timestamp": time.time() - 3000, "type": "info", "message": "机器人已连接"},
            {"timestamp": time.time() - 2400, "type": "warning", "message": "接收到未知命令"},
            {"timestamp": time.time() - 1800, "type": "error", "message": "连接断开"},
            {"timestamp": time.time() - 1200, "type": "info", "message": "重新连接成功"},
            {"timestamp": time.time() - 600, "type": "info", "message": "处理消息: 帮助命令"},
        ]
        
        return {"success": True, "logs": logs}
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return {"success": False, "message": f"获取日志失败: {str(e)}"}

@router.get("/logs")
async def get_logs(
    page: int = 1, 
    type: str = "all", 
    date_range: str = "today", 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """获取日志，支持分页和筛选"""
    try:
        # 这里模拟返回一些日志数据
        # 实际应用中，应该从日志文件或数据库中读取，并应用筛选条件
        logs = [
            {"timestamp": time.time() - 3600 * 24, "type": "info", "source": "system", "message": "系统启动成功"},
            {"timestamp": time.time() - 3600 * 23, "type": "info", "source": "bot", "message": "机器人已连接"},
            {"timestamp": time.time() - 3600 * 22, "type": "warning", "source": "command", "message": "接收到未知命令"},
            {"timestamp": time.time() - 3600 * 21, "type": "error", "source": "network", "message": "连接断开"},
            {"timestamp": time.time() - 3600 * 20, "type": "info", "source": "network", "message": "重新连接成功"},
            {"timestamp": time.time() - 3600 * 19, "type": "info", "source": "message", "message": "处理消息: 帮助命令"},
            {"timestamp": time.time() - 3600 * 18, "type": "debug", "source": "system", "message": "内存使用: 256MB"},
            {"timestamp": time.time() - 3600 * 17, "type": "info", "source": "bot", "message": "处理消息: 签到命令"},
            {"timestamp": time.time() - 3600 * 16, "type": "info", "source": "bot", "message": "处理消息: 查询命令"},
            {"timestamp": time.time() - 3600 * 15, "type": "warning", "source": "system", "message": "CPU使用率过高: 85%"},
        ]
        
        # 模拟分页
        total_pages = 3
        
        return {
            "success": True, 
            "logs": logs, 
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": len(logs) * total_pages
            }
        }
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return {"success": False, "message": f"获取日志失败: {str(e)}"}

@router.post("/toggle-bot")
async def toggle_bot(action: BotActionModel, current_user: Dict = Depends(get_current_user)):
    """切换机器人状态"""
    try:
        # 这里应该实现实际的机器人启动/停止逻辑
        # 这里只是模拟返回成功
        return {"success": True, "status": action.action, "message": f"机器人已{action.action}"}
    except Exception as e:
        logger.error(f"切换机器人状态失败: {str(e)}")
        return {"success": False, "message": f"切换机器人状态失败: {str(e)}"}

@router.post("/reconnect-protocol")
async def reconnect_protocol(current_user: Dict = Depends(get_current_user)):
    """重新连接协议"""
    try:
        # 这里应该实现实际的协议重连逻辑
        # 这里只是模拟返回成功
        return {"success": True, "message": "协议已重新连接"}
    except Exception as e:
        logger.error(f"重新连接协议失败: {str(e)}")
        return {"success": False, "message": f"重新连接协议失败: {str(e)}"}

@router.get("/system-resources")
async def get_system_resources(current_user: Dict = Depends(get_current_user)):
    """获取系统资源使用情况"""
    try:
        # 获取实际的系统资源使用情况
        cpu_percent = f"{psutil.cpu_percent(interval=1)}%"
        memory = psutil.virtual_memory()
        memory_used = f"{float(memory.used) / (1024 * 1024):.1f}MB"
        processes = f"{len(psutil.pids())}"
        disk = psutil.disk_usage('/')
        disk_used = f"{float(disk.used) / (1024 * 1024 * 1024):.1f}GB"

        return {"success": True, "data":{"cpu": cpu_percent, "memory": memory_used, "processes": processes, "disk": disk_used}}
    except Exception as e:
        logger.error("获取系统资源失败: %s", str(e))
        return {"success": False, "message": f"获取系统资源失败: {str(e)}"}

import asyncio

@router.get("/processes")
async def get_processes(limit: int = 5, _: Dict = Depends(get_current_user)):
    try:
        processes = []
        all_procs = list(psutil.process_iter(['pid', 'name', 'memory_info']))

        # 第一次采样
        for proc in all_procs:
            try:
                proc.cpu_percent(None)  # 初始采样，返回0但触发内部计时器
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        await asyncio.sleep(1.0)  # 非阻塞等待，给CPU使用率采样时间

        for proc in all_procs:
            try:
                memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                cpu_percent = proc.cpu_percent(None)  # 第二次采样，真实数值

                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_mb': round(memory_mb, 1),
                    'cpu_percent': round(cpu_percent, 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        top_processes = processes[:limit]

        return {"success": True, "processes": top_processes}
    except Exception as e:
        logger.error("获取进程信息失败: %s", str(e))
        return {"success": False, "message": f"获取进程信息失败: {str(e)}"}
