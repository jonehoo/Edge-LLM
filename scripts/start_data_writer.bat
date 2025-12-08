@echo off
chcp 65001 >nul
echo ========================================
echo 启动数据写入服务
echo ========================================
echo.

cd /d %~dp0\..

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
)

echo.
echo 启动数据写入服务（每60秒写入一次）...
echo 按 Ctrl+C 停止服务
echo.

python scripts\data_writer.py --interval 60

pause

