# PowerShell启动脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "边缘物联网温度分析系统" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境是否存在
if (-not (Test-Path "venv")) {
    Write-Host "正在创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "虚拟环境创建完成" -ForegroundColor Green
    Write-Host ""
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 检查并安装依赖
Write-Host "检查依赖..." -ForegroundColor Yellow
python -m pip install -q -r requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动Web应用..." -ForegroundColor Cyan
Write-Host "访问地址: http://localhost:8501" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动Streamlit应用
streamlit run web/app.py --server.port 8501 --server.address localhost




