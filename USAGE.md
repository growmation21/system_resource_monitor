# System Resource Monitor - User Manual

## 📖 Overview
The System Resource Monitor is a powerful Chrome app that provides real-time monitoring of your system's hardware resources including CPU, memory, disk usage, and GPU performance. This manual covers all features and functionality.

## 🚀 Getting Started

### Launching the Application

#### Method 1: Desktop Shortcut (Recommended)
1. Double-click the "System Resource Monitor" icon on your desktop
2. The application starts automatically and opens the monitoring window
3. Backend service initializes and begins collecting system data

#### Method 2: Start Menu
1. Click Windows Start button
2. Type "System Resource Monitor"
3. Click the application icon to launch

#### Method 3: System Tray
1. Look for the monitor icon in your system tray (bottom-right corner)
2. Right-click the icon
3. Select "Open Monitor" from the context menu

#### Method 4: Manual Launch
```powershell
# Open PowerShell in the installation directory
cd "C:\Program Files\SystemResourceMonitor"

# Start with default settings
python launch_monitor.py

# Start with custom port
python launch_monitor.py --port 8888

# Start with specific configuration
python launch_monitor.py --config custom_settings.json
```

### First-Time Setup

When you first launch the application, you'll see the **Quick Setup Wizard**:

1. **Welcome Screen**: Introduction and overview of features
2. **Hardware Detection**: Automatic detection of your system components
3. **Display Preferences**: Choose your preferred theme and layout
4. **Monitoring Selection**: Select which components to monitor
5. **Update Frequency**: Set how often data refreshes (1-30 seconds)
6. **Completion**: Review settings and start monitoring

## 🖥️ User Interface Overview

### Main Monitoring Window

The main window displays real-time system information in an organized layout:

```
┌─────────────────────────────────────────────────────┐
│  System Resource Monitor               [_] [□] [×]  │
├─────────────────────────────────────────────────────┤
│  🔧 Settings    📊 Performance    🔔 Notifications  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  💻 CPU Usage                   📊 Memory Usage     │
│  ▓▓▓▓▓▓▓░░░ 45%                ▓▓▓▓▓▓░░░░ 60%      │
│  8 Cores • 3.2 GHz             16 GB • 9.6 GB Used │
│                                                     │
│  💽 Disk Usage                  🎮 GPU Usage        │
│  C: ▓▓▓▓▓░░░░░ 55%             RTX 3070             │
│  D: ▓▓░░░░░░░░ 25%             ▓▓▓░░░░░░░ 35%      │
│                                 65°C • 4.2/8 GB    │
├─────────────────────────────────────────────────────┤
│  Last Update: 2 seconds ago    •    FPS: 60        │
└─────────────────────────────────────────────────────┘
```

### Interface Elements

#### Title Bar
- **Window Title**: Shows app name and current status
- **Control Buttons**: Minimize, maximize, close
- **Always-on-Top Indicator**: Pin icon when enabled

#### Toolbar
- **🔧 Settings**: Opens the comprehensive settings panel
- **📊 Performance**: Shows performance metrics and FPS counter
- **🔔 Notifications**: Displays alert status and notification settings
- **🔄 Refresh**: Manual refresh button (when needed)

#### Data Display Sections

**CPU Section**:
- Usage percentage with visual bar
- Core count and current frequency
- Temperature (if sensor available)
- Per-core usage (expandable view)

**Memory Section**:
- RAM usage percentage and visual indicator
- Total memory and used amount
- Available memory
- Memory type and speed (in detailed view)

**Disk Section**:
- Usage for each detected drive
- Free space and total capacity
- Read/write activity indicators
- Drive health status (if available)

**GPU Section** (NVIDIA GPUs):
- GPU utilization percentage
- Memory usage and temperature
- GPU name and driver version
- Multiple GPU support

