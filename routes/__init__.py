from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from .pages import router as pages_router, set_templates
from .auth import router as auth_router
from .api import router as api_router

def init_routes(app: FastAPI, templates: Jinja2Templates):
    # 设置模板到路由中
    pages_router.templates = templates
    set_templates(templates)
    
    # 包含所有路由
    app.include_router(pages_router)
    app.include_router(auth_router)
    app.include_router(api_router)