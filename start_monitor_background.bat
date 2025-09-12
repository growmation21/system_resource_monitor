@echo off
REM System Resource Monitor - Background Launcher
REM Starts the monitor without showing any console windows

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Start the hidden launcher using pythonw (no console window)
start /B pythonw.exe launch_hidden.py %*

REM Optional: Show a brief confirmation message
echo System Resource Monitor started in background mode.
echo Check system tray or Task Manager for 'python.exe' process.
timeout /t 3 >nul

REM Exit the batch file (this window will close)
exit
