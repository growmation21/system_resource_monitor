// Popup JavaScript
class SystemMonitorPopup {
    constructor() {
        this.backendUrl = 'http://localhost:8888';
        this.isConnected = false;
        this.init();
    }
    
    async init() {
        // Load settings
        await this.loadSettings();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start monitoring
        this.startMonitoring();
    }
    
    async loadSettings() {
        try {
            const result = await chrome.storage.local.get(['backend_url', 'theme']);
            if (result.backend_url) {
                this.backendUrl = result.backend_url;
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }
    
    setupEventListeners() {
        document.getElementById('openMonitor').addEventListener('click', () => {
            this.openMonitorWindow();
        });
        
        document.getElementById('settings').addEventListener('click', () => {
            this.openSettings();
        });
    }
    
    openMonitorWindow() {
        chrome.runtime.sendMessage({action: 'openWindow'}, (response) => {
            console.log('Monitor window opened');
        });
    }
    
    openSettings() {
        chrome.tabs.create({
            url: chrome.runtime.getURL('settings.html')
        });
    }
    
    async startMonitoring() {
        this.updateStatus('Connecting to backend...');
        
        try {
            const response = await fetch(`${this.backendUrl}/api/status`);
            if (response.ok) {
                const data = await response.json();
                this.isConnected = true;
                this.updateStatus('Connected');
                this.updateQuickStats(data);
            } else {
                throw new Error('Failed to connect');
            }
        } catch (error) {
            this.isConnected = false;
            this.updateStatus('Backend not running');
            this.showConnectionError();
        }
    }
    
    updateStatus(message) {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = `status ${this.isConnected ? 'connected' : 'disconnected'}`;
    }
    
    updateQuickStats(data) {
        const quickStatsElement = document.getElementById('quickStats');
        
        quickStatsElement.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">CPU Usage</span>
                <span class="stat-value">${data.cpu_utilization?.toFixed(1) || 0}%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Memory Usage</span>
                <span class="stat-value">${data.ram_used_percent?.toFixed(1) || 0}%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Disk Usage</span>
                <span class="stat-value">${data.hdd_used_percent?.toFixed(1) || 0}%</span>
            </div>
        `;
        
        if (data.gpus && data.gpus.length > 0) {
            const gpu = data.gpus[0];
            quickStatsElement.innerHTML += `
                <div class="stat-item">
                    <span class="stat-label">GPU Usage</span>
                    <span class="stat-value">${gpu.gpu_utilization || 0}%</span>
                </div>
            `;
        }
    }
    
    showConnectionError() {
        const quickStatsElement = document.getElementById('quickStats');
        quickStatsElement.innerHTML = `
            <div style="text-align: center; color: #f44336; padding: 16px;">
                <div>❌ Cannot connect to backend</div>
                <div style="font-size: 12px; margin-top: 8px;">
                    Make sure Python backend is running:<br>
                    <code style="background: #333; padding: 2px 4px; border-radius: 2px;">
                        python launch_monitor.py --port 8888
                    </code>
                </div>
            </div>
        `;
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SystemMonitorPopup();
});
