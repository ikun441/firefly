from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging

from .auth import get_current_user
from .utils import read_config

router = APIRouter(tags=["pages"])
# templates将在__init__.py中被设置
templates = None
logger = logging.getLogger("pages")

# 确保templates被设置
def set_templates(t):
    global templates
    templates = t

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user: dict = Depends(get_current_user)):
    try:
        config = read_config()
        
        # 如果是新安装，重定向到开始页面
        if config.get("server", {}).get("is_new", False):
            return RedirectResponse(url="/start")
        
        # 检查是否使用默认密码
        default_password = config.get("server", {}).get("password") == "ilovefirefly"
        default_username = config.get("server", {}).get("username") == "ilovefirefly"
        show_password_warning = default_password and default_username
        
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request, 
                "user": user, 
                "config": config,
                "show_password_warning": show_password_warning
            }
        )
    except Exception as e:
        logger.error(f"加载仪表盘页面失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载仪表盘页面失败: {str(e)}")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user: dict = Depends(get_current_user)):
    try:
        config = read_config()
        
        # 获取背景设置
        background = config.get("ui", {}).get("background", {
            "type": "RINGS",
            "color": "#1b1b1b",
            "background_color": "#000000",
            "speed": 1.0
        })
        
        return templates.TemplateResponse(
            "settings.html", 
            {
                "request": request, 
                "user": user, 
                "config": config,
                "background": background
            }
        )
    except Exception as e:
        logger.error(f"加载设置页面失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载设置页面失败: {str(e)}")

@router.get("/start", response_class=HTMLResponse)
async def start_page(request: Request, user: dict = Depends(get_current_user)):
    try:
        config = read_config()
        
        # 如果不是新安装，重定向到仪表盘
        if not config.get("server", {}).get("is_new", True):
            return RedirectResponse(url="/dashboard")
        
        return templates.TemplateResponse(
            "start.html", 
            {
                "request": request, 
                "user": user, 
                "config": config
            }
        )
    except Exception as e:
        logger.error(f"加载开始页面失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载开始页面失败: {str(e)}")

@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, user: dict = Depends(get_current_user)):
    try:
        config = read_config()
        
        return templates.TemplateResponse(
            "logs.html", 
            {
                "request": request, 
                "user": user, 
                "config": config
            }
        )
    except Exception as e:
        logger.error(f"加载日志页面失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载日志页面失败: {str(e)}")

@router.get("/processes", response_class=HTMLResponse)
async def processes_page(request: Request, user: dict = Depends(get_current_user)):
    try:
        config = read_config()
        
        return templates.TemplateResponse(
            "processes.html", 
            {
                "request": request, 
                "user": user, 
                "config": config
            }
        )
    except Exception as e:
        logger.error(f"加载进程页面失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"加载进程页面失败: {str(e)}")

@router.get("/run")
async def run_page(request: Request, user: dict = Depends(get_current_user)):
    try:
        return templates.TemplateResponse("run.html", {"request": request, "user": user})
    except Exception as e:
        logger.error(f"加载运行页面失败: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})

@router.get("/error")
async def error_page(request: Request, error: str = "未知错误"):
    try:
        return templates.TemplateResponse("error.html", {"request": request, "error": error})
    except Exception as e:
        logger.error(f"加载错误页面失败: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "error": "页面加载失败"})