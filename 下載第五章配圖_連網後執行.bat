@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在嘗試下載第五章三個來源圖檔；下載失敗不會改寫正文。
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\fetch_game_art.ps1" -Chapter 5
echo.
echo 成功下載後重新開啟 index.html；未取得的圖片仍顯示提示卡。
pause
