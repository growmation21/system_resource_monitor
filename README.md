# 🖥️ System Resource Monitor

<div align="center">

![System Resource Monitor](ui_example.jpg)

**A comprehensive real-time system monitoring solution with Chrome Extension integration**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green.svg)](https://chrome.google.com/webstore)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

</div>

## 🌟 Features

### 🔍 **Real-time Monitoring**
- **CPU Usage & Performance** - Multi-core monitoring with detailed metrics
- **Memory Management** - RAM usage, available memory, and virtual memory stats  
- **Disk I/O Monitoring** - Drive usage, read/write speeds, and health metrics
- **GPU Monitoring** - NVIDIA GPU utilization, VRAM usage, and temperature (CUDA-enabled)

### 🌐 **Chrome Extension Interface**
- **Modern Chrome Extension** - Manifest V3 compliant with toolbar integration
- **Real-time Dashboard** - Live updating metrics via WebSocket connection
- **Popup Interface** - Quick system stats accessible from Chrome toolbar
- **Settings Management** - Comprehensive configuration panel with persistence
- **Always-On-Top Mode** - Keep monitoring window above other applications

### ⚙️ **Advanced Configuration**
- **Customizable Update Intervals** - 1-30 second refresh rates
- **Theme Support** - Dark/Light themes with auto-detection
- **Multi-Monitor Support** - Works across multiple displays
- **Notification System** - Configurable alerts for resource thresholds
- **Performance Optimization** - Minimal system impact (<5% CPU usage)

### 🔧 **System Integration**
- **Windows Desktop Integration** - Desktop shortcuts and system tray support
- **Windows Startup** - Optional automatic startup with Windows
- **Service Mode** - Background monitoring service
- **Comprehensive Testing** - 150+ automated tests across all components

## 🚀 Quick Start

### 📋 Prerequisites
- **Windows 10/11** (version 1903 or later)
- **Python 3.7+** (3.9+ recommended)
- **Google Chrome** (latest version)
- **4GB RAM** minimum (8GB recommended)

### ⚡ Installation

#### Method 1: Automatic Setup (Recommended)
```powershell
# Clone the repository
git clone https://github.com/growmation21/system_resource_monitor.git
cd system_resource_monitor

# Run the automated installer
python install.py
```

#### Method 2: Manual Installation
```powershell
# Install Python dependencies
pip install psutil aiohttp websockets pynvml py-cpuinfo pytest pytest-asyncio

# Install Chrome Extension
# 1. Open chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the chrome-extension folder
```

### 🎯 Usage

#### Start the Backend Service
```powershell
# Start monitoring service
python launch_monitor.py

# Or specify custom port
python launch_monitor.py --port 8888
```

#### Access the Monitor
1. **Chrome Extension**: Click the extension icon in Chrome toolbar
2. **Desktop**: Use the desktop shortcut (if installed)
3. **Direct**: Open `http://localhost:8888` in your browser

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [📦 Installation Guide](INSTALL.md) | Complete installation instructions and setup |
| [📚 User Manual](USAGE.md) | Detailed usage guide and feature overview |
| [🎯 Project Status](PROJECT_STATUS.md) | Current development status and roadmap |
| [🔧 Implementation Plan](implementation-plan.md) | Technical implementation details |

## 🏗️ Architecture

### 🔧 **Backend Components**
```
back-end/
├── monitor.py          # Main monitoring service & WebSocket server
├── hardware.py         # Hardware detection & system information  
├── gpu.py             # NVIDIA GPU monitoring (NVML integration)
└── hdd.py             # Disk monitoring & I/O statistics
```

### 🌐 **Chrome Extension**
```
chrome-extension/
├── manifest.json       # Extension configuration (Manifest V3)
├── background.js       # Service worker & window management
├── popup.html/js       # Toolbar popup interface
├── monitor.html/js     # Main monitoring window
└── settings.html/js    # Configuration panel
```

### 🧪 **Testing Suite**
```
tests/
├── test_hardware_monitoring.py    # Hardware component tests
├── test_websocket_communication.py # WebSocket & API tests  
├── test_integration.py            # End-to-end integration tests
└── test_performance_validation.py # Performance & stress tests
```

## 🔬 Technical Specifications

### 📊 **Performance Metrics**
- **CPU Usage**: <5% on modern systems
- **Memory Footprint**: 20-50MB RAM
- **Update Frequency**: 1-30 seconds (configurable)
- **Network**: Local WebSocket communication only
- **Storage**: Minimal disk I/O for settings and logs

### 🔧 **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 (1903+) | Windows 11 |
| **Python** | 3.7+ | 3.9+ |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 100MB | 500MB |
| **GPU** | Any | NVIDIA (for GPU monitoring) |

### 🌐 **Browser Compatibility**
- **Google Chrome** 88+ (Manifest V3 support)
- **Microsoft Edge** 88+ (Chromium-based)
- **Other Chromium browsers** with extension support

## 🛠️ Development

### 🏃‍♂️ **Running Tests**
```powershell
# Run complete test suite
python tests/run_all_tests.py

# Run specific test categories
python tests/test_hardware_monitoring.py
python tests/test_integration.py
python tests/test_performance_validation.py
```

### 🔧 **Development Setup**
```powershell
# Install development dependencies
pip install pytest pytest-asyncio

# Enable debug logging
python launch_monitor.py --log-level DEBUG

# Run with verbose output
python launch_monitor.py --verbose
```

### 📝 **Project Structure**
```
system_resource_monitor/
├── 📁 back-end/              # Python monitoring service
├── 📁 chrome-extension/      # Chrome Extension (Manifest V3)
├── 📁 chrome-app/           # Legacy Chrome App (deprecated)
├── 📁 tests/                # Comprehensive testing suite
├── 📁 docs/                 # Project documentation
├── 📁 front-end/            # Web interface components
├── 📄 requirements.txt      # Python dependencies
├── 📄 launch_monitor.py     # Main launcher script
└── 📄 desktop_integration.py # Windows integration
```

## 🚀 Features in Detail

### 🖥️ **Real-time System Monitoring**

#### CPU Monitoring
- Multi-core usage tracking
- Per-core performance metrics
- CPU frequency and architecture detection
- Temperature monitoring (if supported)

#### Memory Management
- Physical RAM usage and availability
- Virtual memory statistics
- Memory pressure indicators
- Process memory breakdown

#### Storage Monitoring  
- Drive usage across all mounted volumes
- Read/write I/O statistics
- Disk health and performance metrics
- SSD vs HDD detection

#### GPU Monitoring (NVIDIA)
- GPU utilization and memory usage
- VRAM allocation and availability
- Temperature and power consumption
- Multi-GPU support (if available)

### 🌐 **Chrome Extension Interface**

#### Toolbar Integration
- Quick access popup with system summary
- Real-time status indicators
- One-click access to full monitoring window
- Settings and configuration panel

#### Monitoring Window
- Live-updating charts and graphs
- Responsive design for different window sizes
- Always-on-top functionality
- Customizable layout and themes

#### Settings Panel
- Backend connection configuration
- Display preferences (themes, window size)
- Monitoring component toggles
- Notification thresholds and alerts

## 🔍 Troubleshooting

### ❗ **Common Issues**

#### Installation Problems
```powershell
# Python not found
winget install Python.Python.3.11

# Permission denied
# Run PowerShell as Administrator

# Chrome extension not loading
# Ensure Developer Mode is enabled in chrome://extensions/
```

#### Runtime Issues
```powershell
# Backend server won't start
netstat -an | findstr :8888  # Check if port is in use
python launch_monitor.py --port 9999  # Try different port

# GPU monitoring not working
nvidia-smi  # Verify NVIDIA drivers
pip install pynvml  # Install GPU monitoring library
```

### 📋 **Debug Information**
```powershell
# Enable debug logging
python launch_monitor.py --log-level DEBUG

# Check system compatibility
python -c "import platform; print(platform.platform())"

# Test individual components
python back-end/hardware.py  # Test hardware detection
python back-end/gpu.py       # Test GPU monitoring
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 🔧 **Development Guidelines**
- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation for changes
- Ensure cross-platform compatibility

## 📋 Roadmap

### 🎯 **Current Status: v1.0 - Feature Complete**
- ✅ **Phase 1**: Hardware monitoring backend
- ✅ **Phase 2**: WebSocket communication
- ✅ **Phase 3**: Chrome Extension interface  
- ✅ **Phase 4**: Settings and configuration
- ✅ **Phase 5**: Desktop integration
- ✅ **Phase 6**: Advanced features
- ✅ **Phase 7**: Testing and validation

### 🚀 **Future Enhancements**
- 🔮 **Network monitoring** - Bandwidth usage and connection tracking
- 🔮 **Process monitoring** - Individual application resource usage
- 🔮 **Historical data** - Long-term performance tracking and analysis
- 🔮 **Remote monitoring** - Monitor multiple systems from one interface
- 🔮 **Mobile companion** - Android/iOS app for remote monitoring

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **psutil** - Cross-platform system monitoring library
- **aiohttp** - Async HTTP client/server framework  
- **websockets** - WebSocket implementation for Python
- **pynvml** - NVIDIA GPU monitoring interface
- **Chrome Extension APIs** - Browser integration capabilities

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/growmation21/system_resource_monitor/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/growmation21/system_resource_monitor/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/growmation21/system_resource_monitor/discussions)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the open source community

</div>
