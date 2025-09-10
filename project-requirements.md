# System Resource Monitoring - Project Requirements

## Objective

The objective of this project is to impliment a local system resource monitoring app which runs in chrome as an app. (borderless window with a title bar but no address bar or tabs) The UI should be similar to the ui_example.jpg image. This app window should be movable across desktop monitors and resizeable by the user, but should be locked to always on top mode. The monitor app should be launched from a desktop icon and the app should not need a virtual environment. 

The project which much of the code was isolated from is located at Z:\development\ComfyUI-Crystools
Review that project for reference, if needed.

## Overview

This document outlines the requirements and implementation details for extracting the real-time system monitoring feature from ComfyUI-Crystools. The feature provides live indicators for CPU, RAM, GPU utilization, VRAM usage, and GPU temperature displayed as progress bars in the user interface.

## Architecture Overview

### Data Flow
1. **Hardware Monitoring Thread** runs continuously in the background
2. **Hardware Info Collector** gathers system statistics using platform libraries
3. **GPU Info Collector** gathers GPU-specific data via NVIDIA APIs
4. **WebSocket Broadcaster** sends real-time data to frontend clients
5. **Frontend UI Components** receive data and update visual indicators
6. **Settings System** allows users to configure which monitors to display

### Core Data Structure
```python
{
    'cpu_utilization': float,        # CPU usage percentage (0-100)
    'ram_total': int,               # Total RAM in bytes
    'ram_used': int,                # Used RAM in bytes  
    'ram_used_percent': float,      # RAM usage percentage (0-100)
    'hdd_total': int,               # Total disk space in bytes
    'hdd_used': int,                # Used disk space in bytes
    'hdd_used_percent': float,      # Disk usage percentage (0-100)
    'device_type': str,             # GPU device type identifier
    'gpus': [                       # Array of GPU data (supports multiple GPUs)
        {
            'gpu_utilization': float,    # GPU usage percentage (0-100)
            'gpu_temperature': float,    # GPU temperature in Celsius
            'vram_total': int,          # Total VRAM in bytes
            'vram_used': int,           # Used VRAM in bytes
            'vram_used_percent': float, # VRAM usage percentage (0-100)
        }
    ]
}
```

## Required Components

### 1. Backend Hardware Monitoring

#### Core Files
- `back-end/hardware.py` - Main hardware information orchestrator
- `back-end/gpu.py` - GPU-specific monitoring (NVIDIA/Jetson support)
- `back-end/monitor.py` - Threading and data collection management
- `back-end/hdd.py` - Hard drive monitoring utilities

#### Key Classes
- **`CHardwareInfo`** - Aggregates all hardware monitoring data
- **`CGPUInfo`** - Handles GPU detection and monitoring via pynvml/jtop
- **`CMonitor`** - Manages monitoring thread and data broadcasting

### 2. WebSocket Communication Layer

#### API Endpoints
- `PATCH /resources/monitor` - Update global monitoring settings
- `GET /resources/monitor/GPU` - Retrieve GPU information
- `PATCH /resources/monitor/GPU/{index}` - Configure per-GPU monitoring
- `GET /resources/monitor/HDD` - Retrieve available disk drives

#### WebSocket Events
- `'resources.monitor'` - Real-time monitoring data broadcast

### 3. Frontend UI Components

#### Core Files
- `front-end/monitor.ts` - Main monitor controller and settings management
- `front-end/monitorUI.ts` - UI rendering, progress bars, and real-time updates
- `front-end/progressBarUIBase.ts` - Base class for progress bar components
- `front-end/styles.ts` - Color definitions and styling constants
- `front-end/monitor.css` - CSS styling for monitor displays

#### UI Features
- Real-time percentage progress bars
- Color-coded indicators (CPU: green, RAM: dark green, GPU: blue, VRAM: darker blue)
- Temperature gradient display (green to red)
- Hover tooltips with detailed usage information
- Configurable display options and refresh rates

### 4. Integration Requirements

#### Settings System
- User preferences for enabling/disabling specific monitors
- Configurable refresh rate (1-30 seconds, default: 5 seconds)
- Monitor size configuration (width/height)
- Per-GPU monitoring toggles

#### Menu Integration
- Integration with application menu system
- Settings panels for configuration

## Installation Instructions

### Prerequisites

#### System Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.15+
- **Python**: 3.8+ with pip package manager
- **Node.js**: 16+ (if building TypeScript components)
- **NVIDIA GPU**: Optional, for GPU monitoring features

#### Hardware Support
- **CPU Monitoring**: All platforms via psutil
- **RAM Monitoring**: All platforms via psutil  
- **Disk Monitoring**: All platforms via psutil
- **GPU Monitoring**: NVIDIA GPUs only (CUDA-capable)

### Python Dependencies

Install required packages:

```bash
# Core monitoring dependencies
pip install psutil>=5.8.0
pip install py-cpuinfo>=8.0.0

# GPU monitoring (NVIDIA)
pip install pynvml>=11.4.1

# PyTorch for CUDA detection (optional but recommended)
pip install torch>=1.9.0

# Web framework dependencies
pip install aiohttp>=3.8.0
```

### Alternative Installation via Requirements File