#### Status Bar
- **Last Update Time**: Shows when data was last refreshed
- **FPS Counter**: Current refresh rate
- **Connection Status**: WebSocket connection indicator
- **Performance Mode**: Current optimization level

## ⚙️ Settings and Configuration

### Accessing Settings

Click the **🔧 Settings** button to open the comprehensive settings panel. The panel is organized into six main tabs:

### 1. General Settings Tab

#### Basic Configuration
- **Update Interval**: Set refresh rate (1-30 seconds)
  - Higher frequency = more current data, more CPU usage
  - Lower frequency = less system impact, delayed updates
- **Theme Selection**: 
  - **Auto**: Follows Windows system theme
  - **Dark**: Dark theme for low-light environments
  - **Light**: Light theme for bright environments
- **Language**: Interface language selection (if multiple available)
- **Startup Behavior**: 
  - Launch with Windows
  - Start minimized to tray
  - Restore last window position

#### Display Options
- **Always on Top**: Keep window above all other applications
- **Window Opacity**: Adjust transparency (10-100%)
- **Compact Mode**: Reduced interface for small screens
- **Hide When Minimized**: Minimize to system tray instead of taskbar

### 2. Hardware Tab

#### CPU Monitoring
- **Enable CPU Monitoring**: Toggle CPU usage tracking
- **Show Per-Core Usage**: Display individual core utilization
- **Temperature Monitoring**: Enable CPU temperature (if sensors available)
- **Frequency Display**: Show current CPU frequency
- **Load Average**: Display system load averages

#### Memory Monitoring
- **Enable Memory Monitoring**: Toggle RAM usage tracking
- **Show Detailed Memory**: Break down memory usage by type
- **Cache Information**: Display system cache usage
- **Swap Usage**: Monitor virtual memory usage (if applicable)

#### Storage Monitoring
- **Drive Selection**: Choose which drives to monitor
  - Individual drive toggles
  - Include/exclude network drives
  - Monitor external drives
- **Health Monitoring**: Drive health status (if supported)
- **Activity Indicators**: Show read/write activity

#### GPU Monitoring
- **Enable GPU Monitoring**: Toggle NVIDIA GPU tracking
- **Multi-GPU Support**: Configure multiple GPU display
- **Temperature Alerts**: Set GPU temperature thresholds
- **Memory Tracking**: Monitor GPU memory usage
- **Performance States**: Display GPU power states

### 3. Display Tab

#### Window Configuration
- **Window Size**: 
  - Predefined sizes (Small: 400x300, Medium: 600x450, Large: 800x600)
  - Custom dimensions
  - Auto-resize based on content
- **Position Settings**:
  - Remember last position
  - Snap to screen edges
  - Multi-monitor positioning
  - Center on startup

#### Visual Customization
- **Color Schemes**:
  - **Default**: Standard system colors
  - **High Contrast**: Improved accessibility
  - **Custom**: User-defined color palette
  - **Performance**: Optimized for minimal resource usage
- **Progress Bar Styles**:
  - Classic horizontal bars
  - Circular indicators
  - Numerical only
  - Graph-style displays
- **Font Settings**:
  - Font family selection
  - Size adjustment (Small/Medium/Large)
  - Weight options (Normal/Bold)

### 4. Notifications Tab

#### Alert Configuration
- **CPU Usage Alerts**:
  - Warning threshold (default: 80%)
  - Critical threshold (default: 90%)
  - Sustained duration before alert (5-60 seconds)
- **Memory Usage Alerts**:
  - Warning threshold (default: 85%)
  - Critical threshold (default: 95%)
  - Low memory warnings
- **Temperature Alerts**:
  - CPU temperature limits (default: 80°C warning, 90°C critical)
  - GPU temperature limits (default: 85°C warning, 95°C critical)
- **Disk Space Alerts**:
  - Low disk space warnings (default: 10% free)
  - Critical disk space (default: 5% free)

#### Notification Methods
- **Visual Notifications**:
  - Windows 10/11 toast notifications
  - In-app alert indicators
  - Tray icon status changes
  - Window border color changes
