#!/bin/bash
#声明utf-8编码
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

echo "Firefly - QQ Bot Deployment Script"
echo "================项目启动中===================="

#检查是否有python环境
if ! command -v python &> /dev/null; then
    echo "Python未安装，正在自动安装Python，请勿退出避免引起不必要的问题。"
    sudo apt install python3 -y
    exit 1
else echo "Python已安装，正在检查conda环境"
fi

# 检查是否安装了Conda
if ! command -v conda &> /dev/null; then
    echo "Conda未安装，正在自动安装Conda。"
    sudo apt install conda -y
    if [ $? -ne 0 ]; then
        echo "conda安装失败，请手动安装。"
        exit 1
    else echo "Conda已安装，正在检查虚拟环境"
    fi 
fi

# 检查虚拟环境是否存在
if ! conda env list | grep -q "firefly"; then
    echo "创建firefly虚拟环境..."
    conda create -n firefly python=3.10 -y
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败！"
        exit 1
    else echo "虚拟环境创建成功"
    fi
fi

# 激活虚拟环境并安装依赖
echo "激活虚拟环境并安装依赖..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate firefly
if [ $? -ne 0 ]; then
    echo "激活虚拟环境失败！"
    exit 1
else echo "虚拟环境激活成功"
fi

# 安装依赖
echo "开始安装依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "安装依赖失败！"
    exit 1
else echo "依赖安装成功"
fi

# 启动应用
echo "启动Firefly应用..."
python run.py
if [ $? -ne 0 ]; then
    echo "启动应用失败！"
    exit 1
else echo "应用启动成功！默认访问地址在localhost:8000,具体信息请查看日志！"
fi