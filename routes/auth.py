from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Form, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dotenv import load_dotenv

from .utils import read_config, update_config

# 加载环境变量
load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("auth")

# 存储会话
sessions = {}

# 存储会话

# 生成会话ID
def generate_session_id() -> str:
    return str(uuid.uuid4())

# 验证用户凭据
def verify_credentials(username: str, password: str) -> bool:
    try:
        env_username = os.getenv("USERNAME", "ilovefirefly")
        env_password = os.getenv("PASSWORD", "ilovefirefly")
        return username == env_username and password == env_password
    except Exception as e:
        logger.error(f"验证凭据失败: {str(e)}")
        return False

# 获取当前用户
async def get_current_user(session_id: Optional[str] = Cookie(None)) -> Dict[str, Any]:
    if not session_id or session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sessions[session_id]

@router.post("/login")
async def login(response: Response, request: Request):
    try:
        username = os.getenv("USERNAME", "ilovefirefly")
        password = os.getenv("PASSWORD", "ilovefirefly")
    except Exception:
        # 如果不是JSON格式，尝试表单格式
        username = os.getenv("USERNAME", "ilovefirefly")
        password = os.getenv("PASSWORD", "ilovefirefly")
    try:
        if verify_credentials(username, password):
            # 创建会话
            session_id = generate_session_id()
            sessions[session_id] = {"username": username}
            
            # 设置Cookie
            response.set_cookie(key="session_id", value=session_id, httponly=True)
            
            # 检查是否是新安装
            config = read_config()
            is_new = config.get("server", {}).get("is_new", False)
            env_username = os.getenv("USERNAME", "ilovefirefly")
            env_password = os.getenv("PASSWORD", "ilovefirefly")
            default_credentials = (username == env_username and password == env_password)
            
            return {
                "success": True, 
                "is_new": is_new,
                "default_credentials": default_credentials,
                "redirect": "/start" if is_new else "/dashboard"
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "用户名或密码错误"}
            )
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"登录失败: {str(e)}"}
        )

@router.post("/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    try:
        if session_id and session_id in sessions:
            del sessions[session_id]
        
        response.delete_cookie(key="session_id")
        return {"success": True, "redirect": "/login"}
    except Exception as e:
        logger.error(f"登出失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"登出失败: {str(e)}"}
        )

@router.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    user: dict = Depends(get_current_user)
):
    try:
        env_password = os.getenv("PASSWORD", "ilovefirefly")
        
        # 验证当前密码
        if env_password != current_password:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "当前密码不正确"}
            )
        
        # 更新.env文件中的密码
        env_file_path = ".env"
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(env_file_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith('PASSWORD='):
                        f.write(f'PASSWORD={new_password}\n')
                    else:
                        f.write(line)
        else:
            # 如果.env文件不存在，创建一个
            with open(env_file_path, 'w', encoding='utf-8') as f:
                f.write(f'USERNAME={os.getenv("USERNAME", "ilovefirefly")}\n')
                f.write(f'PASSWORD={new_password}\n')
        
        # 重新加载环境变量
        load_dotenv(override=True)
        
        return {"success": True, "message": "密码已更新"}
    except Exception as e:
        logger.error(f"更新密码失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"更新密码失败: {str(e)}"}
        )