- **Audio Notifications**:
  - System sound alerts
  - Custom sound files
  - Volume control
  - Mute option
- **Advanced Options**:
  - Snooze functionality
  - Repeat intervals
  - Auto-dismiss timers
  - Do not disturb mode

### 5. Performance Tab

#### Optimization Settings
- **Performance Mode**:
  - **Balanced**: Standard monitoring with good performance
  - **High Performance**: Faster updates, higher resource usage
  - **Power Saver**: Reduced update frequency for battery life
  - **Custom**: User-defined optimization parameters

#### Data Collection
- **Sampling Rate**: Internal data collection frequency
- **Data Retention**: How long to keep historical data
- **Averaging**: Smooth data fluctuations
- **Precision**: Decimal places for numerical displays

#### System Impact
- **CPU Priority**: Process priority level
- **Memory Limit**: Maximum RAM usage for the application
- **Network Throttling**: Limit WebSocket data rate
- **Background Mode**: Reduced activity when window not visible

#### Advanced Performance
- **Multi-threading**: Enable parallel data collection
- **Caching**: Cache system information for faster access
- **Batch Updates**: Group multiple updates for efficiency
- **Hardware Acceleration**: Use GPU for UI rendering (if available)

### 6. Advanced Tab

#### Data Export
- **Export Formats**:
  - JSON format for data analysis
  - CSV format for spreadsheet applications
  - XML format for system integration
  - Custom format templates
- **Export Options**:
  - Manual export on demand
  - Scheduled automatic exports
  - Real-time streaming to files
  - Cloud service integration (future feature)

#### Import/Export Settings
- **Settings Backup**:
  - Export current configuration to file
  - Create automatic backup schedules
  - Include/exclude specific setting categories
- **Settings Restore**:
  - Import configuration from file
  - Merge with current settings or replace completely
  - Validate imported settings for compatibility

#### Developer Options
- **Debug Mode**: Enable detailed logging and diagnostics
- **API Access**: Enable REST API endpoints for external access
- **WebSocket Settings**: Configure connection parameters
- **Testing Tools**: Built-in diagnostic and testing features

#### Reset Options
- **Reset to Defaults**: Restore all settings to initial values
- **Selective Reset**: Reset specific setting categories
- **Factory Reset**: Complete application reset including cache
- **Backup Before Reset**: Automatic backup creation before reset

## 🎮 Advanced Features

### Multi-Monitor Support

#### Configuration
1. Open Settings → Display Tab
2. Enable "Multi-Monitor Mode"
3. Configure per-monitor settings:
   - Primary display selection
   - Window behavior on each monitor
   - DPI scaling adjustments
   - Monitor-specific themes

#### Features
- **Snap-to-Edge**: Windows automatically snap to monitor edges
- **Monitor Memory**: Remembers position on each monitor
- **Cross-Monitor Dragging**: Smooth window movement between displays
- **DPI Awareness**: Proper scaling on high-resolution displays

### System Tray Integration

#### Tray Icon Features
- **Right-Click Menu**:
  - Open Monitor
  - Quick Settings
  - Enable/Disable Monitoring
  - Exit Application
- **Status Indicators**:
  - Normal: Green icon
  - Warning: Yellow icon (resource threshold exceeded)
  - Critical: Red icon (critical threshold exceeded)
  - Disconnected: Gray icon (backend not running)

#### Tray Notifications
- **Resource Alerts**: Popup notifications for threshold violations
- **System Status**: Connection status and health indicators
- **Quick Actions**: Direct access to common functions

### Keyboard Shortcuts

#### Global Shortcuts (work when app has focus)
- **Ctrl+R**: Manual refresh
- **Ctrl+S**: Open settings panel
- **Ctrl+T**: Toggle always-on-top
- **Ctrl+M**: Minimize to tray
- **Ctrl+Q**: Quick exit
- **F11**: Toggle fullscreen mode
- **F5**: Refresh data
- **Esc**: Close settings panel or exit fullscreen

