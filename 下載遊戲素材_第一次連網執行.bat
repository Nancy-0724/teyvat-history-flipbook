@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Downloading Genshin Impact screenshots for this offline flipbook...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\fetch_game_art.ps1"
echo.
echo The originally included historical SVG diagrams will appear if a source download fails.
pause
