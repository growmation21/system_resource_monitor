# System Resource Monitor - Installation Guide

## 📋 Overview
This guide provides step-by-step instructions for installing and setting up the System Resource Monitor Chrome Extension on Windows 10/11 systems.

## 🔧 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (version 1903 or later) or Windows 11
- **Python**: Version 3.7 or later
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100MB free disk space
- **Network**: Internet connection for dependency installation

### Recommended Requirements
- **Python**: Version 3.9 or later for optimal performance
- **Chrome Browser**: Latest version for Chrome Extension support
- **GPU**: NVIDIA GPU with current drivers for GPU monitoring
- **Memory**: 16GB RAM for smooth operation with multiple applications

### Hardware Compatibility
- **CPU**: Any x64 processor (Intel/AMD)
- **GPU**: NVIDIA GPUs supported via CUDA/NVML libraries
- **Storage**: SSD recommended for faster application startup
- **Displays**: Multi-monitor setups fully supported

## 📦 Installation Methods

### Method 1: Automatic Installation (Recommended)

#### Step 1: Download and Extract
1. Download the System Resource Monitor package
2. Extract to a permanent location (e.g., `C:\Program Files\SystemResourceMonitor\`)
3. Open PowerShell or Command Prompt as Administrator

#### Step 2: Run Automated Installer
```powershell
cd "C:\Program Files\SystemResourceMonitor"
python install.py

# Or create desktop shortcuts for easy launching
python create_shortcuts.py --create
```

**What the installer does:**
- ✅ Checks Python version compatibility
- ✅ Installs required Python packages
- ✅ Creates desktop shortcuts
- ✅ Sets up Windows startup integration (optional)
- ✅ Configures Chrome Extension integration
- ✅ Creates system tray shortcuts
- ✅ Validates all dependencies

#### Step 3: Complete Setup
1. Follow the installer prompts
2. Choose installation options:
   - Desktop shortcut creation
   - Windows startup integration
   - System tray integration
   - Chrome Extension registration
3. Wait for dependency installation to complete
4. Verify installation with the test launcher

### Method 2: Manual Installation

#### Step 1: Install Python Dependencies
```powershell
# Core monitoring dependencies
pip install psutil aiohttp websockets

# Optional GPU monitoring (NVIDIA only)
pip install pynvml py-cpuinfo

# Development and testing (optional)
pip install pytest pytest-asyncio
```

#### Step 2: Configure Chrome Extension
1. Open Chrome browser
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked"
5. Select the `chrome-extension` folder from the installation directory
6. The System Resource Monitor extension should appear in your toolbar

#### Step 3: Create Desktop Integration
```powershell
# Run desktop integration script
python desktop_integration.py --install

# Or create shortcuts manually
python desktop_integration.py --create-shortcuts
```

## 🚀 First Launch

### Starting the Application

#### Method 1: Desktop Shortcut
1. Double-click the "System Resource Monitor" desktop icon
2. The backend server will start automatically
3. Chrome Extension will be available in the browser toolbar

#### Method 2: Manual Launch
```powershell
# Navigate to installation directory
cd "C:\Program Files\SystemResourceMonitor"

# Start the monitoring service (with console window)
python launch_monitor.py

# Start in background mode (no console window)  
python launch_monitor.py --hidden

# Or use PowerShell launcher with system tray
powershell -ExecutionPolicy Bypass -File Start-Monitor.ps1 -SystemTray

# Or specify custom port
python launch_monitor.py --port 8888
```

#### Method 3: Background Mode (Recommended)
```powershell
# Option A: Hidden console mode
python launch_monitor.py --hidden

# Option B: System tray mode (with GUI controls)
python system_tray_launcher.py

# Option C: PowerShell launcher (auto-detects best mode)
powershell -ExecutionPolicy Bypass -File Start-Monitor.ps1 -SystemTray

# Option D: Batch file (simplest)
start_monitor_background.bat
```

#### Method 4: System Tray
1. Look for the System Resource Monitor icon in the system tray  
2. Right-click for options: Start/Stop/Restart/Status
3. Application runs completely in background

### Initial Configuration

#### First-Time Setup Wizard
1. **Monitor Selection**: Choose which hardware components to monitor
   - ✅ CPU usage and temperature
   - ✅ Memory usage and availability
   - ✅ Disk usage for selected drives
   - ✅ GPU utilization (if NVIDIA GPU detected)

2. **Display Preferences**: Configure the monitoring display
   - Update frequency (1-30 seconds)
   - Theme selection (Dark/Light/Auto)
   - Window positioning and size
   - Always-on-top behavior

3. **Advanced Settings**: Fine-tune monitoring behavior
   - Notification thresholds
   - Data export options
   - Performance optimization
   - Multi-monitor configuration

#### Testing Your Installation
```powershell
# Run the test suite to verify everything works
python tests/run_all_tests.py

# Or run individual test categories
python tests/test_hardware_monitoring.py
python tests/test_integration.py
```

## 🔧 Configuration Options

### Basic Configuration
- **Update Interval**: 1-30 seconds (default: 2 seconds)
- **Theme**: Dark/Light/Auto (follows system theme)
- **Window Size**: Customizable from 400x300 to 1200x800
- **Position**: Remembers last position across sessions

### Advanced Configuration
- **GPU Monitoring**: Enable/disable NVIDIA GPU monitoring
- **Disk Selection**: Choose specific drives to monitor
- **Notifications**: Set thresholds for CPU/Memory/Temperature alerts
- **Performance**: Adjust refresh rates and data retention
- **Export**: Configure automatic data export and logging

### Settings Management
```javascript
// Access settings programmatically
const settings = {
    theme: 'dark',
    updateInterval: 2000,
    showGPU: true,
    notifications: {
        enabled: true,
        cpuThreshold: 80,
        memoryThreshold: 85
    }
};

// Import/Export settings
// Settings → Export Configuration → Save to file
// Settings → Import Configuration → Load from file
```

## 🔄 Background Operation

### Running Without Console Window

The System Resource Monitor can run completely in the background without keeping a command window open. This provides a cleaner user experience and prevents accidental closure.

#### Available Background Modes

**1. Hidden Console Mode** (Simple, no dependencies)
```powershell
python launch_monitor.py --hidden
```
- Runs backend server in background
- No console window visible
- Stop via Task Manager or system shutdown

**2. System Tray Mode** (Recommended, with GUI controls)  
```powershell
# Install dependencies first
pip install pystray pillow

# Start system tray launcher
python system_tray_launcher.py
```
- Adds icon to system tray
- Right-click menu for Start/Stop/Restart/Status
- Visual indicator of running state
- Easy access to Chrome Extension setup

**3. PowerShell Launcher** (Auto-configuring)
```powershell
powershell -ExecutionPolicy Bypass -File Start-Monitor.ps1 -SystemTray
```
- Automatically installs system tray dependencies
- Falls back to hidden mode if needed  
- Shows setup instructions
- Clean PowerShell interface

**4. Batch File** (Simplest for non-technical users)
```batch
start_monitor_background.bat
```
- Double-click to start
- Automatically uses background mode
- Shows brief confirmation message

#### Creating Desktop Shortcuts

For easy access, create desktop shortcuts for different launch modes:
```powershell
# Create all available shortcuts
python create_shortcuts.py --create

# This creates:
# - System Resource Monitor.lnk (normal mode)
# - System Resource Monitor (Background).lnk (hidden mode)
# - System Resource Monitor (Tray).lnk (system tray mode)
# - Start System Monitor (PowerShell).lnk (PowerShell launcher)
```

#### Managing Background Processes

**To check if monitor is running:**
```powershell
# Check for python processes
Get-Process -Name "python*" | Where-Object {$_.MainWindowTitle -like "*monitor*"}

# Check if port is in use
netstat -an | findstr :8888
```

**To stop background monitor:**
```powershell
# Stop all python processes (use with caution)
Stop-Process -Name "python*" -Force

# Or stop specific port listener
# Use system tray right-click → Quit (recommended)
```

### System Tray Features

When using system tray mode, you get these features:

- **Visual Status**: Icon changes color based on server status (green=running, red=stopped)
- **Right-Click Menu**:
  - Start/Stop Monitor
  - Restart Monitor  
  - Show Status
  - Open Chrome Extensions page
  - View Setup Instructions
  - Open Monitor in Browser
  - Quit Application

- **Notifications**: Windows notifications for status changes
- **Auto-Start**: Automatically starts backend server when launched

## 🌐 Chrome Extension Integration

### Installing Chrome Extension

#### Automatic Installation (Recommended)
The installer automatically configures Chrome Extension integration. No manual steps required.

#### Manual Installation
1. Open Chrome browser
2. Go to `chrome://extensions/`
3. Enable Developer mode (toggle in top-right)
4. Click "Load unpacked extension"
5. Navigate to `[InstallDir]\chrome-extension`
6. Select folder and click "Open"
7. The extension will appear in Chrome's toolbar

### Chrome Extension Features
- **Real-time Monitoring**: Live data updates via WebSocket
- **Responsive Design**: Adapts to different window sizes
- **Settings Panel**: Comprehensive configuration interface
- **Keyboard Shortcuts**: Quick access to common functions
- **Always On Top**: Keep monitoring window above other applications
- **Popup Interface**: Quick system stats in toolbar popup

### Chrome Extension Permissions
The extension requests these permissions:
- **Storage**: Save settings and preferences
- **Windows**: Manage monitoring window behavior
- **Active Tab**: Basic extension functionality

## 🖥️ Multi-Monitor Support

### Configuration
1. Open Settings Panel
2. Navigate to "Display" tab
3. Configure monitor-specific settings:
   - Primary display selection
   - Window snap behavior
   - Monitor-specific positioning
   - DPI scaling adjustments

### Features
- **Automatic Detection**: Detects all connected monitors
- **Snap-to-Edge**: Windows snap to monitor edges
- **Remember Positions**: Window positions saved per monitor
- **DPI Awareness**: Proper scaling on high-DPI displays

## 🔍 Troubleshooting

### Common Issues

#### Installation Problems

**Issue**: Python not found
```powershell
# Solution: Install Python or add to PATH
# Download Python from python.org
# Or use Windows Store version
winget install Python.Python.3.11
```

**Issue**: Permission denied errors
```powershell
# Solution: Run as Administrator
# Right-click PowerShell → "Run as Administrator"
# Then run installation commands
```

**Issue**: Chrome Extension not loading
```powershell
# Solution: Check Chrome version and developer mode
# Ensure Chrome is updated to latest version
# Verify developer mode is enabled in chrome://extensions/
```

#### Runtime Problems

**Issue**: Backend server won't start
```powershell
# Check if port is in use
netstat -an | findstr :8765

# Try different port
python launch_monitor.py --port 8888
```

**Issue**: GPU monitoring not working
```powershell
# Install NVIDIA drivers and CUDA toolkit
# Verify GPU is detected
nvidia-smi

# Install pynvml if missing
pip install pynvml
```

**Issue**: High CPU usage
```powershell
# Reduce update frequency in settings
# Settings → Performance → Update Interval → 5 seconds
# Disable GPU monitoring if not needed
```

### Log Files and Debugging

#### Log Locations
- **Application Logs**: `logs/system_monitor.log`
- **Error Logs**: `logs/error.log`
- **Performance Logs**: `logs/performance.log`
- **WebSocket Logs**: `logs/websocket.log`

#### Debug Mode
```powershell
# Enable debug logging
python launch_monitor.py --log-level DEBUG

# Enable verbose output
python launch_monitor.py --verbose

# Check specific component
python back-end/hardware.py  # Test hardware monitoring
python back-end/gpu.py       # Test GPU detection
```

#### Getting Help
1. **Check Documentation**: Review user manual and FAQ
2. **Run Diagnostics**: Use built-in diagnostic tools
3. **Check Logs**: Review log files for error messages
4. **Test Suite**: Run `python tests/run_all_tests.py`
5. **System Info**: Use `python -c "import platform; print(platform.platform())"`

## 🔄 Updates and Maintenance

### Automatic Updates
- Monitor checks for updates on startup
- Optional automatic update installation
- Settings preserved during updates

### Manual Updates
```powershell
# Backup current settings
python settings_manager.py --export backup.json

# Update application files
# (Replace files with new version)

# Restore settings if needed
python settings_manager.py --import backup.json
```

### Uninstallation
```powershell
# Run automated uninstaller
python desktop_integration.py --uninstall

# Manual cleanup if needed
# Remove desktop shortcuts
# Remove startup entries
# Delete application folder
```

## 📊 Performance Optimization

### System Impact
- **CPU Usage**: <5% on modern systems
- **Memory Usage**: ~20-50MB RAM
- **Network**: Local WebSocket communication only
- **Storage**: Minimal disk I/O for settings and logs

### Optimization Tips
1. **Adjust Update Frequency**: Lower frequency = less CPU usage
2. **Disable Unused Monitoring**: Turn off GPU monitoring if not needed
3. **Use Dark Theme**: Reduces screen power consumption
4. **Close Unused Features**: Disable notifications if not needed
5. **Regular Cleanup**: Clear old log files periodically

## ✅ Verification Checklist

After installation, verify these items work:

- [ ] Backend server starts without errors
- [ ] Chrome Extension loads and connects to backend
- [ ] CPU and memory monitoring display correctly
- [ ] Disk usage shows for all drives
- [ ] GPU monitoring works (if NVIDIA GPU present)
- [ ] Settings panel opens and functions properly
- [ ] Window positioning and always-on-top work
- [ ] Desktop shortcuts launch the application
- [ ] System tray integration functions
- [ ] Application starts with Windows (if enabled)

## 🎯 Quick Start Summary

For experienced users who want to get started quickly:

```powershell
# 1. Extract files to permanent location
cd "C:\Program Files\SystemResourceMonitor"

# 2. Run installer
python install.py

# 3. Launch application
# Use desktop shortcut or:
python launch_monitor.py

# 4. Open Chrome Extension
# Click the extension icon in Chrome toolbar

# 5. Configure settings
# Click gear icon in monitor window
```

**Congratulations!** You now have a fully functional system resource monitor running on your Windows system. The application will remember your settings and preferences for future sessions.

For additional help, see the [User Manual](USAGE.md) or run the diagnostic tools included with the application.
