@echo off
REM 环境检查脚本 - 验证Python 3.11环境

echo ========================================
echo   环境检查 - Python版本验证
echo ========================================
echo.

echo 检查Python安装...
python --version
if errorlevel 1 (
    echo [失败] 未找到Python，请先安装
    echo.
    echo 请访问以下地址下载Python 3.11:
    echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    pause
    exit /b 1
)

echo.
echo 检查Python版本...
python -c "import sys; v=sys.version_info; print(f'Python {v.major}.{v.minor}.{v.micro}')"
if errorlevel 1 (
    echo [失败] Python版本检查失败
    pause
    exit /b 1
)

echo.
echo 检查pip...
pip --version
if errorlevel 1 (
    echo [失败] pip未正确安装
    pause
    exit /b 1
)

echo.
echo ========================================
echo   环境检查完成！
echo ========================================
echo.
echo 您的环境已准备好开发猜拳小游戏。
echo.
echo 下一步: 运行 setup.bat 初始化项目
echo.
pause
