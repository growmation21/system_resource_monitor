# Background Launcher Options

This directory now includes multiple ways to run the System Resource Monitor without keeping a console window open.

## Quick Start Options

### 🎯 **Recommended: PowerShell Launcher** 
```powershell
powershell -ExecutionPolicy Bypass -File Start-Monitor.ps1 -SystemTray
```
- Auto-installs dependencies
- System tray interface  
- Clean setup instructions
- Fallback to hidden mode

### 🖱️ **System Tray Mode** (Best user experience)
```powershell
pip install pystray pillow
python system_tray_launcher.py
```
- Right-click system tray icon for controls
- Start/Stop/Restart from GUI
- Visual status indicators
- Windows notifications

### 🔇 **Hidden Console Mode** (No dependencies)
```powershell
python launch_monitor.py --hidden
```
- Simplest background operation
- No additional packages needed
- Stop via Task Manager

### 📁 **Batch File** (Double-click simplicity)
```batch
start_monitor_background.bat
```
- Double-click to start
- Brief confirmation message
- Automatic background mode

## Desktop Shortcuts

Create shortcuts for all launch modes:
```powershell
python create_shortcuts.py --create
```

This creates 4 desktop shortcuts:
- **System Resource Monitor**: Normal mode (with console)
- **System Resource Monitor (Background)**: Hidden mode (no console)  
- **System Resource Monitor (Tray)**: System tray mode
- **Start System Monitor (PowerShell)**: PowerShell launcher

## Files Added

| File | Purpose |
|------|---------|
| `system_tray_launcher.py` | System tray interface with GUI controls |
| `launch_hidden.py` | Hidden console launcher (no window) |  
| `Start-Monitor.ps1` | PowerShell launcher with auto-setup |
| `start_monitor_background.bat` | Simple batch file launcher |
| `create_shortcuts.py` | Desktop shortcut creation utility |

## Updated Files

| File | Changes |
|------|---------|
| `launch_monitor.py` | Added `--hidden` option |
| `INSTALL.md` | Added background operation section |

## Chrome Extension Setup

All background modes show these setup instructions:

1. **Open Chrome** → `chrome://extensions/`
2. **Enable Developer mode** (top-right toggle)
3. **Click "Load unpacked"**
4. **Select folder**: `chrome-extension`  
5. **Click extension icon** in Chrome toolbar

## Managing Background Processes

### Check if running:
```powershell
netstat -an | findstr :8888
Get-Process -Name "python*"
```

### Stop background monitor:
- **System Tray**: Right-click icon → Quit
- **Task Manager**: End `python.exe` process
- **PowerShell**: `Stop-Process -Name "python*" -Force`

## Troubleshooting

**System tray icon not appearing?**
```powershell
pip install pystray pillow --upgrade
```

**PowerShell execution policy error?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Process won't stop?**
```powershell
# Find the process
Get-Process -Name "python*" | Format-Table Id,ProcessName,MainWindowTitle

# Stop specific process by ID
Stop-Process -Id <ProcessId> -Force
```

---

**Result**: System Resource Monitor now runs cleanly in the background without console windows! 🎉
