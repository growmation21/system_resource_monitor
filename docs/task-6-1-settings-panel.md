# Settings Panel Implementation (Task 6.1)

## Overview

The Settings Panel provides a comprehensive configuration interface for the System Resource Monitor Chrome app. It allows users to customize various aspects of the monitoring display, performance settings, and system behavior.

## Features Implemented

### 1. Settings Dialog/Panel
- **Modal interface** with tabbed organization
- **Responsive design** that adapts to different screen sizes
- **Smooth animations** and professional styling
- **Theme support** (Dark/Light themes)

### 2. Monitor Enable/Disable Toggles
- **Hardware monitors**: CPU, Memory, Disk, GPU, VRAM, Temperature
- **Per-GPU controls**: Individual toggles for each detected GPU
- **Real-time visibility updates** when settings change
- **Visual feedback** with hover effects and animations

### 3. Refresh Rate Configuration
- **Slider control** with range from 100ms to 30 seconds
- **Real-time display** of current refresh rate
- **Automatic application** to WebSocket connection
- **Performance optimization** with minimum thresholds

### 4. Monitor Size Configuration
- **Width and height controls** with validation
- **Minimum/maximum constraints** for usability
- **Real-time application** to window dimensions
- **Input validation** to prevent invalid values

### 5. Advanced Configuration Options
- **Temperature unit selection** (Celsius/Fahrenheit)
- **Disk display mode** (Percentage/Absolute values)
- **Auto-reconnection settings** with attempt limits
- **Animation speed control** for UI transitions
- **Compact mode** for reduced screen space usage

## File Structure

```
chrome-app/
├── settings-panel.js          # Main settings panel implementation
├── settings-test.html         # Test page for settings functionality
└── window.html               # Updated with settings integration
```

## Integration Points

### SystemMonitor Class Extensions
- `setRefreshRate(rate)` - Updates WebSocket polling interval
- `updateMonitorVisibility(enabledMonitors)` - Shows/hides monitor displays
- `getLastData()` - Provides GPU information for per-GPU settings
- `lastData` property - Stores latest monitoring data

### Event System
- `settingsChanged` - Fired when any setting is modified
- `monitorVisibilityChanged` - Fired when monitor visibility changes
- `systemMonitorReady` - Fired when system monitor is initialized

## Settings Categories

### General Tab
- **Refresh Rate**: 100ms - 30 seconds
- **Window Size**: Width (200-800px), Height (150-600px)
- **Auto Reconnect**: Enable/disable automatic reconnection
- **Temperature Unit**: Celsius or Fahrenheit
- **Max Reconnect Attempts**: 1-50 attempts

### Monitors Tab
- **Hardware Monitors**: Individual toggles for each monitor type
- **GPU Monitors**: Per-GPU enable/disable controls
- **Disk Display Mode**: Percentage or absolute values

### Display Tab
- **Theme Selection**: Dark, Light, or Auto (System)
- **Show Tooltips**: Enable/disable hover information
- **Show Percentages**: Display percentage values
- **Show Values**: Display absolute values
- **Compact Mode**: Reduced spacing and size
- **Animation Speed**: UI transition timing (100-1000ms)

### Performance Tab
- **Update Animations**: Enable/disable monitor animations
- **Performance Information**: Current stats display
- **Settings Management**: Reset, Export, Import functions

## API Reference

### SettingsPanel Class

#### Constructor
```javascript
new SettingsPanel(systemMonitor)
```
- `systemMonitor`: Reference to SystemMonitor instance

#### Methods
```javascript
show()                     // Show settings panel
hide()                     // Hide settings panel  
toggle()                   // Toggle panel visibility
getSettings()              // Get current settings object
updateSetting(key, value)  // Update specific setting
resetToDefaults()          // Reset all settings
exportSettings()           // Export settings to JSON file
importSettings()           // Import settings from JSON file
```

#### Events
```javascript
// Listen for settings changes
document.addEventListener('settingsChanged', (event) => {
    console.log('Settings updated:', event.detail);
});

// Listen for monitor visibility changes
document.addEventListener('monitorVisibilityChanged', (event) => {
    console.log('Monitor visibility:', event.detail);
});
```

## Settings Storage

Settings are automatically saved to `localStorage` with the key `systemMonitor.settings`. The settings object structure:

```javascript
{
    refreshRate: 1000,           // Milliseconds
    enabledMonitors: {
        cpu: true,
        memory: true,
        disk: true,
        gpu: true,
        vram: true,
        temperature: true
    },
    enabledGPUs: {              // Per-GPU settings
        0: true,
        1: true
    },
    windowSize: {
        width: 300,
        height: 200
    },
    theme: 'dark',              // 'dark', 'light', 'auto'
    showTooltips: true,
    showPercentages: true,
    showValues: true,
    animationSpeed: 300,        // Milliseconds
    compactMode: false,
    autoReconnect: true,
    maxReconnectAttempts: 10,
    temperatureUnit: 'celsius', // 'celsius', 'fahrenheit'
    diskDisplayMode: 'percentage', // 'percentage', 'absolute'
    updateAnimation: true
}
```

## Usage Examples

### Basic Integration
```javascript
// Initialize with system monitor
const systemMonitor = new SystemMonitor();
const settingsPanel = new SettingsPanel(systemMonitor);

// Show settings panel
settingsPanel.show();
```

### Custom Event Handling
```javascript
// Listen for settings changes
document.addEventListener('settingsChanged', (event) => {
    const settings = event.detail;
    
    // Apply custom logic based on settings
    if (settings.compactMode) {
        document.body.classList.add('compact');
    }
});
```

### Programmatic Settings Updates
```javascript
// Update specific setting
settingsPanel.updateSetting('refreshRate', 2000);

// Get current settings
const currentSettings = settingsPanel.getSettings();
console.log('Current refresh rate:', currentSettings.refreshRate);
```

## Testing

Use `chrome-app/settings-test.html` to test the settings panel functionality:

1. Open the test page in a web browser
2. Click the settings button (⚙️) to open the panel
3. Test various controls and observe console output
4. Verify settings persistence across page reloads

## Performance Considerations

- **Debounced saves**: Settings are saved immediately but efficiently
- **Minimal DOM updates**: Only affected elements are updated
- **Memory management**: Event listeners are properly cleaned up
- **Animation optimization**: CSS transforms used for smooth animations

## Browser Compatibility

- Chrome 88+ (Primary target for Chrome app)
- Firefox 78+ (For testing)
- Safari 14+ (For testing)
- Edge 88+ (For testing)

## Future Enhancements

- **Color scheme customization**: Custom color pickers
- **Layout presets**: Predefined monitor arrangements
- **Export/Import profiles**: Named configuration sets
- **Keyboard shortcuts**: Quick access to common functions
- **Advanced filtering**: Show/hide specific data types
