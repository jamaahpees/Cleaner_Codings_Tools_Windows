@echo off
setlocal
cd /d "%~dp0"
title Dev & AI CLI Cleaner - Portable Launcher

echo ===================================================
echo     Dev & AI CLI Cleaner - Windows Portable
echo ===================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak terdeteksi pada sistem Windows Anda.
    echo Pastikan Python 3.10+ sudah terinstal dan dicentang "Add python.exe to PATH".
    echo Silakan download di: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/2] Memastikan dependencies terinstal...
python -m pip install customtkinter send2trash -q

echo [2/2] Menjalankan aplikasi Dev & AI CLI Cleaner...
start "" pythonw dev_cleaner.py

echo.
echo Aplikasi telah berjalan di background (GUI).
exit /b 0