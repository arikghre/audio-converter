@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo.
echo  ====================================
echo   AG's Media Converter  -  Build
echo  ====================================
echo.
python build_tool.py
pause
