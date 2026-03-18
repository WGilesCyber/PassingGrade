# PassingGrade — Windows build script
# Produces: dist/PassingGrade.exe (single file, no console window)
#
# Requirements (dev machine only — end users need nothing):
#   pip install -r requirements.txt
#
# Usage:
#   cd <repo root>
#   powershell -ExecutionPolicy Bypass -File build/build_windows.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Set-Location $root

Write-Host "Building PassingGrade for Windows..." -ForegroundColor Cyan

pyinstaller --clean PassingGrade.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Build succeeded: dist/PassingGrade.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "To distribute:" -ForegroundColor Yellow
    Write-Host "  Copy dist/PassingGrade.exe to the target machine."
    Write-Host "  (Optional) Place a customized policy/policy.json next to the exe."
} else {
    Write-Host "Build failed." -ForegroundColor Red
    exit 1
}
