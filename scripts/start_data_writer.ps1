# PowerShell脚本 - 启动数据写入服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动数据写入服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到项目根目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

# 检查虚拟环境
$venvPath = Join-Path $projectRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "警告: 未找到虚拟环境，使用系统Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "启动数据写入服务（每60秒写入一次）..." -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

python scripts\data_writer.py --interval 60

Read-Host "按 Enter 键退出"

