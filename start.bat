@echo off
chcp 65001 >nul
echo ========================================
echo 边缘物联网温度分析系统
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建完成
    echo.
)

REM 激活虚拟环境并安装依赖
echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 检查依赖...
pip install -q -r requirements.txt

echo.
echo ========================================
echo 启动Web应用...
echo 访问地址: http://localhost:8501
echo 按 Ctrl+C 停止应用
echo ========================================
echo.

REM 启动Streamlit应用
streamlit run web/app.py --server.port 8501 --server.address localhost

pause




