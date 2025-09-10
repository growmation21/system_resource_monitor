// Monitor window JavaScript
class SystemMonitor {
    constructor() {
        this.backendUrl = 'http://localhost:8888';
        this.isConnected = false;
        this.websocket = null;
        this.reconnectInterval = null;
        this.lastData = null;
        
        this.statusElement = document.getElementById('status');
        this.monitorsElement = document.getElementById('monitors');
        
        this.colors = {
            cpu: '#2196F3',
            memory: '#4CAF50', 
            disk: '#FF9800',
            gpu: '#9C27B0',
            vram: '#E91E63',
            temperature: '#f44336'
        };
        
        this.progressBars = new Map();
        
        this.init();
    }
    
    async init() {
        await this.loadSettings();
        this.setupEventListeners();
        this.connect();
    }
    
    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get('settings');
            this.settings = result.settings || {
                backendUrl: 'http://localhost:8888',
                updateInterval: 2000,
                theme: 'dark',
                alwaysOnTop: false
            };
            
            if (this.settings.backendUrl) {
                this.backendUrl = this.settings.backendUrl;
            }
            
            // Apply always on top setting
            this.applyAlwaysOnTop();
            
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }
    
    setupEventListeners() {
        document.getElementById('testConnection').addEventListener('click', () => {
            this.connect();
        });
        
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.connect();
        });
        
        document.getElementById('settingsBtn').addEventListener('click', () => {
            chrome.runtime.sendMessage({
                action: 'openSettings'
            });
        });
        
        document.getElementById('closeBtn').addEventListener('click', () => {
            this.cleanup();
            window.close();
        });
        
        // Handle window unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // Set up periodic reconnection attempts
        this.reconnectInterval = setInterval(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, 5000);
        
        // Listen for settings changes via storage events (more reliable than messaging)
        chrome.storage.onChanged.addListener((changes, namespace) => {
            if (namespace === 'sync' && changes.settings) {
                console.log('Settings changed via storage event:', changes.settings.newValue);
                this.settings = changes.settings.newValue;
                if (this.settings.backendUrl) {
                    this.backendUrl = this.settings.backendUrl;
                }
                this.applyAlwaysOnTop();
            }
        });
        
        // Also listen for runtime messages as fallback
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            try {
                if (message.type === 'settingsChanged') {
                    console.log('Settings updated via message:', message.settings);
                    this.settings = message.settings;
                    this.backendUrl = this.settings.backendUrl;
                    this.applyAlwaysOnTop();
                    sendResponse({success: true});
                } else {
                    sendResponse({success: false, error: 'Unknown message type'});
                }
            } catch (error) {
                console.error('Error handling message:', error);
                sendResponse({success: false, error: error.message});
            }
            return true; // Keep message channel open for async response
        });
    }
    
    applyAlwaysOnTop() {
        if (this.settings && this.settings.alwaysOnTop) {
            // Enable always on top behavior
            this.enableAlwaysOnTop();
        } else {
            // Disable always on top behavior
            this.disableAlwaysOnTop();
        }
    }
    
    enableAlwaysOnTop() {
        try {
            // For Chrome extensions, we use a simpler approach for always-on-top
            // by keeping the window focused using setInterval
            
            console.log('Enabling always-on-top behavior');
            
            // Method 1: Periodic focus (fallback for Chrome extension limitations)
            this.alwaysOnTopInterval = setInterval(() => {
                try {
                    window.focus();
                } catch (error) {
                    console.warn('Could not focus window:', error);
                }
            }, 1000); // Check every second (less aggressive than before)
            
            // Method 2: Focus on visibility change
            this.focusHandler = () => {
                try {
                    window.focus();
                } catch (error) {
                    console.warn('Could not focus window on visibility change:', error);
                }
            };
            
            document.addEventListener('visibilitychange', this.focusHandler);
            window.addEventListener('blur', this.focusHandler);
            
            // Method 3: Try Chrome windows API if available (best effort)
            if (chrome && chrome.windows && chrome.windows.getCurrent) {
                chrome.windows.getCurrent((currentWindow) => {
                    if (chrome.runtime.lastError) {
                        console.warn('Chrome windows API not available:', chrome.runtime.lastError);
                        return;
                    }
                    
                    this.windowId = currentWindow.id;
                    console.log('Got window ID:', this.windowId);
                    
                    // Try to update window properties
                    if (chrome.windows.update) {
                        this.windowUpdateInterval = setInterval(() => {
                            if (this.windowId) {
                                chrome.windows.update(this.windowId, { focused: true }).catch(() => {
                                    // Ignore errors - this is best effort
                                });
                            }
                        }, 2000);
                    }
                });
            }
            
            console.log('Always on top enabled');
            
        } catch (error) {
            console.error('Error enabling always-on-top:', error);
        }
    }
    
    disableAlwaysOnTop() {
        try {
            // Clear all intervals and handlers
            if (this.alwaysOnTopInterval) {
                clearInterval(this.alwaysOnTopInterval);
                this.alwaysOnTopInterval = null;
            }
            
            if (this.windowUpdateInterval) {
                clearInterval(this.windowUpdateInterval);
                this.windowUpdateInterval = null;
            }
            
            if (this.focusHandler) {
                document.removeEventListener('visibilitychange', this.focusHandler);
                window.removeEventListener('blur', this.focusHandler);
                this.focusHandler = null;
            }
            
            console.log('Always on top disabled');
            
        } catch (error) {
            console.error('Error disabling always-on-top:', error);
        }
    }
    
    cleanup() {
        // Clean up always on top
        this.disableAlwaysOnTop();
        
        // Clean up WebSocket
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        // Clean up intervals
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }
        
        console.log('Monitor cleanup completed');
    }
    
    connect() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            return; // Already connected
        }
        
        try {
            const wsUrl = this.backendUrl.replace('http', 'ws') + '/ws';
            console.log('Connecting to:', wsUrl);
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.onConnected();
            };
            
            this.websocket.onmessage = (event) => {
                this.onMessage(event);
            };
            
            this.websocket.onclose = () => {
                this.onDisconnected();
            };
            
            this.websocket.onerror = (error) => {
                this.onError(error);
            };
            
        } catch (error) {
            this.onError(error);
        }
    }
    
    onConnected() {
        this.isConnected = true;
        this.statusElement.className = 'status connected';
        this.statusElement.innerHTML = '<div>✓ Connected to System Monitor</div>';
        
        // Hide status and show monitors after a brief delay
        setTimeout(() => {
            this.statusElement.style.display = 'none';
            this.monitorsElement.style.display = 'grid';
            this.initializeMonitorDisplay();
        }, 1000);
    }
    
    onDisconnected() {
        this.isConnected = false;
        this.statusElement.className = 'status connecting';
        this.statusElement.innerHTML = `
            <div class="spinner"></div>
            <div>Reconnecting...</div>
        `;
        this.statusElement.style.display = 'block';
        this.monitorsElement.style.display = 'none';
    }
    
    onError(error) {
        this.isConnected = false;
        this.statusElement.className = 'status error';
        this.statusElement.innerHTML = `
            <div>❌ Connection Error</div>
            <div style="font-size: 12px; margin-top: 8px;">Make sure Python backend is running</div>
            <div style="font-size: 10px; margin-top: 4px; background: #333; padding: 4px; border-radius: 2px;">
                python launch_monitor.py --port 8888
            </div>
            <div style="margin-top: 16px;">
                <button class="btn" onclick="systemMonitor.connect()">Retry Connection</button>
            </div>
        `;
    }
    
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received:', data);
            
            if (data.data) {
                this.lastData = data.data;
            }
            
            switch(data.type) {
                case 'connected':
                    console.log('Server connection confirmed');
                    break;
                case 'monitor_data':
                    this.updateMonitors(data.data);
                    break;
                case 'pong':
                    console.log('Pong received');
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Failed to parse message:', error);
        }
    }
    
    initializeMonitorDisplay() {
        this.monitorsElement.innerHTML = `
            <div style="text-align: center; padding: 20px; grid-column: 1 / -1;">
                <p>Waiting for hardware data...</p>
                <div style="margin-top: 20px;">
                    <button class="btn" onclick="systemMonitor.sendMessage({type: 'ping'})">
                        Test Connection
                    </button>
                </div>
            </div>
        `;
    }
    
    sendMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
    
    updateMonitors(data) {
        console.log('Received monitor data:', data);
        this.createMonitorDisplays(data);
    }
    
    createMonitorDisplays(data) {
        this.monitorsElement.innerHTML = ''; // Clear existing content
        
        // CPU Monitor
        if (data.cpu) {
            this.createProgressBar('cpu', 'CPU Usage', data.cpu.usage, 100, '%', this.colors.cpu);
        }
        
        // Memory Monitor
        if (data.memory) {
            this.createProgressBar('memory', 'Memory Usage', data.memory.percent, 100, '%', this.colors.memory);
        }
        
        // Disk Monitors
        if (data.drives && data.drives.length > 0) {
            data.drives.forEach((drive, index) => {
                const driveId = `disk-${drive.path.replace(/[^a-zA-Z0-9]/g, '_')}`;
                this.createProgressBar(driveId, `Drive ${drive.path}`, drive.used_percent, 100, '%', this.colors.disk);
            });
        }
        
        // GPU Monitors
        if (data.gpus && data.gpus.length > 0) {
            data.gpus.forEach((gpu, index) => {
                // GPU Utilization
                this.createProgressBar(`gpu-${index}`, `GPU ${index} (${gpu.name})`, gpu.gpu_utilization, 100, '%', this.colors.gpu);
                
                // VRAM Usage
                if (gpu.vram_total > 0) {
                    this.createProgressBar(`vram-${index}`, `GPU ${index} VRAM`, gpu.vram_used_percent, 100, '%', this.colors.vram);
                }
                
                // Temperature
                if (gpu.gpu_temperature > 0) {
                    this.createProgressBar(`temp-${index}`, `GPU ${index} Temp`, gpu.gpu_temperature, 90, '°C', this.colors.temperature);
                }
            });
        }
    }
    
    createProgressBar(id, label, value, max, unit, color) {
        const percent = max > 0 ? Math.min((value / max) * 100, 100) : 0;
        const displayValue = unit === 'bytes' ? this.formatBytes(value) : `${value.toFixed(1)}${unit}`;
        const displayMax = unit === 'bytes' ? this.formatBytes(max) : `${max}${unit}`;
        
        const monitorItem = document.createElement('div');
        monitorItem.className = 'monitor-item';
        monitorItem.id = `monitor-${id}`;
        
        monitorItem.innerHTML = `
            <div class="monitor-label">
                <span>${label}</span>
                <span class="monitor-value">${displayValue}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${percent}%; background-color: ${color};"></div>
                <div class="progress-text">${percent.toFixed(1)}%</div>
            </div>
        `;
        
        this.monitorsElement.appendChild(monitorItem);
        this.progressBars.set(id, monitorItem);
        
        return monitorItem;
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
    }
}

// Initialize monitor when DOM is loaded
let systemMonitor;
document.addEventListener('DOMContentLoaded', () => {
    systemMonitor = new SystemMonitor();
});