#### Settings Panel Shortcuts
- **Tab**: Navigate between fields
- **Ctrl+Tab**: Switch between tabs
- **Enter**: Apply changes
- **Esc**: Cancel changes
- **Ctrl+Z**: Undo last change
- **Ctrl+Shift+R**: Reset current tab to defaults

### Performance Monitoring

#### Real-Time Metrics
- **FPS Counter**: Shows current refresh rate
- **Frame Time**: Time between updates
- **CPU Overhead**: Application's CPU usage
- **Memory Footprint**: Application's RAM usage
- **Network Traffic**: WebSocket data transfer rates

#### Performance Profiler
- **Resource Usage Graph**: Historical view of app performance
- **Bottleneck Detection**: Identifies performance issues
- **Optimization Suggestions**: Recommendations for better performance
- **Benchmark Mode**: Test system performance under load

## 📊 Data Interpretation

### Understanding the Metrics

#### CPU Usage
- **Percentage**: Current CPU utilization (0-100%)
- **Per-Core**: Individual core usage (helpful for multi-threaded apps)
- **Frequency**: Current CPU speed (may vary with power management)
- **Temperature**: CPU die temperature (requires sensor support)

**Normal Values**:
- Idle: 5-15%
- Light use: 20-40%
- Heavy use: 60-85%
- Critical: >90% sustained

#### Memory Usage
- **Used**: Currently allocated RAM
- **Available**: RAM available for new applications
- **Cached**: System cache (not necessarily "used")
- **Percentage**: Used memory as percentage of total

**Normal Values**:
- Good: <70% usage
- Acceptable: 70-85%
- High: 85-95%
- Critical: >95%

#### Disk Usage
- **Used Space**: Occupied storage per drive
- **Free Space**: Available storage
- **Percentage**: Used space as percentage of total capacity
- **Activity**: Read/write operations (if supported)

**Recommendations**:
- Keep >15% free space for optimal performance
- Monitor system drive (usually C:) closely
- Consider cleanup when >85% full

#### GPU Usage (NVIDIA)
- **GPU Utilization**: Processing load (0-100%)
- **Memory Usage**: VRAM utilization
- **Temperature**: GPU die temperature
- **Power State**: Current performance level

**Typical Values**:
- Idle: 0-5% GPU, <50°C
- Gaming: 60-95% GPU, 60-80°C
- Mining/Compute: 95-100% GPU, 70-85°C

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Symptoms**: Double-clicking shortcut does nothing, or error messages appear

**Solutions**:
1. **Check Python Installation**:
   ```powershell
   python --version
   # Should show Python 3.7 or later
   ```

2. **Verify Dependencies**:
   ```powershell
   pip list | findstr psutil
   pip list | findstr aiohttp
   pip list | findstr websockets
   ```

3. **Run Diagnostic**:
   ```powershell
   python tests/test_hardware_monitoring.py
   ```

4. **Check Logs**:
   - Look in `logs/system_monitor.log` for error messages
   - Check Windows Event Viewer for application errors

#### Chrome App Not Loading

**Symptoms**: Chrome app shows error or blank screen

**Solutions**:
1. **Verify Chrome Extensions**:
   - Go to `chrome://extensions/`
   - Ensure "System Resource Monitor" is enabled
   - Check for error messages

2. **Reload Extension**:
   - Click refresh icon next to the extension
   - Or remove and re-add the extension

3. **Check Developer Mode**:
   - Ensure Developer mode is enabled in Chrome
   - Extension must be loaded as "unpacked"

4. **Clear Chrome Data**:
   - Clear browser cache and cookies
   - Restart Chrome browser

#### No Data Displaying

**Symptoms**: Monitor opens but shows no system information

**Solutions**:
1. **Check Backend Connection**:
   ```powershell
   # Test if backend is running
   netstat -an | findstr :8765
   ```

