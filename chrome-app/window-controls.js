/**
 * Window Controls UI Component
 * 
 * Provides user interface controls for window management features
 * including monitor selection, always-on-top toggle, and window positioning.
 */

class WindowControls {
    constructor() {
        this.windowState = null;
        this.displays = [];
        this.isVisible = false;
        
        this.setupEventListeners();
        this.requestWindowState();
    }
    
    /**
     * Setup event listeners for window management messages
     */
    setupEventListeners() {
        window.addEventListener('message', (event) => {
            if (event.origin !== 'file://') return;
            
            const { type, state, displays, alwaysOnTop } = event.data;
            
            switch (type) {
                case 'WINDOW_STATE':
                    this.windowState = state;
                    this.displays = displays || [];
                    this.updateUI();
                    break;
                    
                case 'DISPLAY_INFO':
                    this.displays = displays || [];
                    this.updateDisplayList();
                    break;
                    
                case 'ALWAYS_ON_TOP_CHANGED':
                    if (this.windowState) {
                        this.windowState.alwaysOnTop = alwaysOnTop;
                        this.updateAlwaysOnTopButton();
                    }
                    break;
            }
        });
    }
    
    /**
     * Request current window state from background script
     */
    requestWindowState() {
        window.postMessage({ type: 'GET_WINDOW_STATE' }, '*');
        window.postMessage({ type: 'GET_DISPLAYS' }, '*');
    }
    
    /**
     * Create window controls UI
     */
    createUI() {
        const controlsContainer = document.createElement('div');
        controlsContainer.id = 'window-controls';
        controlsContainer.className = 'window-controls';
        controlsContainer.innerHTML = `
            <div class="window-controls-header">
                <h3>Window Settings</h3>
                <button id="window-controls-toggle" class="toggle-button">⚙️</button>
            </div>
            <div class="window-controls-content" id="window-controls-content">
                <div class="control-group">
                    <label>Always on Top:</label>
                    <button id="always-on-top-toggle" class="toggle-button">OFF</button>
                </div>
                
                <div class="control-group">
                    <label>Monitor:</label>
                    <select id="monitor-select">
                        <option value="0">Primary Monitor</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Window Size:</label>
                    <div class="size-controls">
                        <input type="number" id="window-width" placeholder="Width" min="200" max="800">
                        <span>×</span>
                        <input type="number" id="window-height" placeholder="Height" min="150" max="600">
                        <button id="apply-size">Apply</button>
                    </div>
                </div>
                
                <div class="control-group">
                    <label>Quick Actions:</label>
                    <div class="quick-actions">
                        <button id="reset-position">Reset Position</button>
                        <button id="center-window">Center Window</button>
                        <button id="toggle-monitor">Next Monitor</button>
                    </div>
                </div>
                
                <div class="control-group">
                    <label>Snap to Edge:</label>
                    <div class="snap-controls">
                        <button class="snap-btn" data-edge="topLeft">↖</button>
                        <button class="snap-btn" data-edge="top">↑</button>
                        <button class="snap-btn" data-edge="topRight">↗</button>
                        <button class="snap-btn" data-edge="left">←</button>
                        <button class="snap-btn" data-edge="right">→</button>
                        <button class="snap-btn" data-edge="bottomLeft">↙</button>
                        <button class="snap-btn" data-edge="bottom">↓</button>
                        <button class="snap-btn" data-edge="bottomRight">↘</button>
                    </div>
                </div>
                
                <div class="control-group">
                    <label>Presets:</label>
                    <div class="preset-controls">
                        <button class="preset-btn" data-preset="compact">Compact</button>
                        <button class="preset-btn" data-preset="standard">Standard</button>
                        <button class="preset-btn" data-preset="detailed">Detailed</button>
                        <button class="preset-btn" data-preset="sidebar">Sidebar</button>
                    </div>
                </div>
                
                <div class="control-group">
                    <label>Window Info:</label>
                    <div class="window-info" id="window-info">
                        <div>Position: <span id="position-info">-</span></div>
                        <div>Size: <span id="size-info">-</span></div>
                        <div>Monitor: <span id="monitor-info">-</span></div>
                    </div>
                </div>
            </div>
        `;
        
        return controlsContainer;
    }
    
