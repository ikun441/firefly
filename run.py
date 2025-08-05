import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from routes import init_routes
from routes.utils import get_data_dir, setup_logging, read_config

# 设置日志
logger = setup_logging()

# 确保数据目录存在
data_dir = get_data_dir()

# 读取配置
config = read_config()

# 创建FastAPI应用
app = FastAPI(title="All-in-One Scripts")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化模板
templates = Jinja2Templates(directory="templates")

# 初始化路由
init_routes(app, templates)

# 启动应用
if __name__ == "__main__":
    # 从配置中获取主机和端口
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8000)
    
    print(f"启动服务器于 http://{host}:{port}")
    print(f"本地访问请前往 http://localhost:{port}")
    uvicorn.run("run:app", host=host, port=port, reload=False)