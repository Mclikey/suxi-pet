@echo off
setlocal
title 苏汐桌宠一键打包（仓库版）
cd /d "%~dp0"

echo ============================================
echo   苏汐桌宠一键打包（首次使用前先装好 Node.js 和 Rust）
echo ============================================
echo.

echo [1/3] 构建前端...
call npm run build
if errorlevel 1 goto npmfail

echo.
echo [2/3] 编译 Rust 核心（约 2~3 分钟，请耐心等待）...
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
where cargo >nul 2>nul
if errorlevel 1 goto cargomissing
cd src-tauri
cargo build --release --features win7
if errorlevel 1 goto cargofail
cd ..

echo.
echo [3/3] 部署到运行包...
cd /d "%~dp0"
taskkill /F /IM KuroCat.exe >nul 2>&1
timeout /t 1 /nobreak >nul
tasklist | find /I "KuroCat.exe" >nul
if not errorlevel 1 goto stillrunning
if not exist "..\苏汐桌宠-运行包" mkdir "..\苏汐桌宠-运行包"
copy /Y "src-tauri\target\release\KuroCat.exe" "..\苏汐桌宠-运行包\KuroCat.exe"
if errorlevel 1 goto copyfail

echo.
echo ============================================
echo   打包完成！
echo   exe 位置：..\苏汐桌宠-运行包\KuroCat.exe
echo   双击 苏汐桌宠-运行包\启动苏汐桌宠.bat 启动桌宠
echo ============================================
pause
exit /b 0

:stillrunning
echo.
echo [错误] KuroCat.exe 仍在运行（可能以管理员权限启动，无法自动结束）。
echo        请手动退出桌宠后重新运行本脚本。
pause
exit /b 1

:copyfail
echo.
echo [错误] 复制 exe 失败（桌宠可能正在运行），请手动退出桌宠后重试。
pause
exit /b 1

:npmfail
echo.
echo [错误] 前端构建失败，请检查上方报错（常见：node/npm 未安装或不在 PATH）。
pause
exit /b 1

:cargomissing
echo.
echo [错误] 找不到 cargo。请确认 Rust 已安装：%USERPROFILE%\.cargo\bin\cargo.exe
pause
exit /b 1

:cargofail
echo.
echo [错误] Rust 编译失败，请检查上方报错。
pause
exit /b 1

