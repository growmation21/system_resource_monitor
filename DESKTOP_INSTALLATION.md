# System Resource Monitor - Desktop Integration Guide

## 🚀 Quick Installation

### Automatic Installation
```bash
# Install with desktop shortcuts
python desktop_integration.py --install

# Install with autostart enabled
python desktop_integration.py --install --autostart

# Generate icons only
python desktop_integration.py --icons-only
```

### Manual Launch
```bash
# Launch application
python launch_monitor.py

# Launch minimized (for autostart)
python launch_monitor.py --minimized

# Launch on custom port
python launch_monitor.py --port 9000
```

---

## 📋 Installation Features

### ✅ What Gets Installed

**Desktop Integration:**
- Desktop shortcut to launch the application
- Start Menu entry (Windows only)
- Application icons in multiple sizes (16x16 to 256x256)
- User data directory for settings and logs

**Auto-start Options:**
- Windows: Registry entry in `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- macOS: LaunchAgent plist file in `~/Library/LaunchAgents/`
- Linux: Desktop file in `~/.config/autostart/`

**Application Data:**
- Config directory: `{USER_DATA}/config/`
- Logs directory: `{USER_DATA}/logs/`
- Chrome app files: `{USER_DATA}/chrome-app/`

### 🗂️ Directory Structure After Installation

```
User Data Directory:
├── config/                    # User settings and preferences
├── logs/                      # Application logs
└── chrome-app/               # Chrome app files (copied)
    ├── window.html
    ├── manifest.json
    ├── background.js
    └── icons/
        ├── icon-16.png
        ├── icon-32.png
        ├── icon-48.png
        ├── icon-128.png
        └── icon-256.png
```

---

## 🖥️ Platform-Specific Installation

### Windows

**Desktop Shortcut:**
- Creates `.lnk` file on Desktop
- Fallback to `.bat` file if pywin32 not available
- Start Menu entry in User Programs folder

**Autostart:**
- Registry key: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Key name: `system-resource-monitor`
- Command: `python "path\to\launch_monitor.py" --minimized`

**Service Installation (Optional):**
```cmd
# Using NSSM (Non-Sucking Service Manager)
# 1. Download NSSM from https://nssm.cc/
# 2. Install as service:
nssm install SystemResourceMonitor python.exe "C:\path\to\launch_monitor.py" --minimized
nssm start SystemResourceMonitor
```

### macOS

**Desktop Integration:**
- Creates `.app` bundle on Desktop
- LaunchAgent for autostart
- Uses `python3` command

**App Bundle Structure:**
```
System Resource Monitor.app/
├── Contents/
│   ├── Info.plist
│   └── MacOS/
│       └── launcher
```

**Autostart:**
- LaunchAgent plist: `~/Library/LaunchAgents/com.growmation21.system-resource-monitor.plist`

### Linux

**Desktop Integration:**
- Creates `.desktop` file on Desktop
- Autostart via `~/.config/autostart/`
- Uses standard XDG directories

**Desktop File:**
```ini
[Desktop Entry]
Name=System Resource Monitor
Exec=python3 "/path/to/launch_monitor.py"
Icon=/path/to/icon-256.png
Type=Application
Categories=System;Monitor;Utility;
```

---

## 🔧 Advanced Configuration

### System Tray Integration

**Install Dependencies:**
```bash
python system_tray.py --install-tray-deps
```

**Run with System Tray:**
```bash
python system_tray.py
```

**Features:**
- Minimizes to system tray
- Right-click context menu
- Start/stop monitoring
- Quick dashboard access
- About dialog

### Chrome App Customization

**Icon Generation:**
```bash
cd chrome-app/icons
python generate_icons.py
```

**Custom Port Configuration:**
```bash
# Edit chrome-app/window.html
# Change WebSocket URL: ws://localhost:8888/ws
# To custom port: ws://localhost:YOUR_PORT/ws
```

### Backend Configuration

**Environment Variables:**
```bash
export MONITOR_PORT=8888
export MONITOR_HOST=localhost
export MONITOR_DEBUG=false
```

**Custom Hardware Detection:**
```python
# Edit back-end/hardware.py
# Modify get_system_info() function
# Add custom sensors or modify detection logic
```

---

## 🧪 Testing Installation

### Verify Desktop Integration
```bash
# Test launcher
python launch_monitor.py

