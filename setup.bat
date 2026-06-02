@echo off
REM 猜拳小游戏 - 项目初始化脚本
REM 适用于 Windows 环境

echo ========================================
echo   猜拳小游戏 - 项目初始化
echo ========================================
echo.

REM 检查Python版本
echo [1/5] 检查Python版本...
python --version
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装 Python 3.11
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python检测成功
echo.

REM 创建虚拟环境
echo [2/5] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo [OK] 虚拟环境创建成功
) else (
    echo [跳过] 虚拟环境已存在
)
echo.

REM 激活虚拟环境
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat
echo [OK] 虚拟环境已激活
echo.

REM 升级pip
echo [4/5] 升级pip...
python -m pip install --upgrade pip
echo [OK] pip升级完成
echo.

REM 安装依赖
echo [5/5] 安装项目依赖...
pip install -r requirements.txt
echo [OK] 依赖安装完成
echo.

echo ========================================
echo   初始化完成！
echo ========================================
echo.
echo 下一步:
echo   1. 激活虚拟环境: call venv\Scripts\activate.bat
echo   2. 运行游戏: python src\main.py
echo   3. 运行测试: pytest
echo.
pause
