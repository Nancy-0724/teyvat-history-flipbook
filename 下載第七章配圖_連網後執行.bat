@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\fetch_game_art.py --chapter 7
) else (
  python tools\fetch_game_art.py --chapter 7
)
if errorlevel 1 (
  echo 圖片尚未全部取得，請查看上方訊息；既有圖片與正文不會刪除。
) else (
  echo 第七章天釘圖片已就緒。
)
pause
