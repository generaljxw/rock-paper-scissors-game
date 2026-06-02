#!/bin/bash
# 猜拳小游戏 - 项目初始化脚本
# 适用于 Linux / macOS 环境

echo "========================================"
echo "   猜拳小游戏 - 项目初始化"
echo "========================================"
echo ""

# 检查Python版本
echo "[1/5] 检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "[错误] 未检测到Python，请先安装 Python 3.11"
    echo "下载地址: https://www.python.org/downloads/"
    read -p "按Enter键退出..."
    exit 1
fi

echo "[OK] Python检测成功"
echo ""

# 创建虚拟环境
echo "[2/5] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[OK] 虚拟环境创建成功"
else
    echo "[跳过] 虚拟环境已存在"
fi
echo ""

# 激活虚拟环境
echo "[3/5] 激活虚拟环境..."
source venv/bin/activate
echo "[OK] 虚拟环境已激活"
echo ""

# 升级pip
echo "[4/5] 升级pip..."
python -m pip install --upgrade pip
echo "[OK] pip升级完成"
echo ""

# 安装依赖
echo "[5/5] 安装项目依赖..."
pip install -r requirements.txt
echo "[OK] 依赖安装完成"
echo ""

echo "========================================"
echo "   初始化完成！"
echo "========================================"
echo ""
echo "下一步:"
echo "   1. 激活虚拟环境: source venv/bin/activate"
echo "   2. 运行游戏: python src/main.py"
echo "   3. 运行测试: pytest"
echo ""
read -p "按Enter键继续..."
