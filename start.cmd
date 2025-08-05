@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 强制使用 cmd.exe 重新运行自身，避免 "call :label" 报错
if not defined IS_BATCH (
set IS_BATCH=1
cmd /c "%~f0" %*
exit /b
)

echo [信息] Firefly - QQ Bot 部署脚本
echo ====================================

:: 检查 Python 环境
echo [检查] 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
echo [错误] Python 未安装！
echo [提示] 下载链接: https://www.python.org/downloads/
pause
exit /b 1
) else (
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] 检测到 Python 版本: !PYTHON_VERSION!
)

:: 检查 Conda 安装
echo [检查] 正在检查 Conda 或 Miniconda 环境...
where conda >nul 2>&1
if %errorlevel% neq 0 (
echo [错误] 未找到 Conda！
echo [提示] 请从以下地址下载并安装 Miniconda:
echo https://docs.conda.io/en/latest/miniconda.html
pause
exit /b 1
)

:: 获取 conda 安装目录，找到 activate.bat
for /f "delims=" %%i in ('where conda') do set "CONDA_PATH=%%~dpi"
set "ACTIVATE_SCRIPT=!CONDA_PATH!..\Scripts\activate.bat"
if not exist "!ACTIVATE_SCRIPT!" (
echo [错误] 未找到 activate.bat 文件！
pause
exit /b 1
)

echo [成功] 检测到 Conda，准备使用: !ACTIVATE_SCRIPT!

:: 检查 firefly 环境是否存在
call "!ACTIVATE_SCRIPT!" base >nul
conda env list | findstr /c:"firefly" >nul
if %errorlevel% neq 0 (
echo [信息] 未检测到 firefly 环境，正在创建...
conda create -n firefly python=3.10 -y
if %errorlevel% neq 0 (
echo [错误] 虚拟环境创建失败！
pause
exit /b 1
)
echo [成功] firefly 虚拟环境创建完成
) else (
echo [成功] firefly 环境已存在
)

:: 激活 firefly 环境
echo [信息] 正在激活 firefly 环境...
call "!ACTIVATE_SCRIPT!" firefly
if %errorlevel% neq 0 (
echo [错误] 激活虚拟环境失败！
pause
exit /b 1
)
echo [成功] 虚拟环境激活完成

:: 安装依赖
echo [信息] 正在安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
echo [错误] 安装依赖失败！
echo [提示] 请检查 requirements.txt 是否存在，并确认网络正常
pause
exit /b 1
)
echo [成功] 依赖安装完成

:: 启动应用
echo [信息] 启动 Firefly 应用中...
echo [提示] 按 Ctrl+C 可终止程序
python run.py

pause
exit /b 0