2. **Restart Backend Service**:
   ```powershell
   python launch_monitor.py --restart
   ```

3. **Verify WebSocket Connection**:
   - Check browser developer console (F12)
   - Look for WebSocket connection errors

4. **Test Individual Components**:
   ```powershell
   python back-end/hardware.py    # Test CPU/Memory
   python back-end/gpu.py         # Test GPU
   python back-end/hdd.py         # Test Disk
   ```

#### High CPU Usage

**Symptoms**: System Resource Monitor using excessive CPU

**Solutions**:
1. **Reduce Update Frequency**:
   - Settings → General → Update Interval → 5+ seconds
   - Disable GPU monitoring if not needed

2. **Enable Performance Mode**:
   - Settings → Performance → Power Saver mode
   - Reduce data retention and precision

3. **Check for Background Processes**:
   ```powershell
   # Check if multiple instances are running
   tasklist | findstr python
   ```

4. **Update Graphics Drivers**:
   - Outdated drivers can cause high CPU usage
   - Update NVIDIA drivers for GPU monitoring

#### GPU Monitoring Not Working

**Symptoms**: GPU section shows "Not Available" or errors

**Solutions**:
1. **Install NVIDIA Drivers**:
   - Download latest drivers from NVIDIA website
   - Restart system after installation

2. **Install CUDA Toolkit** (optional but recommended):
   - Download from NVIDIA developer site
   - Provides additional monitoring capabilities

3. **Check NVIDIA Software**:
   ```powershell
   nvidia-smi
   # Should list your GPU(s)
   ```

4. **Install pynvml**:
   ```powershell
   pip install pynvml
   ```

#### Settings Not Saving

**Symptoms**: Configuration changes don't persist after restart

**Solutions**:
1. **Check File Permissions**:
   - Ensure write access to installation directory
   - Run as administrator if needed

2. **Verify Chrome Storage**:
   - Chrome app settings use Chrome's storage API
   - Check if Chrome has enough storage space

3. **Manual Settings Export**:
   - Settings → Advanced → Export Settings
   - Save backup copy of configuration

4. **Reset Settings**:
   - Settings → Advanced → Reset to Defaults
   - Reconfigure from scratch

### Performance Optimization

#### Optimizing for Low-End Systems

1. **Reduce Update Frequency**: Set to 5-10 seconds
2. **Disable Unnecessary Monitoring**: Turn off GPU if not needed
3. **Use Power Saver Mode**: Settings → Performance → Power Saver
4. **Simplify Display**: Use numerical display instead of graphs
5. **Reduce Window Size**: Smaller window = less rendering overhead

#### Optimizing for High-End Systems

1. **Increase Update Frequency**: Set to 1-2 seconds for responsive updates
2. **Enable All Monitoring**: CPU, Memory, Disk, GPU
3. **Use High Performance Mode**: Settings → Performance → High Performance
4. **Enable Advanced Graphics**: Smooth animations and transitions
5. **Multi-Monitor Setup**: Spread across multiple displays

## 📋 Maintenance and Updates

### Regular Maintenance

#### Weekly Tasks
- **Clear Log Files**: Remove old log files to save disk space
- **Check for Updates**: Look for application updates
- **Verify Settings**: Ensure configuration is still optimal
- **Performance Check**: Monitor app's own resource usage

#### Monthly Tasks
- **Export Settings**: Create backup of current configuration
- **Clean Temporary Files**: Clear cache and temporary data
- **Update Dependencies**: Check for Python package updates
- **System Health Check**: Run full diagnostic test

### Backup and Restore

#### Creating Backups
```powershell
# Automatic backup
python settings_manager.py --backup

# Manual backup with timestamp
python settings_manager.py --export "backup_$(date +%Y%m%d).json"
```

