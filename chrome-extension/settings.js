// Settings management for System Resource Monitor Chrome Extension

class SettingsManager {
    constructor() {
        this.defaultSettings = {
            backendUrl: 'http://localhost:8888',
            updateInterval: 2000,
            autoReconnect: true,
            theme: 'dark',
            windowSize: 'medium',
            alwaysOnTop: false,
            enableCPU: true,
            enableMemory: true,
            enableDisk: true,
            enableGPU: true,
            enableNotifications: false,
            cpuThreshold: 85,
            memoryThreshold: 90
        };
        
        this.init();
    }
    
    async init() {
        console.log('Settings Manager initialized');
        await this.loadSettings();
        this.setupEventListeners();
        this.populateForm();
    }
    
    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get('settings');
            this.settings = { ...this.defaultSettings, ...result.settings };
            console.log('Settings loaded:', this.settings);
        } catch (error) {
            console.error('Error loading settings:', error);
            this.settings = { ...this.defaultSettings };
        }
    }
    
    async saveSettings() {
        try {
            await chrome.storage.sync.set({ settings: this.settings });
            console.log('Settings saved:', this.settings);
            this.showMessage('Settings saved successfully!', 'success');
            
            // Settings will be automatically picked up by other parts via storage.onChanged
            console.log('Settings will be broadcast via storage events');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showMessage('Error saving settings!', 'error');
        }
    }
    
    populateForm() {
        // Backend Connection
        document.getElementById('backendUrl').value = this.settings.backendUrl;
        document.getElementById('updateInterval').value = this.settings.updateInterval;
        document.getElementById('autoReconnect').checked = this.settings.autoReconnect;
        
        // Display Settings
        document.getElementById('theme').value = this.settings.theme;
        document.getElementById('windowSize').value = this.settings.windowSize;
        document.getElementById('alwaysOnTop').checked = this.settings.alwaysOnTop;
        
        // Monitoring Settings
        document.getElementById('enableCPU').checked = this.settings.enableCPU;
        document.getElementById('enableMemory').checked = this.settings.enableMemory;
        document.getElementById('enableDisk').checked = this.settings.enableDisk;
        document.getElementById('enableGPU').checked = this.settings.enableGPU;
        
        // Notification Settings
        document.getElementById('enableNotifications').checked = this.settings.enableNotifications;
        document.getElementById('cpuThreshold').value = this.settings.cpuThreshold;
        document.getElementById('memoryThreshold').value = this.settings.memoryThreshold;
    }
    
    collectFormData() {
        this.settings = {
            // Backend Connection
            backendUrl: document.getElementById('backendUrl').value.trim(),
            updateInterval: parseInt(document.getElementById('updateInterval').value),
            autoReconnect: document.getElementById('autoReconnect').checked,
            
            // Display Settings
            theme: document.getElementById('theme').value,
            windowSize: document.getElementById('windowSize').value,
            alwaysOnTop: document.getElementById('alwaysOnTop').checked,
            
            // Monitoring Settings
            enableCPU: document.getElementById('enableCPU').checked,
            enableMemory: document.getElementById('enableMemory').checked,
            enableDisk: document.getElementById('enableDisk').checked,
            enableGPU: document.getElementById('enableGPU').checked,
            
            // Notification Settings
            enableNotifications: document.getElementById('enableNotifications').checked,
            cpuThreshold: parseInt(document.getElementById('cpuThreshold').value),
            memoryThreshold: parseInt(document.getElementById('memoryThreshold').value)
        };
    }
    
    setupEventListeners() {
        // Save Settings Button
        document.getElementById('saveSettings').addEventListener('click', () => {
            this.collectFormData();
            this.saveSettings();
        });
        
        // Reset Settings Button
        document.getElementById('resetSettings').addEventListener('click', () => {
            if (confirm('Are you sure you want to reset all settings to defaults?')) {
                this.settings = { ...this.defaultSettings };
                this.populateForm();
                this.saveSettings();
            }
        });
        
        // Test Connection Button
        document.getElementById('testConnection').addEventListener('click', () => {
            this.testConnection();
        });
        
        // Clear Data Button
        document.getElementById('clearData').addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all stored data? This action cannot be undone.')) {
                this.clearAllData();
            }
        });
        
        // Form validation
        this.setupFormValidation();
    }
    
    setupFormValidation() {
        // Backend URL validation
        document.getElementById('backendUrl').addEventListener('blur', (e) => {
            const url = e.target.value.trim();
            if (url && !this.isValidUrl(url)) {
                e.target.style.borderColor = '#f44336';
                this.showMessage('Invalid URL format', 'error');
            } else {
                e.target.style.borderColor = '#555';
            }
        });
        
        // Update interval validation
        document.getElementById('updateInterval').addEventListener('change', (e) => {
            const interval = parseInt(e.target.value);
            if (interval < 1000 || interval > 30000) {
                e.target.style.borderColor = '#f44336';
                this.showMessage('Update interval must be between 1000-30000ms', 'error');
            } else {
                e.target.style.borderColor = '#555';
            }
        });
        
        // Threshold validation
        ['cpuThreshold', 'memoryThreshold'].forEach(id => {
            document.getElementById(id).addEventListener('change', (e) => {
                const value = parseInt(e.target.value);
                if (value < 50 || value > 100) {
                    e.target.style.borderColor = '#f44336';
                    this.showMessage('Threshold must be between 50-100%', 'error');
                } else {
                    e.target.style.borderColor = '#555';
                }
            });
        });
    }
    
    async testConnection() {
        const testButton = document.getElementById('testConnection');
        const originalText = testButton.textContent;
        
        testButton.textContent = '🔄 Testing...';
        testButton.disabled = true;
        
        try {
            const url = document.getElementById('backendUrl').value.trim();
            const response = await fetch(`${url}/api/status`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showMessage(`✅ Connection successful! Server: ${data.status || 'OK'}`, 'success');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Connection test failed:', error);
            this.showMessage(`❌ Connection failed: ${error.message}`, 'error');
        } finally {
            testButton.textContent = originalText;
            testButton.disabled = false;
        }
    }
    
    async clearAllData() {
        try {
            await chrome.storage.sync.clear();
            await chrome.storage.local.clear();
            
            // Reset to defaults
            this.settings = { ...this.defaultSettings };
            this.populateForm();
            
            this.showMessage('All data cleared and settings reset to defaults', 'success');
        } catch (error) {
            console.error('Error clearing data:', error);
            this.showMessage('Error clearing data!', 'error');
        }
    }
    
    showMessage(text, type = 'success') {
        const messageEl = document.getElementById('statusMessage');
        messageEl.textContent = text;
        messageEl.className = `status-message ${type}`;
        messageEl.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    }
    
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    // Export settings for backup
    exportSettings() {
        const dataStr = JSON.stringify(this.settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'system-resource-monitor-settings.json';
        link.click();
    }
    
    // Import settings from backup
    importSettings(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedSettings = JSON.parse(e.target.result);
                
                // Validate imported settings
                const validSettings = {};
                Object.keys(this.defaultSettings).forEach(key => {
                    if (importedSettings.hasOwnProperty(key)) {
                        validSettings[key] = importedSettings[key];
                    } else {
                        validSettings[key] = this.defaultSettings[key];
                    }
                });
                
                this.settings = validSettings;
                this.populateForm();
                this.saveSettings();
                
                this.showMessage('Settings imported successfully!', 'success');
            } catch (error) {
                console.error('Error importing settings:', error);
                this.showMessage('Error importing settings file!', 'error');
            }
        };
        reader.readAsText(file);
    }
}

// Theme management
class ThemeManager {
    constructor() {
        this.applyTheme();
    }
    
    async applyTheme() {
        try {
            const result = await chrome.storage.sync.get('settings');
            const theme = result.settings?.theme || 'dark';
            
            if (theme === 'auto') {
                // Use system preference
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                this.setTheme(prefersDark ? 'dark' : 'light');
            } else {
                this.setTheme(theme);
            }
        } catch (error) {
            console.error('Error applying theme:', error);
            this.setTheme('dark'); // Default fallback
        }
    }
    
    setTheme(theme) {
        document.body.className = theme === 'light' ? 'light-theme' : '';
        
        if (theme === 'light') {
            // Apply light theme styles
            document.body.style.backgroundColor = '#f5f5f5';
            document.body.style.color = '#333';
            
            const sections = document.querySelectorAll('.settings-section');
            sections.forEach(section => {
                section.style.backgroundColor = '#ffffff';
                section.style.borderColor = '#ddd';
            });
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SettingsManager();
    new ThemeManager();
});

// Handle window close
window.addEventListener('beforeunload', () => {
    console.log('Settings window closing');
});