Create `requirements.txt`:
```text
# Core system monitoring
psutil>=5.8.0
py-cpuinfo>=8.0.0

# GPU monitoring
pynvml>=11.4.1
jetson-stats>=4.0.0  # For Jetson devices only

# PyTorch ecosystem
torch>=1.9.0

# Web server
aiohttp>=3.8.0

# Optional: Additional hardware info
GPUtil>=1.4.0
```

Install with:
```bash
pip install -r requirements.txt
```

### Frontend Dependencies

If building TypeScript components:

```bash
# Install Node.js dependencies
npm install typescript@^4.9.0
npm install @types/node@^18.0.0

# Build TypeScript to JavaScript
npx tsc --build tsconfig.json
```

### Platform-Specific Setup

#### Windows
```powershell
# Install Python packages
pip install psutil pynvml py-cpuinfo torch

# Verify NVIDIA drivers (for GPU monitoring)
nvidia-smi
```

#### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt update

# Install system dependencies
sudo apt install python3-pip python3-dev

# Install Python packages
pip3 install psutil pynvml py-cpuinfo torch

# For NVIDIA GPU monitoring
sudo apt install nvidia-utils-*
```

#### macOS
```bash
# Install via Homebrew
brew install python@3.9

# Install Python packages
pip3 install psutil py-cpuinfo torch

# Note: GPU monitoring not available on macOS
```

## Implementation Steps

### 1. Backend Implementation

1. **Create hardware monitoring classes**:
   ```python
   # Implement CHardwareInfo for system stats
   # Implement CGPUInfo for GPU monitoring
   # Implement CMonitor for threading
   ```

2. **Set up data collection**:
   ```python
   # Initialize monitoring with desired refresh rate
   monitor = CMonitor(rate=5, switchCPU=True, switchRAM=True, switchGPU=True)
   ```

3. **Implement WebSocket broadcasting**:
   ```python
   # Send real-time data to connected clients
   await send_message(hardware_data)
   ```

### 2. Frontend Implementation

1. **Create UI components**:
   ```typescript
   // Implement MonitorUI class for progress bars
   // Create settings panels for configuration
   // Add CSS styling for visual indicators
   ```

2. **Set up WebSocket client**:
   ```typescript
   // Listen for 'resources.monitor' events
   api.addEventListener('resources.monitor', updateDisplay);
   ```

3. **Implement real-time updates**:
   ```typescript
   // Update progress bars with new data
   // Handle multi-GPU scenarios
   // Apply color coding and animations
   ```

### 3. Integration Steps

1. **Menu system integration**
2. **Settings persistence implementation**  
3. **Error handling and fallbacks**

## Configuration Options

### Monitor Settings
- **CPU Usage**: Enable/disable CPU utilization monitoring
- **RAM Usage**: Enable/disable memory usage monitoring  
- **Disk Usage**: Enable/disable storage monitoring with drive selection
- **GPU Usage**: Per-GPU utilization monitoring toggle
- **VRAM Usage**: Per-GPU memory monitoring toggle
- **GPU Temperature**: Per-GPU temperature monitoring with gradient display

### Display Settings
- **Refresh Rate**: 1-30 seconds (default: 5 seconds)
- **Monitor Width**: 40-200 pixels (default: 60 pixels)
- **Monitor Height**: 15-50 pixels (default: 30 pixels)
- **Position**: Floating, Always on Top, Position Locked (if supported)

### Color Scheme
```typescript
enum Colors {
  'CPU' = '#0AA015',      // Green
  'RAM' = '#07630D',      // Dark green
  'DISK' = '#730F92',     // Purple
  'GPU' = '#0C86F4',      // Blue
  'VRAM' = '#176EC7',     // Dark blue
  'TEMP_START' = '#00ff00', // Green (cool)
  'TEMP_END' = '#ff0000',   // Red (hot)
}
```

## Performance Considerations

### Resource Usage
- **CPU Overhead**: 0.1-0.5% system utilization
- **Memory Usage**: ~10-20MB for monitoring service
- **Network Traffic**: ~1KB per update cycle
- **Update Frequency**: Configurable 1-30 second intervals

### Optimization Tips
- Disable unused monitors to reduce overhead
- Increase refresh rate for better performance on slower systems
- Use efficient data structures for multi-GPU scenarios
- Implement proper error handling for hardware detection failures

## Troubleshooting

### Common Issues

1. **GPU monitoring not working**:
   - Verify NVIDIA drivers are installed
   - Check CUDA availability with `nvidia-smi`
   - Ensure pynvml is properly installed

2. **Permission errors**:
   - Run with appropriate system permissions
   - Check hardware access permissions on Linux

3. **High CPU usage**:
   - Increase refresh rate interval
   - Disable unnecessary monitoring features
   - Check for hardware detection loops

### Debug Information
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check hardware detection
from general.hardware import CHardwareInfo
hardware = CHardwareInfo()
print(hardware.getStatus())
```

## License and Dependencies

This implementation is based on the ComfyUI-Crystools project. Ensure compliance with:
- Original project license terms
- Third-party library licenses (psutil, pynvml, etc.)
- NVIDIA software license agreements

## Future Enhancements

- AMD GPU support via additional libraries
- Network usage monitoring
- Process-specific monitoring
- Historical data logging and charts
- Custom alert thresholds
- Export monitoring data to external systems
- Docker Container Monitoring