#### Restoring from Backup
```powershell
# Restore from latest backup
python settings_manager.py --restore

# Restore from specific file
python settings_manager.py --import "backup_20250910.json"
```

### Application Updates

#### Checking for Updates
1. **Automatic Check**: App checks for updates on startup
2. **Manual Check**: Settings → Advanced → Check for Updates
3. **Version Information**: Help → About shows current version

#### Installing Updates
1. **Automatic Installation**: Enable in Settings → General
2. **Manual Installation**: Download and run new installer
3. **Settings Preservation**: Updates preserve your configuration

## 🎯 Tips and Best Practices

### Optimal Configuration

#### For Gaming Systems
- Update frequency: 2-3 seconds
- Enable GPU monitoring
- Set temperature alerts (CPU: 80°C, GPU: 85°C)
- Use dark theme to reduce screen glare
- Position on secondary monitor

#### For Workstations
- Update frequency: 5 seconds
- Monitor all drives
- Enable memory and CPU alerts
- Use compact mode for space efficiency
- Enable always-on-top during intensive tasks

#### For Laptops
- Use Power Saver mode
- Reduce update frequency to 10 seconds
- Disable GPU monitoring if not needed
- Enable battery-specific optimizations
- Use system tray mode to save screen space

### Advanced Usage

#### Integration with Other Tools
- **Export data to Excel**: Use CSV export for analysis
- **Monitoring Scripts**: Use API endpoints for automation
- **Alert Integration**: Configure external notification systems
- **Performance Logging**: Set up automated performance logging

#### Custom Configurations
- **Create profiles**: Save different configurations for different scenarios
- **Scheduled settings**: Change settings based on time of day
- **Conditional monitoring**: Enable/disable features based on system state
- **External triggers**: Use command-line options for automation

## ❓ Frequently Asked Questions

### General Questions

**Q: Does this work on Mac or Linux?**
A: Currently optimized for Windows 10/11. Linux support may work with modifications. Mac support is not currently available.

**Q: Can I monitor multiple computers?**
A: Each installation monitors one computer. For multiple systems, install on each computer separately.

**Q: Is this safe to run continuously?**
A: Yes, the application is designed for 24/7 operation with minimal system impact.

### Technical Questions

**Q: What's the difference between this and Task Manager?**
A: This provides a dedicated, always-visible, customizable monitoring window with advanced features like GPU monitoring, notifications, and data export.

**Q: Why use Chrome app instead of a regular program?**
A: Chrome apps provide excellent UI flexibility, automatic updates, cross-platform compatibility, and robust security.

**Q: Can I modify the interface?**
A: Yes, the Chrome app interface can be customized through settings, themes, and layout options.

### Troubleshooting Questions

**Q: The application uses too much CPU. How can I fix this?**
A: Increase the update interval, disable GPU monitoring, or switch to Power Saver mode in Performance settings.

**Q: My GPU doesn't show up. What's wrong?**
A: Ensure you have an NVIDIA GPU with current drivers installed. AMD GPUs are not currently supported.

**Q: Can I run this on a work computer?**
A: Check with your IT department about installing applications and monitoring system resources.

## 📞 Getting Support

### Self-Help Resources
1. **Built-in Diagnostics**: Settings → Advanced → Run Diagnostics
2. **Test Suite**: Run `python tests/run_all_tests.py`
3. **Log Analysis**: Check `logs/system_monitor.log` for errors
4. **Documentation**: Review installation and troubleshooting guides

### Reporting Issues
When reporting problems, please include:
- Windows version and build number
- Python version (`python --version`)
- Hardware specifications (CPU, RAM, GPU)
- Error messages from logs
- Steps to reproduce the issue
- Screenshots if applicable

### System Information Collection
```powershell
# Collect system information for support
python diagnostic_tool.py --system-info > system_report.txt
```

This comprehensive user manual covers all aspects of using the System Resource Monitor. For additional help or specific questions not covered here, refer to the troubleshooting section or run the built-in diagnostic tools.
