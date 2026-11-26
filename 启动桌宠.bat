@echo off
cd /d "%~dp0"
if not exist "苏汐桌宠-运行包\KuroCat.exe" (
  echo [苏汐桌宠] 还没有打包，请先双击 一键打包.bat 生成 exe。
  timeout /t 4 >nul
  exit /b
)
tasklist /FI "IMAGENAME eq KuroCat.exe" 2>nul | find /I "KuroCat.exe" >nul
if %errorlevel%==0 (
  echo [苏汐桌宠] 已经在运行中，无需重复启动。
  timeout /t 3 >nul
  exit /b
)
start "" /D "%~dp0苏汐桌宠-运行包" "KuroCat.exe"
