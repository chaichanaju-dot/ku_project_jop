@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "%~dp0ต่อภาพ_แอป.py"
if errorlevel 1 pause
