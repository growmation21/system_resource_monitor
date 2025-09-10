/**
 * Settings Panel Implementation for System Resource Monitor
 * 
 * Provides comprehensive configuration interface including:
 * - Monitor enable/disable toggles
 * - Refresh rate configuration
 * - Monitor size configuration
 * - Per-GPU monitoring toggles
 * - Display preferences
 * - Performance settings
 */

class SettingsPanel {
    constructor(systemMonitor) {
        this.systemMonitor = systemMonitor;
        this.isVisible = false;
        this.settings = this.loadSettings();
        
        // Default settings
        this.defaultSettings = {
            refreshRate: 1000, // 1 second
            enabledMonitors: {
                cpu: true,
                memory: true,
                disk: true,
                gpu: true,
                vram: true,
                temperature: true
            },
            enabledGPUs: {}, // Will be populated based on detected GPUs
            windowSize: {
                width: 300,
                height: 200
            },
            theme: 'dark',
            showTooltips: true,
            showPercentages: true,
            showValues: true,
            animationSpeed: 300,
            compactMode: false,
            autoReconnect: true,
            maxReconnectAttempts: 10,
            temperatureUnit: 'celsius',
            diskDisplayMode: 'percentage', // 'percentage' or 'absolute'
            updateAnimation: true,
            
            // Task 6.2: Advanced Configuration Options
            selectedDiskDrives: ['C:'], // Default to C: drive on Windows
            colorScheme: {
                cpu: '#2196F3',
                memory: '#4CAF50',
                disk: '#FF9800',
                gpu: '#9C27B0',
                vram: '#E91E63',
                temperature: '#F44336',
                background: '#1a1a1a',
                text: '#ffffff',
                accent: '#0078d4'
            },
            customColors: false, // Use custom color scheme
            windowPosition: {
                x: 100,
                y: 100,
                remember: true
            },
            windowLayout: {
                columnsPerRow: 2,
                stackVertically: false,
                groupByType: true,
                showHeaders: true
            },
            performanceSettings: {
                enableVSync: true,
                reduceAnimations: false,
                backgroundThrottling: true,
                memoryOptimization: true,
                maxDataPoints: 100,
                enableProfiling: false
            },
            notifications: {
                enabled: true,
                cpuThreshold: 90,
                memoryThreshold: 85,
                temperatureThreshold: 80,
                soundEnabled: false
            }
        };
        
        this.init();
    }
    
    /**
     * Initialize settings panel
     */
    init() {
        this.createSettingsPanel();
        this.setupEventListeners();
        this.applySettings();
        
        // Listen for system monitor events
        document.addEventListener('systemMonitorReady', () => {
            this.updateGPUSettings();
        });
    }
    
    /**
     * Load settings from localStorage
     */
    loadSettings() {
        try {
            const saved = localStorage.getItem('systemMonitor.settings');
            if (saved) {
                const parsed = JSON.parse(saved);
                return { ...this.defaultSettings, ...parsed };
            }
        } catch (e) {
            console.warn('Failed to load settings:', e);
        }
        return { ...this.defaultSettings };
    }
    
    /**
     * Save settings to localStorage
     */
    saveSettings() {
        try {
            localStorage.setItem('systemMonitor.settings', JSON.stringify(this.settings));
            this.applySettings();
        } catch (e) {
            console.warn('Failed to save settings:', e);
        }
    }
    
    /**
     * Apply current settings to the system monitor
     */
    applySettings() {
        if (!this.systemMonitor) return;
        
        // Apply refresh rate
        if (this.systemMonitor.setRefreshRate) {
            this.systemMonitor.setRefreshRate(this.settings.refreshRate);
        }
        
        // Apply enabled monitors
        this.updateMonitorVisibility();
        
        // Apply theme
        this.applyTheme();
        
        // Apply display preferences
        this.applyDisplayPreferences();
        
        // Trigger settings changed event
        document.dispatchEvent(new CustomEvent('settingsChanged', {
            detail: this.settings
        }));
    }
    
