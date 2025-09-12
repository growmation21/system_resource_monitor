# System Resource Monitor - Background Launcher (PowerShell)
# Starts the monitor without showing any console windows

param(
    [int]$Port = 8888,
    [switch]$SystemTray = $false
)

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Starting System Resource Monitor in background mode..." -ForegroundColor Green

try {
    if ($SystemTray) {
        # Try to start system tray version
        Write-Host "Attempting to start system tray version..." -ForegroundColor Cyan
        
        # Check if required dependencies are installed
        $pystrayInstalled = & python -c "import pystray; print('OK')" 2>$null
        $pillowInstalled = & python -c "from PIL import Image; print('OK')" 2>$null
        
        if ($pystrayInstalled -eq "OK" -and $pillowInstalled -eq "OK") {
            # Start system tray version
            Start-Process -FilePath "pythonw.exe" -ArgumentList "system_tray_launcher.py", "--port", $Port -WindowStyle Hidden -WorkingDirectory $ScriptDir
            Write-Host "System tray launcher started successfully!" -ForegroundColor Green
            Write-Host "Look for the System Resource Monitor icon in your system tray." -ForegroundColor Yellow
        } else {
            Write-Host "System tray dependencies not installed. Installing..." -ForegroundColor Yellow
            & python -m pip install pystray pillow --quiet
            if ($LASTEXITCODE -eq 0) {
                Start-Process -FilePath "pythonw.exe" -ArgumentList "system_tray_launcher.py", "--port", $Port -WindowStyle Hidden -WorkingDirectory $ScriptDir
                Write-Host "System tray launcher started successfully!" -ForegroundColor Green
            } else {
                Write-Host "Failed to install dependencies. Using hidden mode instead." -ForegroundColor Yellow
                $SystemTray = $false
            }
        }
    }
    
    if (-not $SystemTray) {
        # Start hidden mode launcher
        Write-Host "Starting hidden background launcher..." -ForegroundColor Cyan
        Start-Process -FilePath "pythonw.exe" -ArgumentList "launch_monitor.py", "--hidden", "--port", $Port -WindowStyle Hidden -WorkingDirectory $ScriptDir
        Write-Host "Hidden launcher started successfully!" -ForegroundColor Green
    }
    
    Start-Sleep -Seconds 3
    
    # Verify the process started
    $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainModule.FileName -like "*python*" -and 
        $_.StartInfo.WorkingDirectory -eq $ScriptDir
    }
    
    if ($pythonProcesses.Count -gt 0) {
        Write-Host "`nSystem Resource Monitor is now running in the background!" -ForegroundColor Green
        Write-Host "Backend URL: http://localhost:$Port" -ForegroundColor Cyan
        Write-Host "WebSocket: ws://localhost:$Port/ws" -ForegroundColor Cyan
        Write-Host "`nChrome Extension Setup:" -ForegroundColor Yellow
        Write-Host "1. Open Chrome → chrome://extensions/" -ForegroundColor White
        Write-Host "2. Enable 'Developer mode'" -ForegroundColor White
        Write-Host "3. Click 'Load unpacked'" -ForegroundColor White
        Write-Host "4. Select folder: $ScriptDir\chrome-extension" -ForegroundColor White
        Write-Host "5. Click the extension icon in Chrome toolbar" -ForegroundColor White
        
        if ($SystemTray) {
            Write-Host "`nRight-click the system tray icon for options." -ForegroundColor Magenta
        } else {
            Write-Host "`nTo stop: End 'python.exe' process in Task Manager" -ForegroundColor Red
            Write-Host "or run: Stop-Process -Name 'python*' -Force" -ForegroundColor Red
        }
    } else {
        Write-Host "Warning: Could not verify if the process started successfully." -ForegroundColor Yellow
        Write-Host "Check Task Manager for 'python.exe' processes." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Error starting System Resource Monitor: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nPress any key to close this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