    /**
     * Add CSS styles for window controls
     */
    addStyles() {
        if (document.getElementById('window-controls-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'window-controls-styles';
        styles.textContent = `
            .window-controls {
                background: rgba(45, 45, 45, 0.95);
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12px;
                color: #fff;
            }
            
            .window-controls-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid #555;
            }
            
            .window-controls-header h3 {
                margin: 0;
                font-size: 14px;
                color: #ccc;
            }
            
            .window-controls-content {
                display: none;
            }
            
            .window-controls-content.visible {
                display: block;
            }
            
            .control-group {
                margin: 8px 0;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .control-group label {
                font-weight: 500;
                color: #ccc;
                min-width: 80px;
            }
            
            .toggle-button {
                background: #4a4a4a;
                border: 1px solid #666;
                border-radius: 4px;
                color: #fff;
                padding: 4px 8px;
                cursor: pointer;
                font-size: 11px;
                transition: all 0.2s;
            }
            
            .toggle-button:hover {
                background: #5a5a5a;
            }
            
            .toggle-button.active {
                background: #0078d4;
                border-color: #106ebe;
            }
            
            #monitor-select {
                background: #4a4a4a;
                border: 1px solid #666;
                border-radius: 4px;
                color: #fff;
                padding: 4px 8px;
                font-size: 11px;
                min-width: 120px;
            }
            
            .size-controls {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .size-controls input {
                background: #4a4a4a;
                border: 1px solid #666;
                border-radius: 4px;
                color: #fff;
                padding: 4px 6px;
                width: 60px;
                font-size: 11px;
            }
            
            .size-controls span {
                color: #ccc;
            }
            
            .quick-actions {
                display: flex;
                gap: 5px;
            }
            
            .quick-actions button {
                background: #4a4a4a;
                border: 1px solid #666;
                border-radius: 4px;
                color: #fff;
                padding: 4px 8px;
                cursor: pointer;
                font-size: 10px;
                transition: all 0.2s;
            }
            
            .quick-actions button:hover {
                background: #5a5a5a;
            }
            
            .snap-controls {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 3px;
                max-width: 90px;
            }
            
            .snap-btn {
                background: #4a4a4a;
                border: 1px solid #666;
                border-radius: 3px;
                color: #fff;
                padding: 6px;
                cursor: pointer;
                font-size: 10px;
                transition: all 0.2s;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .snap-btn:hover {
                background: #5a5a5a;
                transform: scale(1.1);
            }
            
            .snap-btn:active {
                background: #0078d4;
            }
            
            .preset-controls {
                display: flex;
                flex-wrap: wrap;
                gap: 3px;
            }
            
            .preset-btn {
                background: #4a4a4a;
                border: 1px solid #666;
                border-radius: 3px;
                color: #fff;
                padding: 3px 6px;
                cursor: pointer;
                font-size: 9px;
                transition: all 0.2s;
            }
            
            .preset-btn:hover {
                background: #5a5a5a;
            }
            
            .preset-btn:active {
                background: #0078d4;
            }
            
            .window-info {
                font-size: 10px;
                color: #aaa;
            }
            
            .window-info div {
                margin: 2px 0;
            }
            
            .window-info span {
                color: #ccc;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * Initialize window controls
     */
    init(container) {
        this.addStyles();
        const controlsUI = this.createUI();
        container.appendChild(controlsUI);
        
        this.setupUIEventListeners();
        this.updateUI();
    }
    
    /**
     * Setup UI event listeners
     */
    setupUIEventListeners() {
        // Toggle controls visibility
        document.getElementById('window-controls-toggle').addEventListener('click', () => {
            this.toggleControlsVisibility();
        });
        
        // Always on top toggle
        document.getElementById('always-on-top-toggle').addEventListener('click', () => {
            window.postMessage({ type: 'TOGGLE_ALWAYS_ON_TOP' }, '*');
        });
        
        // Monitor selection
        document.getElementById('monitor-select').addEventListener('change', (e) => {
            const monitorIndex = parseInt(e.target.value);
            window.postMessage({ 
                type: 'MOVE_TO_MONITOR', 
                data: { monitorIndex } 
            }, '*');
        });
        
        // Window size application
        document.getElementById('apply-size').addEventListener('click', () => {
            const width = parseInt(document.getElementById('window-width').value);
            const height = parseInt(document.getElementById('window-height').value);
            
            if (width && height) {
                window.postMessage({ 
                    type: 'SET_WINDOW_SIZE', 
                    data: { width, height } 
                }, '*');
            }
        });
        
        // Reset position
        document.getElementById('reset-position').addEventListener('click', () => {
            window.postMessage({ type: 'RESET_WINDOW_POSITION' }, '*');
        });
        
        // Center window (calculate center of current monitor)
        document.getElementById('center-window').addEventListener('click', () => {
            window.postMessage({ type: 'CENTER_WINDOW' }, '*');
        });
        
        // Toggle monitor
        document.getElementById('toggle-monitor').addEventListener('click', () => {
            if (this.displays.length > 1) {
                const nextMonitor = (this.windowState.monitor + 1) % this.displays.length;
                window.postMessage({ 
                    type: 'MOVE_TO_MONITOR', 
                    data: { monitorIndex: nextMonitor } 
                }, '*');
            }
        });
        
        // Snap controls
        document.querySelectorAll('.snap-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const edge = btn.dataset.edge;
                window.postMessage({ 
                    type: 'SNAP_TO_EDGE', 
                    data: { edge } 
                }, '*');
            });
        });
        
        // Preset controls
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = btn.dataset.preset;
                window.postMessage({ 
                    type: 'APPLY_PRESET', 
                    data: { presetName: preset } 
                }, '*');
            });
        });
    }
    
    /**
     * Toggle controls visibility
     */
    toggleControlsVisibility() {
        const content = document.getElementById('window-controls-content');
        const toggle = document.getElementById('window-controls-toggle');
        
        this.isVisible = !this.isVisible;
        
        if (this.isVisible) {
            content.classList.add('visible');
            toggle.textContent = '▼';
        } else {
            content.classList.remove('visible');
            toggle.textContent = '⚙️';
        }
    }
    
    /**
     * Update UI with current window state
     */
    updateUI() {
        if (!this.windowState) return;
        
        this.updateAlwaysOnTopButton();
        this.updateDisplayList();
        this.updateSizeInputs();
        this.updateWindowInfo();
    }
    
    /**
     * Update always-on-top button
     */
    updateAlwaysOnTopButton() {
        const button = document.getElementById('always-on-top-toggle');
        if (!button || !this.windowState) return;
        
        if (this.windowState.alwaysOnTop) {
            button.textContent = 'ON';
            button.classList.add('active');
        } else {
            button.textContent = 'OFF';
            button.classList.remove('active');
        }
    }
    
    /**
     * Update display list
     */
    updateDisplayList() {
        const select = document.getElementById('monitor-select');
        if (!select) return;
        
        select.innerHTML = '';
        
        this.displays.forEach((display, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = display.name || `Monitor ${index + 1}`;
            
            if (this.windowState && index === this.windowState.monitor) {
                option.selected = true;
            }
            
            select.appendChild(option);
        });
    }
    
    /**
     * Update size input fields
     */
    updateSizeInputs() {
        if (!this.windowState) return;
        
        const widthInput = document.getElementById('window-width');
        const heightInput = document.getElementById('window-height');
        
        if (widthInput) widthInput.value = this.windowState.width;
        if (heightInput) heightInput.value = this.windowState.height;
    }
    
    /**
     * Update window information display
     */
    updateWindowInfo() {
        if (!this.windowState) return;
        
        const positionInfo = document.getElementById('position-info');
        const sizeInfo = document.getElementById('size-info');
        const monitorInfo = document.getElementById('monitor-info');
        
        if (positionInfo) {
            positionInfo.textContent = `${this.windowState.left}, ${this.windowState.top}`;
        }
        
        if (sizeInfo) {
            sizeInfo.textContent = `${this.windowState.width} × ${this.windowState.height}`;
        }
        
        if (monitorInfo) {
            const display = this.displays[this.windowState.monitor];
            monitorInfo.textContent = display ? display.name || `Monitor ${this.windowState.monitor + 1}` : 'Unknown';
        }
    }
}

// Initialize window controls when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const windowControls = new WindowControls();
    
    // Add controls to settings panel or create standalone
    const settingsPanel = document.querySelector('.settings-panel');
    if (settingsPanel) {
        windowControls.init(settingsPanel);
    } else {
        // Create standalone controls container
        const container = document.createElement('div');
        container.className = 'window-controls-container';
        document.body.appendChild(container);
        windowControls.init(container);
    }
});