    /**
     * Create the settings panel UI
     */
    createSettingsPanel() {
        const panel = document.createElement('div');
        panel.id = 'settings-panel';
        panel.className = 'settings-panel';
        panel.innerHTML = `
            <div class="settings-header">
                <h3>System Monitor Settings</h3>
                <button id="settings-close" class="close-button">×</button>
            </div>
            
            <div class="settings-content">
                <div class="settings-tabs">
                    <button class="tab-button active" data-tab="general">General</button>
                    <button class="tab-button" data-tab="monitors">Monitors</button>
                    <button class="tab-button" data-tab="display">Display</button>
                    <button class="tab-button" data-tab="advanced">Advanced</button>
                    <button class="tab-button" data-tab="performance">Performance</button>
                    <button class="tab-button" data-tab="notifications">Alerts</button>
                </div>
                
                <div class="settings-tab-content">
                    <!-- General Settings Tab -->
                    <div id="general-tab" class="tab-pane active">
                        <div class="setting-group">
                            <label>Refresh Rate:</label>
                            <div class="setting-control">
                                <input type="range" id="refresh-rate" min="100" max="30000" step="100" value="1000">
                                <span id="refresh-rate-value">1.0s</span>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Window Size:</label>
                            <div class="setting-control">
                                <input type="number" id="window-width" min="200" max="800" value="300" placeholder="Width">
                                <span>×</span>
                                <input type="number" id="window-height" min="150" max="600" value="200" placeholder="Height">
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Auto Reconnect:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="auto-reconnect" checked>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Temperature Unit:</label>
                            <div class="setting-control">
                                <select id="temperature-unit">
                                    <option value="celsius">Celsius (°C)</option>
                                    <option value="fahrenheit">Fahrenheit (°F)</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Monitor Settings Tab -->
                    <div id="monitors-tab" class="tab-pane">
                        <div class="setting-group">
                            <label>Hardware Monitors:</label>
                            <div class="monitor-toggles">
                                <div class="monitor-toggle">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-cpu" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>CPU Usage</span>
                                </div>
                                
                                <div class="monitor-toggle">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-memory" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Memory (RAM)</span>
                                </div>
                                
                                <div class="monitor-toggle">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-disk" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Disk Usage</span>
                                </div>
                                
                                <div class="monitor-toggle">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-gpu" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>GPU Usage</span>
                                </div>
                                
                                <div class="monitor-toggle">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-vram" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>VRAM Usage</span>
                                </div>
                                
                                <div class="monitor-toggle">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-temperature" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>GPU Temperature</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>GPU Monitors:</label>
                            <div id="gpu-toggles" class="gpu-toggles">
                                <!-- GPU-specific toggles will be populated here -->
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Disk Display Mode:</label>
                            <div class="setting-control">
                                <select id="disk-display-mode">
                                    <option value="percentage">Percentage</option>
                                    <option value="absolute">Absolute (GB)</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Display Settings Tab -->
                    <div id="display-tab" class="tab-pane">
                        <div class="setting-group">
                            <label>Theme:</label>
                            <div class="setting-control">
                                <select id="theme-select">
                                    <option value="dark">Dark Theme</option>
                                    <option value="light">Light Theme</option>
                                    <option value="auto">Auto (System)</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Show Tooltips:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="show-tooltips" checked>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Show Percentages:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="show-percentages" checked>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Show Values:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="show-values" checked>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Compact Mode:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="compact-mode">
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Animation Speed:</label>
                            <div class="setting-control">
                                <input type="range" id="animation-speed" min="100" max="1000" step="50" value="300">
                                <span id="animation-speed-value">300ms</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Performance Settings Tab -->
                    <div id="performance-tab" class="tab-pane">
                        <div class="setting-group">
                            <label>Update Animations:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="update-animation" checked>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Max Reconnect Attempts:</label>
                            <div class="setting-control">
                                <input type="number" id="max-reconnect" min="1" max="50" value="10">
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Performance Info:</label>
                            <div class="performance-info">
                                <div>Update Rate: <span id="current-update-rate">--</span></div>
                                <div>Connected: <span id="connection-status">--</span></div>
                                <div>Data Points: <span id="data-points">--</span></div>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <div class="setting-actions">
                                <button id="reset-settings" class="action-button">Reset to Defaults</button>
                                <button id="export-settings" class="action-button">Export Settings</button>
                                <button id="import-settings" class="action-button">Import Settings</button>
                            </div>
                    </div>
                    
                    <!-- Advanced Configuration Tab -->
                    <div id="advanced-tab" class="tab-pane">
                        <div class="setting-group">
                            <label>Disk Drive Selection:</label>
                            <div class="setting-control">
                                <select id="disk-drives" multiple size="4">
                                    <option value="C:">C: Drive (System)</option>
                                    <option value="D:">D: Drive</option>
                                    <option value="E:">E: Drive</option>
                                    <option value="F:">F: Drive</option>
                                </select>
                                <button id="refresh-drives" class="action-button">Refresh Drives</button>
                            </div>
                            <small>Hold Ctrl to select multiple drives</small>
                        </div>
                        
                        <div class="setting-group">
                            <label>Color Scheme:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="custom-colors">
                                    <span class="slider"></span>
                                </label>
                                <span>Use Custom Colors</span>
                            </div>
                        </div>
                        
                        <div id="color-customization" class="color-scheme-panel" style="display: none;">
                            <div class="color-grid">
                                <div class="color-setting">
                                    <label>CPU Color:</label>
                                    <input type="color" id="color-cpu" value="#2196F3">
                                </div>
                                <div class="color-setting">
                                    <label>Memory Color:</label>
                                    <input type="color" id="color-memory" value="#4CAF50">
                                </div>
                                <div class="color-setting">
                                    <label>Disk Color:</label>
                                    <input type="color" id="color-disk" value="#FF9800">
                                </div>
                                <div class="color-setting">
                                    <label>GPU Color:</label>
                                    <input type="color" id="color-gpu" value="#9C27B0">
                                </div>
                                <div class="color-setting">
                                    <label>VRAM Color:</label>
                                    <input type="color" id="color-vram" value="#E91E63">
                                </div>
                                <div class="color-setting">
                                    <label>Temperature Color:</label>
                                    <input type="color" id="color-temperature" value="#F44336">
                                </div>
                            </div>
                            <div class="color-presets">
                                <button class="action-button" onclick="settingsPanel.applyColorPreset('default')">Default</button>
                                <button class="action-button" onclick="settingsPanel.applyColorPreset('cool')">Cool</button>
                                <button class="action-button" onclick="settingsPanel.applyColorPreset('warm')">Warm</button>
                                <button class="action-button" onclick="settingsPanel.applyColorPreset('monochrome')">Mono</button>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Window Position:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="remember-position" checked>
                                    <span class="slider"></span>
                                </label>
                                <span>Remember Window Position</span>
                            </div>
                            <div class="position-controls">
                                <input type="number" id="window-x" placeholder="X" value="100" min="0">
                                <span>×</span>
                                <input type="number" id="window-y" placeholder="Y" value="100" min="0">
                                <button id="center-window" class="action-button">Center</button>
                                <button id="reset-position" class="action-button">Reset</button>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Layout Options:</label>
                            <div class="layout-options">
                                <div class="setting-control">
                                    <label>Columns per Row:</label>
                                    <input type="range" id="columns-per-row" min="1" max="4" value="2" step="1">
                                    <span id="columns-value">2</span>
                                </div>
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="stack-vertically">
                                        <span class="slider"></span>
                                    </label>
                                    <span>Stack Vertically</span>
                                </div>
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="group-by-type" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Group by Type</span>
                                </div>
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="show-headers" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Show Section Headers</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Enhanced Performance Settings Tab -->
                    <div id="performance-tab" class="tab-pane">
                        <div class="setting-group">
                            <label>Rendering Options:</label>
                            <div class="performance-toggles">
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="enable-vsync" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Enable VSync</span>
                                </div>
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="reduce-animations">
                                        <span class="slider"></span>
                                    </label>
                                    <span>Reduce Animations</span>
                                </div>
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="update-animation" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Update Animations</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Memory Management:</label>
                            <div class="performance-toggles">
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="background-throttling" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Background Throttling</span>
                                </div>
                                <div class="setting-control">
                                    <label class="switch">
                                        <input type="checkbox" id="memory-optimization" checked>
                                        <span class="slider"></span>
                                    </label>
                                    <span>Memory Optimization</span>
                                </div>
                                <div class="setting-control">
                                    <label>Max Data Points:</label>
                                    <input type="number" id="max-data-points" min="10" max="1000" value="100">
                                </div>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Connection Settings:</label>
                            <div class="setting-control">
                                <label>Max Reconnect Attempts:</label>
                                <input type="number" id="max-reconnect" min="1" max="50" value="10">
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Debug Options:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="enable-profiling">
                                    <span class="slider"></span>
                                </label>
                                <span>Enable Performance Profiling</span>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Performance Info:</label>
                            <div class="performance-info">
                                <div>Update Rate: <span id="current-update-rate">--</span></div>
                                <div>Connected: <span id="connection-status">--</span></div>
                                <div>Data Points: <span id="data-points">--</span></div>
                                <div>Memory Usage: <span id="memory-usage">--</span></div>
                                <div>FPS: <span id="current-fps">--</span></div>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <div class="setting-actions">
                                <button id="reset-settings" class="action-button">Reset to Defaults</button>
                                <button id="export-settings" class="action-button">Export Settings</button>
                                <button id="import-settings" class="action-button">Import Settings</button>
                                <button id="clear-cache" class="action-button">Clear Cache</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Notifications/Alerts Tab -->
                    <div id="notifications-tab" class="tab-pane">
                        <div class="setting-group">
                            <label>Alert System:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="notifications-enabled" checked>
                                    <span class="slider"></span>
                                </label>
                                <span>Enable Notifications</span>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Threshold Alerts:</label>
                            <div class="threshold-controls">
                                <div class="threshold-setting">
                                    <label>CPU Threshold:</label>
                                    <div class="setting-control">
                                        <input type="range" id="cpu-threshold" min="50" max="100" value="90" step="5">
                                        <span id="cpu-threshold-value">90%</span>
                                    </div>
                                </div>
                                <div class="threshold-setting">
                                    <label>Memory Threshold:</label>
                                    <div class="setting-control">
                                        <input type="range" id="memory-threshold" min="50" max="100" value="85" step="5">
                                        <span id="memory-threshold-value">85%</span>
                                    </div>
                                </div>
                                <div class="threshold-setting">
                                    <label>Temperature Threshold:</label>
                                    <div class="setting-control">
                                        <input type="range" id="temperature-threshold" min="60" max="100" value="80" step="5">
                                        <span id="temperature-threshold-value">80°C</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Notification Options:</label>
                            <div class="setting-control">
                                <label class="switch">
                                    <input type="checkbox" id="sound-enabled">
                                    <span class="slider"></span>
                                </label>
                                <span>Enable Sound Alerts</span>
                            </div>
                        </div>
                        
                        <div class="setting-group">
                            <label>Test Notifications:</label>
                            <div class="setting-actions">
                                <button id="test-cpu-alert" class="action-button">Test CPU Alert</button>
                                <button id="test-memory-alert" class="action-button">Test Memory Alert</button>
                                <button id="test-temp-alert" class="action-button">Test Temperature Alert</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        this.addSettingsStyles();
    }
    
    /**
     * Add CSS styles for the settings panel
     */
    addSettingsStyles() {
        if (document.getElementById('settings-panel-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'settings-panel-styles';
        styles.textContent = `
            :root {
                --bg-color: #1a1a1a;
                --text-color: #ffffff;
                --border-color: #555555;
                --animation-speed: 300ms;
            }
            
            .settings-panel {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 500px;
                max-height: 70vh;
                background: #2d2d2d;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 13px;
                color: var(--text-color);
                z-index: 1000;
                display: none;
                overflow: hidden;
                animation: fadeIn var(--animation-speed) ease-out;
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(0.9);
                }
                to {
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1);
                }
            }
            
            .settings-panel.visible {
                display: block;
            }
            
            .settings-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: #3a3a3a;
                border-bottom: 1px solid var(--border-color);
            }
            
            .settings-header h3 {
                margin: 0;
                font-size: 16px;
                color: var(--text-color);
            }
            
            .close-button {
                background: none;
                border: none;
                color: #ccc;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 3px;
                transition: all 0.2s;
            }
            
            .close-button:hover {
                background: #555;
                color: var(--text-color);
            }
            
            .settings-content {
                max-height: calc(70vh - 60px);
                overflow-y: auto;
                scrollbar-width: thin;
                scrollbar-color: #666 #2d2d2d;
            }
            
            .settings-content::-webkit-scrollbar {
                width: 8px;
            }
            
            .settings-content::-webkit-scrollbar-track {
                background: #2d2d2d;
            }
            
            .settings-content::-webkit-scrollbar-thumb {
                background: #666;
                border-radius: 4px;
            }
            
            .settings-content::-webkit-scrollbar-thumb:hover {
                background: #888;
            }
            
            .settings-tabs {
                display: flex;
                background: #3a3a3a;
                border-bottom: 1px solid var(--border-color);
            }
            
            .tab-button {
                flex: 1;
                padding: 12px 8px;
                background: none;
                border: none;
                color: #ccc;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
                border-bottom: 2px solid transparent;
                text-align: center;
            }
            
            .tab-button:hover {
                background: #444;
                color: var(--text-color);
            }
            
            .tab-button.active {
                color: var(--text-color);
                background: #2d2d2d;
                border-bottom-color: #0078d4;
            }
            
            .tab-pane {
                display: none;
                padding: 20px;
                animation: slideIn var(--animation-speed) ease-out;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .tab-pane.active {
                display: block;
            }
            
            .setting-group {
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid #404040;
            }
            
            .setting-group:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }
            
            .setting-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #ddd;
                font-size: 13px;
            }
            
            .setting-control {
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .setting-control input[type="number"],
            .setting-control input[type="text"],
            .setting-control select {
                background: #404040;
                border: 1px solid #666;
                border-radius: 4px;
                color: var(--text-color);
                padding: 6px 10px;
                font-size: 12px;
                min-width: 80px;
                transition: all 0.2s;
            }
            
            .setting-control input[type="number"]:focus,
            .setting-control input[type="text"]:focus,
            .setting-control select:focus {
                outline: none;
                border-color: #0078d4;
                box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.3);
            }
            
            .setting-control input[type="range"] {
                flex: 1;
                margin-right: 10px;
                min-width: 150px;
                height: 6px;
                background: #404040;
                border-radius: 3px;
                outline: none;
                -webkit-appearance: none;
            }
            
            .setting-control input[type="range"]::-webkit-slider-thumb {
                -webkit-appearance: none;
                width: 16px;
                height: 16px;
                background: #0078d4;
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .setting-control input[type="range"]::-webkit-slider-thumb:hover {
                background: #106ebe;
                transform: scale(1.1);
            }
            
            .setting-control input[type="range"]::-moz-range-thumb {
                width: 16px;
                height: 16px;
                background: #0078d4;
                border-radius: 50%;
                cursor: pointer;
                border: none;
                transition: all 0.2s;
            }
            
            .setting-control input[type="range"]::-moz-range-thumb:hover {
                background: #106ebe;
                transform: scale(1.1);
            }
            
            .setting-control span {
                color: #ccc;
                font-size: 12px;
                min-width: 40px;
                white-space: nowrap;
            }
            
            .switch {
                position: relative;
                display: inline-block;
                width: 44px;
                height: 24px;
                margin-right: 8px;
            }
            
            .switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            
            .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #666;
                transition: 0.3s;
                border-radius: 24px;
            }
            
            .slider:before {
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: 0.3s;
                border-radius: 50%;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            
            input:checked + .slider {
                background-color: #0078d4;
            }
            
            input:checked + .slider:before {
                transform: translateX(20px);
            }
            
            .slider:hover {
                box-shadow: 0 0 0 4px rgba(0, 120, 212, 0.1);
            }
            
            .monitor-toggles,
            .gpu-toggles {
                display: flex;
                flex-direction: column;
                gap: 8px;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .monitor-toggle,
            .gpu-toggle {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 10px 12px;
                background: #3a3a3a;
                border-radius: 6px;
                border: 1px solid #4a4a4a;
                transition: all 0.2s;
            }
            
            .monitor-toggle:hover,
            .gpu-toggle:hover {
                background: #444;
                border-color: #0078d4;
            }
            
            .monitor-toggle span,
            .gpu-toggle span {
                color: #ddd;
                font-size: 12px;
                flex: 1;
            }
            
            .performance-info {
                background: #3a3a3a;
                padding: 15px;
                border-radius: 6px;
                font-size: 12px;
                border: 1px solid #4a4a4a;
            }
            
            .performance-info div {
                margin: 6px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .performance-info span {
                color: #0078d4;
                font-weight: 500;
                font-family: monospace;
            }
            
            .setting-actions {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
                justify-content: center;
                margin-top: 15px;
            }
            
            .action-button {
                background: linear-gradient(135deg, #0078d4, #106ebe);
                border: none;
                border-radius: 6px;
                color: #fff;
                padding: 10px 16px;
                cursor: pointer;
                font-size: 11px;
                font-weight: 500;
                transition: all 0.2s;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            
            .action-button:hover {
                background: linear-gradient(135deg, #106ebe, #0078d4);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }
            
            .action-button:active {
                transform: translateY(0);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            
            /* Responsive adjustments */
            @media (max-width: 600px) {
                .settings-panel {
                    width: 90%;
                    max-width: 450px;
                }
                
                .settings-tabs {
                    flex-wrap: wrap;
                }
                
                .tab-button {
                    min-width: 0;
                    flex: 1 1 auto;
                }
            }
            
            /* Light theme overrides */
            .light-theme {
                --bg-color: #ffffff;
                --text-color: #000000;
                --border-color: #cccccc;
            }
            
            .light-theme .settings-panel {
                background: #ffffff;
                color: #000000;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            }
            
            .light-theme .settings-header {
                background: #f5f5f5;
                border-bottom-color: #cccccc;
            }
            
            .light-theme .settings-tabs {
                background: #f5f5f5;
            }
            
            .light-theme .tab-button {
                color: #666;
            }
            
            .light-theme .tab-button:hover {
                background: #e0e0e0;
                color: #000;
            }
            
            .light-theme .tab-button.active {
                background: #ffffff;
                color: #000;
            }
            
            .light-theme .setting-control input,
            .light-theme .setting-control select {
                background: #f5f5f5;
                border-color: #cccccc;
                color: #000;
            }
            
            .light-theme .monitor-toggle,
            .light-theme .gpu-toggle {
                background: #f5f5f5;
                border-color: #cccccc;
            }
            
            .light-theme .performance-info {
                background: #f5f5f5;
                border-color: #cccccc;
            }
            
            /* Advanced Configuration Styles */
            .color-scheme-panel {
                margin-top: 15px;
                padding: 15px;
                background: #3a3a3a;
                border-radius: 6px;
                border: 1px solid #4a4a4a;
            }
            
            .color-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                margin-bottom: 15px;
            }
            
            .color-setting {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 5px;
            }
            
            .color-setting label {
                font-size: 11px;
                color: #ccc;
                margin: 0;
            }
            
            .color-setting input[type="color"] {
                width: 40px;
                height: 40px;
                border: 2px solid #666;
                border-radius: 8px;
                cursor: pointer;
                background: none;
                transition: all 0.2s;
            }
            
            .color-setting input[type="color"]:hover {
                border-color: #0078d4;
                transform: scale(1.05);
            }
            
            .color-presets {
                display: flex;
                gap: 8px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .position-controls {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 10px;
                flex-wrap: wrap;
            }
            
            .position-controls input[type="number"] {
                width: 70px;
            }
            
            .layout-options {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .performance-toggles {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .threshold-controls {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .threshold-setting {
                background: #3a3a3a;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #4a4a4a;
            }
            
            .threshold-setting label {
                display: block;
                margin-bottom: 8px;
                font-size: 12px;
                color: #ddd;
            }
            
            #disk-drives {
                background: #404040;
                border: 1px solid #666;
                border-radius: 4px;
                color: var(--text-color);
                padding: 8px;
                font-size: 12px;
                min-width: 200px;
                max-width: 300px;
            }
            
            #disk-drives option {
                padding: 4px 8px;
                background: #404040;
                color: var(--text-color);
            }
            
            #disk-drives option:checked {
                background: #0078d4;
                color: #fff;
            }
            
            #disk-drives:focus {
                outline: none;
                border-color: #0078d4;
                box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.3);
            }
            
            /* Responsive adjustments for new tabs */
            @media (max-width: 600px) {
                .color-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .position-controls,
                .layout-options .setting-control {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .threshold-controls {
                    gap: 10px;
                }
            }
            
            /* Enhanced light theme support */
            .light-theme .color-scheme-panel,
            .light-theme .threshold-setting {
                background: #f5f5f5;
                border-color: #cccccc;
            }
            
            .light-theme .color-setting input[type="color"] {
                border-color: #cccccc;
            }
            
            .light-theme #disk-drives {
                background: #ffffff;
                border-color: #cccccc;
                color: #000;
            }
            
            .light-theme #disk-drives option {
                background: #ffffff;
                color: #000;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * Setup event listeners for settings panel
     */
    setupEventListeners() {
        // Settings toggle button
        document.getElementById('settings-toggle').addEventListener('click', () => {
            this.toggle();
        });
        
        // Close button
        document.getElementById('settings-close').addEventListener('click', () => {
            this.hide();
        });
        
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
            });
        });
        
        // Setting controls
        this.setupSettingControls();
        
        // Window click outside to close
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('settings-panel');
            const toggle = document.getElementById('settings-toggle');
            
            if (this.isVisible && 
                !panel.contains(e.target) && 
                !toggle.contains(e.target)) {
                this.hide();
            }
        });
    }
    
    /**
     * Setup individual setting controls
     */
    setupSettingControls() {
        // Refresh rate
        const refreshRate = document.getElementById('refresh-rate');
        const refreshRateValue = document.getElementById('refresh-rate-value');
        
        refreshRate.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            refreshRateValue.textContent = value >= 1000 ? 
                `${(value / 1000).toFixed(1)}s` : `${value}ms`;
            this.settings.refreshRate = value;
            this.saveSettings();
        });
        
        // Window size
        document.getElementById('window-width').addEventListener('change', (e) => {
            this.settings.windowSize.width = parseInt(e.target.value);
            this.saveSettings();
        });
        
        document.getElementById('window-height').addEventListener('change', (e) => {
            this.settings.windowSize.height = parseInt(e.target.value);
            this.saveSettings();
        });
        
        // Monitor toggles
        const monitorTypes = ['cpu', 'memory', 'disk', 'gpu', 'vram', 'temperature'];
        monitorTypes.forEach(type => {
            const checkbox = document.getElementById(`enable-${type}`);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    this.settings.enabledMonitors[type] = e.target.checked;
                    this.saveSettings();
                });
            }
        });
        
        // Other settings
        this.setupOtherControls();
        
        // Load current values
        this.loadCurrentValues();
    }
    
    /**
     * Setup other control event listeners
     */
    setupOtherControls() {
        // Auto reconnect
        document.getElementById('auto-reconnect').addEventListener('change', (e) => {
            this.settings.autoReconnect = e.target.checked;
            this.saveSettings();
        });
        
        // Temperature unit
        document.getElementById('temperature-unit').addEventListener('change', (e) => {
            this.settings.temperatureUnit = e.target.value;
            this.saveSettings();
        });
        
        // Disk display mode
        document.getElementById('disk-display-mode').addEventListener('change', (e) => {
            this.settings.diskDisplayMode = e.target.value;
            this.saveSettings();
        });
        
        // Theme
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.settings.theme = e.target.value;
            this.saveSettings();
        });
        
        // Display preferences
        const displayToggles = [
            { id: 'show-tooltips', setting: 'showTooltips' },
            { id: 'show-percentages', setting: 'showPercentages' },
            { id: 'show-values', setting: 'showValues' },
            { id: 'compact-mode', setting: 'compactMode' },
            { id: 'update-animation', setting: 'updateAnimation' }
        ];
        
        displayToggles.forEach(({ id, setting }) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    this.settings[setting] = e.target.checked;
                    this.saveSettings();
                });
            }
        });
        
        // Animation speed
        const animationSpeed = document.getElementById('animation-speed');
        const animationSpeedValue = document.getElementById('animation-speed-value');
        
        animationSpeed.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            animationSpeedValue.textContent = `${value}ms`;
            this.settings.animationSpeed = value;
            this.saveSettings();
        });
        
        // Max reconnect attempts
        document.getElementById('max-reconnect').addEventListener('change', (e) => {
            this.settings.maxReconnectAttempts = parseInt(e.target.value);
            this.saveSettings();
        });
        
        // Action buttons
        document.getElementById('reset-settings').addEventListener('click', () => {
            this.resetToDefaults();
        });
        
        document.getElementById('export-settings').addEventListener('click', () => {
            this.exportSettings();
        });
        
        document.getElementById('import-settings').addEventListener('click', () => {
            this.importSettings();
        });
        
        // Task 6.2: Advanced Configuration Event Handlers
        this.setupAdvancedConfigurationControls();
    }
    
    /**
     * Setup advanced configuration controls (Task 6.2)
     */
    setupAdvancedConfigurationControls() {
        // Disk drive selection
        const diskDrives = document.getElementById('disk-drives');
        if (diskDrives) {
            diskDrives.addEventListener('change', (e) => {
                const selected = Array.from(e.target.selectedOptions).map(option => option.value);
                this.settings.selectedDiskDrives = selected;
                this.saveSettings();
            });
        }
        
        // Refresh drives button
        document.getElementById('refresh-drives')?.addEventListener('click', () => {
            this.refreshAvailableDrives();
        });
        
        // Custom colors toggle
        document.getElementById('custom-colors')?.addEventListener('change', (e) => {
            this.settings.customColors = e.target.checked;
            document.getElementById('color-customization').style.display = 
                e.target.checked ? 'block' : 'none';
            this.saveSettings();
        });
        
        // Color pickers
        const colorInputs = ['cpu', 'memory', 'disk', 'gpu', 'vram', 'temperature'];
        colorInputs.forEach(type => {
            const colorInput = document.getElementById(`color-${type}`);
            if (colorInput) {
                colorInput.addEventListener('change', (e) => {
                    this.settings.colorScheme[type] = e.target.value;
                    this.saveSettings();
                    this.applyColorScheme();
                });
            }
        });
        
        // Window position controls
        document.getElementById('remember-position')?.addEventListener('change', (e) => {
            this.settings.windowPosition.remember = e.target.checked;
            this.saveSettings();
        });
        
        document.getElementById('window-x')?.addEventListener('change', (e) => {
            this.settings.windowPosition.x = parseInt(e.target.value);
            this.saveSettings();
        });
        
        document.getElementById('window-y')?.addEventListener('change', (e) => {
            this.settings.windowPosition.y = parseInt(e.target.value);
            this.saveSettings();
        });
        
        document.getElementById('center-window')?.addEventListener('click', () => {
            this.centerWindow();
        });
        
        document.getElementById('reset-position')?.addEventListener('click', () => {
            this.resetWindowPosition();
        });
        
        // Layout options
        const columnsSlider = document.getElementById('columns-per-row');
        const columnsValue = document.getElementById('columns-value');
        if (columnsSlider && columnsValue) {
            columnsSlider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                columnsValue.textContent = value;
                this.settings.windowLayout.columnsPerRow = value;
                this.saveSettings();
                this.applyLayout();
            });
        }
        
        const layoutToggles = [
            { id: 'stack-vertically', setting: 'stackVertically' },
            { id: 'group-by-type', setting: 'groupByType' },
            { id: 'show-headers', setting: 'showHeaders' }
        ];
        
        layoutToggles.forEach(({ id, setting }) => {
            document.getElementById(id)?.addEventListener('change', (e) => {
                this.settings.windowLayout[setting] = e.target.checked;
                this.saveSettings();
                this.applyLayout();
            });
        });
        
        // Performance settings
        const performanceToggles = [
            { id: 'enable-vsync', setting: 'enableVSync' },
            { id: 'reduce-animations', setting: 'reduceAnimations' },
            { id: 'background-throttling', setting: 'backgroundThrottling' },
            { id: 'memory-optimization', setting: 'memoryOptimization' },
            { id: 'enable-profiling', setting: 'enableProfiling' }
        ];
        
        performanceToggles.forEach(({ id, setting }) => {
            document.getElementById(id)?.addEventListener('change', (e) => {
                this.settings.performanceSettings[setting] = e.target.checked;
                this.saveSettings();
                this.applyPerformanceSettings();
            });
        });
        
        document.getElementById('max-data-points')?.addEventListener('change', (e) => {
            this.settings.performanceSettings.maxDataPoints = parseInt(e.target.value);
            this.saveSettings();
        });
        
        // Notification settings
        document.getElementById('notifications-enabled')?.addEventListener('change', (e) => {
            this.settings.notifications.enabled = e.target.checked;
            this.saveSettings();
        });
        
        // Threshold sliders
        const thresholds = [
            { id: 'cpu-threshold', setting: 'cpuThreshold', unit: '%' },
            { id: 'memory-threshold', setting: 'memoryThreshold', unit: '%' },
            { id: 'temperature-threshold', setting: 'temperatureThreshold', unit: '°C' }
        ];
        
        thresholds.forEach(({ id, setting, unit }) => {
            const slider = document.getElementById(id);
            const valueSpan = document.getElementById(`${id}-value`);
            
            if (slider && valueSpan) {
                slider.addEventListener('input', (e) => {
                    const value = parseInt(e.target.value);
                    valueSpan.textContent = `${value}${unit}`;
                    this.settings.notifications[setting] = value;
                    this.saveSettings();
                });
            }
        });
        
        document.getElementById('sound-enabled')?.addEventListener('change', (e) => {
            this.settings.notifications.soundEnabled = e.target.checked;
            this.saveSettings();
        });
        
        // Test notification buttons
        document.getElementById('test-cpu-alert')?.addEventListener('click', () => {
            this.testNotification('CPU usage is high!', 'cpu');
        });
        
        document.getElementById('test-memory-alert')?.addEventListener('click', () => {
            this.testNotification('Memory usage is high!', 'memory');
        });
        
        document.getElementById('test-temp-alert')?.addEventListener('click', () => {
            this.testNotification('GPU temperature is high!', 'temperature');
        });
        
        // Additional action buttons
        document.getElementById('clear-cache')?.addEventListener('click', () => {
            this.clearCache();
        });
    }
    
    /**
     * Load current values into form controls
     */
    loadCurrentValues() {
        // Refresh rate
        document.getElementById('refresh-rate').value = this.settings.refreshRate;
        document.getElementById('refresh-rate-value').textContent = 
            this.settings.refreshRate >= 1000 ? 
            `${(this.settings.refreshRate / 1000).toFixed(1)}s` : 
            `${this.settings.refreshRate}ms`;
        
        // Window size
        document.getElementById('window-width').value = this.settings.windowSize.width;
        document.getElementById('window-height').value = this.settings.windowSize.height;
        
        // Monitor toggles
        Object.keys(this.settings.enabledMonitors).forEach(type => {
            const checkbox = document.getElementById(`enable-${type}`);
            if (checkbox) {
                checkbox.checked = this.settings.enabledMonitors[type];
            }
        });
        
        // Other settings
        document.getElementById('auto-reconnect').checked = this.settings.autoReconnect;
        document.getElementById('temperature-unit').value = this.settings.temperatureUnit;
        document.getElementById('disk-display-mode').value = this.settings.diskDisplayMode;
        document.getElementById('theme-select').value = this.settings.theme;
        
        // Display preferences
        document.getElementById('show-tooltips').checked = this.settings.showTooltips;
        document.getElementById('show-percentages').checked = this.settings.showPercentages;
        document.getElementById('show-values').checked = this.settings.showValues;
        document.getElementById('compact-mode').checked = this.settings.compactMode;
        document.getElementById('update-animation').checked = this.settings.updateAnimation;
        
        // Animation speed
        document.getElementById('animation-speed').value = this.settings.animationSpeed;
        document.getElementById('animation-speed-value').textContent = `${this.settings.animationSpeed}ms`;
        
        // Max reconnect
        document.getElementById('max-reconnect').value = this.settings.maxReconnectAttempts;
        
        // Task 6.2: Load advanced configuration values
        this.loadAdvancedConfigurationValues();
    }
    
    /**
     * Load advanced configuration values (Task 6.2)
     */
    loadAdvancedConfigurationValues() {
        // Disk drives
        this.refreshAvailableDrives();
        
        // Custom colors
        const customColorsToggle = document.getElementById('custom-colors');
        if (customColorsToggle) {
            customColorsToggle.checked = this.settings.customColors;
            document.getElementById('color-customization').style.display = 
                this.settings.customColors ? 'block' : 'none';
        }
        
        // Load color values
        this.loadColorValues();
        
        // Window position
        document.getElementById('remember-position').checked = this.settings.windowPosition.remember;
        document.getElementById('window-x').value = this.settings.windowPosition.x;
        document.getElementById('window-y').value = this.settings.windowPosition.y;
        
        // Layout options
        const columnsSlider = document.getElementById('columns-per-row');
        const columnsValue = document.getElementById('columns-value');
        if (columnsSlider && columnsValue) {
            columnsSlider.value = this.settings.windowLayout.columnsPerRow;
            columnsValue.textContent = this.settings.windowLayout.columnsPerRow;
        }
        
        document.getElementById('stack-vertically').checked = this.settings.windowLayout.stackVertically;
        document.getElementById('group-by-type').checked = this.settings.windowLayout.groupByType;
        document.getElementById('show-headers').checked = this.settings.windowLayout.showHeaders;
        
        // Performance settings
        document.getElementById('enable-vsync').checked = this.settings.performanceSettings.enableVSync;
        document.getElementById('reduce-animations').checked = this.settings.performanceSettings.reduceAnimations;
        document.getElementById('background-throttling').checked = this.settings.performanceSettings.backgroundThrottling;
        document.getElementById('memory-optimization').checked = this.settings.performanceSettings.memoryOptimization;
        document.getElementById('enable-profiling').checked = this.settings.performanceSettings.enableProfiling;
        document.getElementById('max-data-points').value = this.settings.performanceSettings.maxDataPoints;
        
        // Notification settings
        document.getElementById('notifications-enabled').checked = this.settings.notifications.enabled;
        document.getElementById('sound-enabled').checked = this.settings.notifications.soundEnabled;
        
        // Threshold values
        const cpuThreshold = document.getElementById('cpu-threshold');
        const cpuThresholdValue = document.getElementById('cpu-threshold-value');
        if (cpuThreshold && cpuThresholdValue) {
            cpuThreshold.value = this.settings.notifications.cpuThreshold;
            cpuThresholdValue.textContent = `${this.settings.notifications.cpuThreshold}%`;
        }
        
        const memoryThreshold = document.getElementById('memory-threshold');
        const memoryThresholdValue = document.getElementById('memory-threshold-value');
        if (memoryThreshold && memoryThresholdValue) {
            memoryThreshold.value = this.settings.notifications.memoryThreshold;
            memoryThresholdValue.textContent = `${this.settings.notifications.memoryThreshold}%`;
        }
        
        const tempThreshold = document.getElementById('temperature-threshold');
        const tempThresholdValue = document.getElementById('temperature-threshold-value');
        if (tempThreshold && tempThresholdValue) {
            tempThreshold.value = this.settings.notifications.temperatureThreshold;
            tempThresholdValue.textContent = `${this.settings.notifications.temperatureThreshold}°C`;
        }
    }
    
    /**
     * Update GPU-specific settings based on detected GPUs
     */
    updateGPUSettings() {
        const gpuToggles = document.getElementById('gpu-toggles');
        if (!gpuToggles) return;
        
        // Clear existing GPU toggles
        gpuToggles.innerHTML = '';
        
        // Get GPU information from system monitor
        if (this.systemMonitor && this.systemMonitor.lastData && this.systemMonitor.lastData.gpu) {
            const gpuData = this.systemMonitor.lastData.gpu;
            
            if (Array.isArray(gpuData)) {
                gpuData.forEach((gpu, index) => {
                    const gpuToggle = document.createElement('div');
                    gpuToggle.className = 'gpu-toggle';
                    gpuToggle.innerHTML = `
                        <label class="switch">
                            <input type="checkbox" id="enable-gpu-${index}" checked>
                            <span class="slider"></span>
                        </label>
                        <span>GPU ${index}: ${gpu.name || 'Unknown'}</span>
                    `;
                    
                    gpuToggles.appendChild(gpuToggle);
                    
                    // Setup event listener
                    const checkbox = gpuToggle.querySelector('input');
                    checkbox.addEventListener('change', (e) => {
                        if (!this.settings.enabledGPUs) {
                            this.settings.enabledGPUs = {};
                        }
                        this.settings.enabledGPUs[index] = e.target.checked;
                        this.saveSettings();
                    });
                    
                    // Load saved state
                    if (this.settings.enabledGPUs && 
                        this.settings.enabledGPUs.hasOwnProperty(index)) {
                        checkbox.checked = this.settings.enabledGPUs[index];
                    }
                });
            }
        }
        
        // Add message if no GPUs detected
        if (gpuToggles.children.length === 0) {
            gpuToggles.innerHTML = '<div style="color: #888; font-style: italic;">No GPUs detected</div>';
        }
    }
    
    /**
     * Switch to a specific tab
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }
    
    /**
     * Show settings panel
     */
    show() {
        const panel = document.getElementById('settings-panel');
        panel.classList.add('visible');
        this.isVisible = true;
        
        // Update performance info
        this.updatePerformanceInfo();
        
        // Update GPU settings
        this.updateGPUSettings();
    }
    
    /**
     * Hide settings panel
     */
    hide() {
        const panel = document.getElementById('settings-panel');
        panel.classList.remove('visible');
        this.isVisible = false;
    }
    
    /**
     * Toggle settings panel visibility
     */
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    /**
     * Update monitor visibility based on settings
     */
    updateMonitorVisibility() {
        // This will be implemented when integrating with the main monitor system
        // For now, just trigger an event that the main system can listen to
        document.dispatchEvent(new CustomEvent('monitorVisibilityChanged', {
            detail: this.settings.enabledMonitors
        }));
    }
    
    /**
     * Apply theme settings
     */
    applyTheme() {
        const root = document.documentElement;
        
        switch (this.settings.theme) {
            case 'light':
                root.style.setProperty('--bg-color', '#ffffff');
                root.style.setProperty('--text-color', '#000000');
                root.style.setProperty('--border-color', '#cccccc');
                break;
            case 'dark':
            default:
                root.style.setProperty('--bg-color', '#1a1a1a');
                root.style.setProperty('--text-color', '#ffffff');
                root.style.setProperty('--border-color', '#555555');
                break;
        }
    }
    
    /**
     * Apply display preferences
     */
    applyDisplayPreferences() {
        document.body.classList.toggle('compact-mode', this.settings.compactMode);
        document.body.classList.toggle('show-tooltips', this.settings.showTooltips);
        document.body.classList.toggle('show-percentages', this.settings.showPercentages);
        document.body.classList.toggle('show-values', this.settings.showValues);
        document.body.classList.toggle('update-animation', this.settings.updateAnimation);
        
        // Update CSS custom properties
        document.documentElement.style.setProperty('--animation-speed', `${this.settings.animationSpeed}ms`);
    }
    
    /**
     * Update performance information display
     */
    updatePerformanceInfo() {
        if (!this.systemMonitor) return;
        
        document.getElementById('current-update-rate').textContent = 
            `${this.settings.refreshRate}ms`;
        
        document.getElementById('connection-status').textContent = 
            this.systemMonitor.isConnected ? 'Connected' : 'Disconnected';
        
        // Count data points (approximate)
        const dataPoints = Object.keys(this.systemMonitor.progressBars || {}).length;
        document.getElementById('data-points').textContent = dataPoints;
    }
    
    /**
     * Reset settings to defaults
     */
    resetToDefaults() {
        if (confirm('Reset all settings to defaults? This cannot be undone.')) {
            this.settings = { ...this.defaultSettings };
            this.saveSettings();
            this.loadCurrentValues();
            alert('Settings reset to defaults.');
        }
    }
    
    /**
     * Export settings to file
     */
    exportSettings() {
        const dataStr = JSON.stringify(this.settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'system-monitor-settings.json';
        link.click();
    }
    
    /**
     * Import settings from file
     */
    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const imported = JSON.parse(event.target.result);
                    this.settings = { ...this.defaultSettings, ...imported };
                    this.saveSettings();
                    this.loadCurrentValues();
                    alert('Settings imported successfully.');
                } catch (error) {
                    alert('Error importing settings: Invalid file format.');
                }
            };
            reader.readAsText(file);
        };
        
        input.click();
    }
    
    /**
     * Get current settings
     */
    getSettings() {
        return { ...this.settings };
    }
    
    /**
     * Update a specific setting
     */
    updateSetting(key, value) {
        this.settings[key] = value;
        this.saveSettings();
    }
    
    // Task 6.2: Advanced Configuration Methods
    
    /**
     * Refresh available disk drives
     */
    refreshAvailableDrives() {
        // In a real implementation, this would query the backend for available drives
        // For now, we'll simulate common Windows drive letters
        const commonDrives = ['C:', 'D:', 'E:', 'F:', 'G:', 'H:'];
        const diskSelect = document.getElementById('disk-drives');
        
        if (diskSelect) {
            // Clear existing options
            diskSelect.innerHTML = '';
            
            // Add drive options
            commonDrives.forEach(drive => {
                const option = document.createElement('option');
                option.value = drive;
                option.textContent = `${drive} Drive`;
                if (drive === 'C:') {
                    option.textContent += ' (System)';
                }
                
                // Select if it was previously selected
                if (this.settings.selectedDiskDrives.includes(drive)) {
                    option.selected = true;
                }
                
                diskSelect.appendChild(option);
            });
        }
        
        // In a production environment, you would make an API call:
        // fetch('/api/drives').then(response => response.json()).then(drives => { ... });
    }
    
    /**
     * Apply color scheme preset
     */
    applyColorPreset(preset) {
        const presets = {
            default: {
                cpu: '#2196F3',
                memory: '#4CAF50',
                disk: '#FF9800',
                gpu: '#9C27B0',
                vram: '#E91E63',
                temperature: '#F44336'
            },
            cool: {
                cpu: '#00BCD4',
                memory: '#03A9F4',
                disk: '#2196F3',
                gpu: '#3F51B5',
                vram: '#673AB7',
                temperature: '#9C27B0'
            },
            warm: {
                cpu: '#FF5722',
                memory: '#FF9800',
                disk: '#FFC107',
                gpu: '#FFEB3B',
                vram: '#CDDC39',
                temperature: '#8BC34A'
            },
            monochrome: {
                cpu: '#757575',
                memory: '#9E9E9E',
                disk: '#BDBDBD',
                gpu: '#E0E0E0',
                vram: '#EEEEEE',
                temperature: '#F5F5F5'
            }
        };
        
        if (presets[preset]) {
            this.settings.colorScheme = { ...this.settings.colorScheme, ...presets[preset] };
            this.saveSettings();
            this.loadColorValues();
            this.applyColorScheme();
        }
    }
    
    /**
     * Load color values into color pickers
     */
    loadColorValues() {
        Object.keys(this.settings.colorScheme).forEach(type => {
            if (['cpu', 'memory', 'disk', 'gpu', 'vram', 'temperature'].includes(type)) {
                const colorInput = document.getElementById(`color-${type}`);
                if (colorInput) {
                    colorInput.value = this.settings.colorScheme[type];
                }
            }
        });
    }
    
    /**
     * Apply current color scheme to the monitor
     */
    applyColorScheme() {
        if (this.systemMonitor && this.settings.customColors) {
            // Update the system monitor's color scheme
            if (this.systemMonitor.colors) {
                Object.assign(this.systemMonitor.colors, this.settings.colorScheme);
            }
            
            // Apply colors to existing progress bars
            document.querySelectorAll('.progress-fill').forEach(fill => {
                const monitorItem = fill.closest('.monitor-item');
                if (monitorItem) {
                    const id = monitorItem.id.replace('monitor-', '');
                    
                    // Determine color based on monitor type
                    let color = '#2196F3'; // default
                    if (id.includes('cpu')) color = this.settings.colorScheme.cpu;
                    else if (id.includes('ram') || id.includes('memory')) color = this.settings.colorScheme.memory;
                    else if (id.includes('disk')) color = this.settings.colorScheme.disk;
                    else if (id.includes('gpu')) color = this.settings.colorScheme.gpu;
                    else if (id.includes('vram')) color = this.settings.colorScheme.vram;
                    else if (id.includes('temp')) color = this.settings.colorScheme.temperature;
                    
                    fill.style.backgroundColor = color;
                }
            });
        }
    }
    
    /**
     * Center window on screen
     */
    centerWindow() {
        const screenWidth = screen.width;
        const screenHeight = screen.height;
        const windowWidth = this.settings.windowSize.width;
        const windowHeight = this.settings.windowSize.height;
        
        const x = Math.floor((screenWidth - windowWidth) / 2);
        const y = Math.floor((screenHeight - windowHeight) / 2);
        
        this.settings.windowPosition.x = x;
        this.settings.windowPosition.y = y;
        
        document.getElementById('window-x').value = x;
        document.getElementById('window-y').value = y;
        
        this.saveSettings();
        this.applyWindowPosition();
    }
    
    /**
     * Reset window position to default
     */
    resetWindowPosition() {
        this.settings.windowPosition.x = 100;
        this.settings.windowPosition.y = 100;
        
        document.getElementById('window-x').value = 100;
        document.getElementById('window-y').value = 100;
        
        this.saveSettings();
        this.applyWindowPosition();
    }
    
    /**
     * Apply window position
     */
    applyWindowPosition() {
        if (this.settings.windowPosition.remember) {
            // In a Chrome app, this would use chrome.app.window API
            // For now, we'll just trigger an event
            document.dispatchEvent(new CustomEvent('windowPositionChanged', {
                detail: {
                    x: this.settings.windowPosition.x,
                    y: this.settings.windowPosition.y
                }
            }));
        }
    }
    
    /**
     * Apply layout settings
     */
    applyLayout() {
        const monitorsContent = document.getElementById('monitors-content');
        if (monitorsContent) {
            // Apply CSS classes based on layout settings
            monitorsContent.classList.toggle('stack-vertically', this.settings.windowLayout.stackVertically);
            monitorsContent.classList.toggle('group-by-type', this.settings.windowLayout.groupByType);
            monitorsContent.classList.toggle('show-headers', this.settings.windowLayout.showHeaders);
            
            // Set CSS custom property for columns
            monitorsContent.style.setProperty('--columns-per-row', this.settings.windowLayout.columnsPerRow);
        }
        
        document.dispatchEvent(new CustomEvent('layoutChanged', {
            detail: this.settings.windowLayout
        }));
    }
    
    /**
     * Apply performance settings
     */
    applyPerformanceSettings() {
        const settings = this.settings.performanceSettings;
        
        // Apply performance optimizations
        if (settings.reduceAnimations) {
            document.body.classList.add('reduced-animations');
        } else {
            document.body.classList.remove('reduced-animations');
        }
        
        if (settings.enableVSync) {
            document.documentElement.style.setProperty('--animation-timing', 'ease-out');
        } else {
            document.documentElement.style.setProperty('--animation-timing', 'linear');
        }
        
        // Enable/disable profiling
        if (settings.enableProfiling) {
            console.log('Performance profiling enabled');
            this.startPerformanceProfiling();
        }
        
        document.dispatchEvent(new CustomEvent('performanceSettingsChanged', {
            detail: settings
        }));
    }
    
    /**
     * Start performance profiling
     */
    startPerformanceProfiling() {
        if (!this.performanceMonitor) {
            this.performanceMonitor = {
                lastFrameTime: performance.now(),
                frameCount: 0,
                fps: 0
            };
            
            const updateFPS = () => {
                const now = performance.now();
                const delta = now - this.performanceMonitor.lastFrameTime;
                this.performanceMonitor.frameCount++;
                
                if (delta >= 1000) { // Update every second
                    this.performanceMonitor.fps = Math.round((this.performanceMonitor.frameCount * 1000) / delta);
                    this.performanceMonitor.frameCount = 0;
                    this.performanceMonitor.lastFrameTime = now;
                    
                    // Update FPS display
                    const fpsElement = document.getElementById('current-fps');
                    if (fpsElement) {
                        fpsElement.textContent = `${this.performanceMonitor.fps} FPS`;
                    }
                }
                
                if (this.settings.performanceSettings.enableProfiling) {
                    requestAnimationFrame(updateFPS);
                }
            };
            
            requestAnimationFrame(updateFPS);
        }
    }
    
    /**
     * Test notification system
     */
    testNotification(message, type) {
        if (this.settings.notifications.enabled) {
            // Create a visual notification
            const notification = document.createElement('div');
            notification.className = 'test-notification';
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-icon">⚠️</span>
                    <span class="notification-message">${message}</span>
                    <button class="notification-close">×</button>
                </div>
            `;
            
            // Add notification styles if not already added
            if (!document.getElementById('notification-styles')) {
                const notificationStyles = document.createElement('style');
                notificationStyles.id = 'notification-styles';
                notificationStyles.textContent = `
                    .test-notification {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #2d2d2d;
                        border: 1px solid #555;
                        border-radius: 8px;
                        padding: 15px;
                        color: #fff;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                        z-index: 10000;
                        animation: slideInRight 0.3s ease-out;
                        min-width: 300px;
                    }
                    
                    .notification-content {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    
                    .notification-icon {
                        font-size: 20px;
                    }
                    
                    .notification-message {
                        flex: 1;
                        font-size: 14px;
                    }
                    
                    .notification-close {
                        background: none;
                        border: none;
                        color: #ccc;
                        font-size: 18px;
                        cursor: pointer;
                        padding: 0;
                        width: 20px;
                        height: 20px;
                    }
                    
                    .notification-close:hover {
                        color: #fff;
                    }
                    
                    @keyframes slideInRight {
                        from {
                            transform: translateX(100%);
                            opacity: 0;
                        }
                        to {
                            transform: translateX(0);
                            opacity: 1;
                        }
                    }
                `;
                document.head.appendChild(notificationStyles);
            }
            
            document.body.appendChild(notification);
            
            // Set up close button
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                notification.remove();
            });
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
            
            // Play sound if enabled
            if (this.settings.notifications.soundEnabled) {
                this.playNotificationSound();
            }
        }
    }
    
    /**
     * Play notification sound
     */
    playNotificationSound() {
        // Create a simple beep sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn('Unable to play notification sound:', error);
        }
    }
    
    /**
     * Clear application cache
     */
    clearCache() {
        if (confirm('Clear all cached data? This will reset temporary data but keep your settings.')) {
            // Clear any cached monitoring data
            if (this.systemMonitor && this.systemMonitor.clearCache) {
                this.systemMonitor.clearCache();
            }
            
            // Clear performance monitoring data
            if (this.performanceMonitor) {
                this.performanceMonitor = null;
            }
            
            // Trigger cache clear event
            document.dispatchEvent(new CustomEvent('cacheCleared'));
            
            alert('Cache cleared successfully.');
        }
    }
}
