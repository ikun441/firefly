@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo [信息] Firefly - QQ Bot 部署脚本
echo ====================================


echo [检查] 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
echo [错误] Python未安装！
echo [提示] 请从以下地址下载并安装 Python:
echo https://www.python.org/downloads/
echo [提示] 安装时请勾选"Add Python to PATH"选项
pause
exit /b 1
) else (
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] 检测到 Python 版本: !PYTHON_VERSION!
)

echo [检查] 正在检查 Conda 环境...
where conda >nul 2>&1
if %errorlevel% neq 0 (
echo [错误] Conda 未安装！
echo [提示] 请从以下地址下载并安装 Miniconda:
echo https://docs.conda.io/en/latest/miniconda.html
echo [提示] 安装时请勾选"Add to PATH"选项
pause
exit /b 1
) else (
for /f "tokens=*" %%i in ('conda --version') do set CONDA_VERSION=%%i
echo [成功] 检测到 !CONDA_VERSION!
)

echo [检查] 正在检查虚拟环境...
conda env list | findstr /C:"firefly" >nul
if %errorlevel% neq 0 (
echo [信息] 正在创建 firefly 虚拟环境 ^(Python 3.10^)...
conda create -n firefly python=3.10 -y
if %errorlevel% neq 0 (
echo [错误] 创建虚拟环境失败！
pause
exit /b 1
)
echo [成功] 虚拟环境创建完成
) else (
echo [成功] 检测到已存在的 firefly 环境
)

echo [信息] 正在激活虚拟环境 firefly...
conda activate firefly
if %errorlevel% neq 0 (
echo [错误] 激活虚拟环境失败！
echo [提示] 请尝试重新安装 Conda
pause
exit /b 1
)
echo [成功] 虚拟环境已激活

echo [信息] 正在安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
echo [错误] 安装依赖失败！
echo [提示] 请检查 requirements.txt 文件是否存在
echo [提示] 检查网络连接并重试
pause
exit /b 1
)
echo [成功] 依赖安装完成

echo [信息] 正在启动 Firefly 应用...
echo [提示] 按 Ctrl+C 可以终止程序运行
python run.py

pause
endlocal
exit /b 0

:: ------------- 子程序：激活 Conda 环境 -------------
:ActivateConda
set "ENV_NAME=%~1"
:: 获取 conda 所在目录
for /f "delims=" %%i in ('where conda') do set "CONDA_PATH=%%~dpi"
if not exist "!CONDA_PATH!\conda.bat" (
echo [错误] 未找到 conda.bat 文件！
exit /b 1
)
:: 调用 conda.bat 来激活环境
call "!CONDA_PATH!\conda.bat" activate %ENV_NAME%
exit /b %errorlevel%