# Test dependencies
python -c "import aiohttp, psutil, GPUtil; print('Dependencies OK')"

# Test Chrome app path
python -c "from pathlib import Path; print(Path('chrome-app/window.html').exists())"
```

### Verify Autostart
```bash
# Windows (check registry)
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v system-resource-monitor

# macOS (check LaunchAgent)
ls ~/Library/LaunchAgents/com.growmation21.system-resource-monitor.plist

# Linux (check autostart)
ls ~/.config/autostart/system-resource-monitor.desktop
```

### Verify System Tray
```bash
# Test tray dependencies
python -c "import pystray, PIL; print('Tray dependencies OK')"

# Run tray app
python system_tray.py
```

---

## 🔍 Troubleshooting

### Common Issues

**1. Chrome not found:**
```
Solution: Install Google Chrome or use default browser fallback
The app will automatically open in your default browser if Chrome is not found.
```

**2. Permission denied on shortcuts:**
```bash
# Windows: Run as Administrator
# macOS/Linux: Check file permissions
chmod +x ~/.local/share/applications/system-resource-monitor.desktop
```

**3. Backend server won't start:**
```bash
# Check port availability
netstat -an | grep 8888

# Try different port
python launch_monitor.py --port 9000
```

**4. Dependencies missing:**
```bash
# Install all requirements
pip install -r requirements.txt

# Manual installation
pip install aiohttp psutil GPUtil pystray Pillow
```

**5. System tray not working:**
```bash
# Install tray dependencies
python system_tray.py --install-tray-deps

# Run without tray
python system_tray.py --no-tray
```

### Debug Mode

**Enable Verbose Logging:**
```bash
# Set environment variable
export MONITOR_DEBUG=true

# Or modify launch_monitor.py
# Add debug prints and error handling
```

**Check Log Files:**
```bash
# Application logs (if configured)
tail -f ~/AppData/Local/system-resource-monitor/logs/app.log  # Windows
tail -f ~/Library/Application\ Support/system-resource-monitor/logs/app.log  # macOS
tail -f ~/.local/share/system-resource-monitor/logs/app.log  # Linux
```

---

## 🗑️ Uninstallation

### Complete Removal
```bash
# Remove all desktop integration
python desktop_integration.py --uninstall

# Manual cleanup (if needed)
# Windows:
# - Delete Desktop shortcut
# - Remove Start Menu entry
# - Delete registry key
# - Remove %LOCALAPPDATA%\system-resource-monitor\

# macOS:
# - Delete Desktop app bundle
# - Remove LaunchAgent plist
# - Remove ~/Library/Application Support/system-resource-monitor/

# Linux:
# - Delete Desktop file
# - Remove autostart entry
# - Remove ~/.local/share/system-resource-monitor/
```

### Service Removal (Windows)
```cmd
# If installed as Windows service
nssm stop SystemResourceMonitor
nssm remove SystemResourceMonitor confirm
```

---

## 🎯 Usage Examples

### Development Mode
```bash
# Run with auto-reload
python launch_monitor.py --port 8888

# Run backend only
cd back-end
python monitor.py

# Run frontend only (open chrome-app/window.html)
```

### Production Mode
```bash
# Install and enable autostart
python desktop_integration.py --install --autostart

# Run as system tray app
python system_tray.py

# Run minimized
python launch_monitor.py --minimized
```

### Monitoring Multiple Systems
```bash
# Start on different ports
python launch_monitor.py --port 8888  # System 1
python launch_monitor.py --port 8889  # System 2

# Access via browser
# http://localhost:8888  (System 1)
# http://localhost:8889  (System 2)
```

---

## 📞 Support

### Getting Help
1. Check this README for common solutions
2. Review log files for error messages
3. Test with minimal configuration
4. Check dependencies and permissions

### Reporting Issues
Include the following information:
- Operating system and version
- Python version
- Installation method used
- Error messages or logs
- Steps to reproduce the issue

---

## 🎉 Success!

After successful installation, you should have:
- ✅ Desktop shortcut working
- ✅ Application launching properly
- ✅ Backend server responding
- ✅ Chrome app displaying data
- ✅ System tray integration (optional)
- ✅ Autostart configured (if enabled)

**Access your monitor at:** `http://localhost:8888` or via the desktop shortcut!
