/**
 * Window Management System for System Resource Monitor
 * 
 * Provides advanced window management features including:
 * - Multi-monitor support
 * - Window position persistence
 * - Size constraints management
 * - Always-on-top toggle functionality
 * - Window state restoration
 */

// Import utilities if available
if (typeof importScripts !== 'undefined') {
    try {
        importScripts('window-utils.js');
    } catch (e) {
        console.warn('Window utilities not available:', e);
    }
}

class WindowManager {
    constructor() {
        this.storageKey = 'systemMonitor.windowState';
        this.defaultConfig = {
            width: 300,
            height: 200,
            minWidth: 200,
            minHeight: 150,
            maxWidth: 800,
            maxHeight: 600,
            left: 100,
            top: 100,
            alwaysOnTop: true,
            monitor: 0
        };
        
        this.currentWindow = null;
        this.availableDisplays = [];
        this.windowState = this.loadWindowState();
        
        // Initialize display detection
        this.initializeDisplays();
    }
    
    /**
     * Initialize display detection and multi-monitor support
     */
    initializeDisplays() {
        if (chrome.system && chrome.system.display) {
            chrome.system.display.getInfo((displays) => {
                this.availableDisplays = displays;
                console.log(`Detected ${displays.length} display(s):`, displays);
                
                // Validate saved monitor index
                if (this.windowState.monitor >= displays.length) {
                    this.windowState.monitor = 0;
                    this.saveWindowState();
                }
            });
        } else {
            console.log('Multi-monitor detection not available in this Chrome version');
            this.availableDisplays = [{
                id: 'primary',
                name: 'Primary Display',
                bounds: { left: 0, top: 0, width: 1920, height: 1080 }
            }];
        }
    }
    
    /**
     * Load window state from Chrome storage
     */
    loadWindowState() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                const parsed = JSON.parse(saved);
                return { ...this.defaultConfig, ...parsed };
            }
        } catch (e) {
            console.warn('Failed to load window state:', e);
        }
        return { ...this.defaultConfig };
    }
    
    /**
     * Save window state to Chrome storage
     */
    saveWindowState() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.windowState));
        } catch (e) {
            console.warn('Failed to save window state:', e);
        }
    }
    
    /**
     * Get optimal window position for specified monitor
     */
    getOptimalPosition(monitorIndex = 0) {
        if (this.availableDisplays.length === 0) {
            return { left: this.windowState.left, top: this.windowState.top };
        }
        
        const display = this.availableDisplays[monitorIndex] || this.availableDisplays[0];
        const bounds = display.bounds;
        
        // Calculate position within monitor bounds
        let left = bounds.left + this.windowState.left;
        let top = bounds.top + this.windowState.top;
        
        // Ensure window is visible on the target monitor
        const maxLeft = bounds.left + bounds.width - this.windowState.width;
        const maxTop = bounds.top + bounds.height - this.windowState.height;
        
        left = Math.max(bounds.left, Math.min(left, maxLeft));
        top = Math.max(bounds.top, Math.min(top, maxTop));
        
        return { left, top };
    }
    
    /**
     * Create window with enhanced management options
     */
    createWindow(htmlFile = 'window.html', options = {}) {
        const position = this.getOptimalPosition(this.windowState.monitor);
        
        const windowOptions = {
            id: 'systemMonitorWindow',
            innerBounds: {
                width: this.windowState.width,
                height: this.windowState.height,
                minWidth: this.windowState.minWidth,
                minHeight: this.windowState.minHeight,
                maxWidth: this.windowState.maxWidth,
                maxHeight: this.windowState.maxHeight
            },
            outerBounds: {
                left: position.left,
                top: position.top
            },
            frame: {
                type: 'chrome',
                color: '#2d2d2d'
            },
            alwaysOnTop: this.windowState.alwaysOnTop,
            resizable: true,
            focused: true,
            visibleOnAllWorkspaces: true,
            ...options
        };
        
        return new Promise((resolve, reject) => {
            chrome.app.window.create(htmlFile, windowOptions, (createdWindow) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                    return;
                }
                
                this.currentWindow = createdWindow;
                this.setupWindowEventHandlers(createdWindow);
                resolve(createdWindow);
            });
        });
    }
    
    /**
     * Setup window event handlers for state persistence
     */
    setupWindowEventHandlers(window) {
        // Handle window resize
        window.onBoundsChanged.addListener(() => {
            const bounds = window.getBounds();
            this.windowState.width = bounds.width;
            this.windowState.height = bounds.height;
            this.windowState.left = bounds.left;
            this.windowState.top = bounds.top;
            this.saveWindowState();
        });
        
        // Handle window move
        window.onMoved.addListener(() => {
            const bounds = window.getBounds();
            this.windowState.left = bounds.left;
            this.windowState.top = bounds.top;
            
            // Update monitor index based on position
            this.updateMonitorIndex(bounds.left, bounds.top);
            this.saveWindowState();
        });
        
        // Handle window close
        window.onClosed.addListener(() => {
            console.log('System Monitor window closed');
            this.currentWindow = null;
        });
        
        // Handle minimize/restore
        window.onMinimized.addListener(() => {
            console.log('System Monitor window minimized');
        });
        
        window.onRestored.addListener(() => {
            console.log('System Monitor window restored');
        });
        
        // Handle fullscreen changes
        window.onFullscreened.addListener(() => {
            console.log('System Monitor window fullscreened');
        });
        
        // Setup content window communication
        window.contentWindow.addEventListener('DOMContentLoaded', () => {
            this.setupContentWindowAPI(window);
        });
    }
    
    /**
     * Update monitor index based on window position
     */
    updateMonitorIndex(left, top) {
        for (let i = 0; i < this.availableDisplays.length; i++) {
            const display = this.availableDisplays[i];
            const bounds = display.bounds;
            
            if (left >= bounds.left && left < bounds.left + bounds.width &&
                top >= bounds.top && top < bounds.top + bounds.height) {
                this.windowState.monitor = i;
                break;
            }
        }
    }
    
    /**
     * Setup API for content window to control window management
     */
    setupContentWindowAPI(window) {
        const contentWindow = window.contentWindow;
        
        // Listen for window management messages
        contentWindow.addEventListener('message', (event) => {
            if (event.origin !== 'file://') return;
            
            const { type, data } = event.data;
            
            switch (type) {
                case 'TOGGLE_ALWAYS_ON_TOP':
                    this.toggleAlwaysOnTop();
                    break;
                    
                case 'MOVE_TO_MONITOR':
                    this.moveToMonitor(data.monitorIndex);
                    break;
                    
                case 'SET_WINDOW_SIZE':
                    this.setWindowSize(data.width, data.height);
                    break;
                    
                case 'MOVE_TO_POSITION':
                    this.moveToPosition(data.left, data.top);
                    break;
                    
                case 'RESET_WINDOW_POSITION':
                    this.resetWindowPosition();
                    break;
                    
                case 'CENTER_WINDOW':
                    this.centerWindow();
                    break;
                    
                case 'APPLY_PRESET':
                    this.applyPreset(data.presetName);
                    break;
                    
                case 'GET_WINDOW_STATE':
                    this.sendWindowState(contentWindow);
                    break;
                    
                case 'GET_DISPLAYS':
                    this.sendDisplayInfo(contentWindow);
                    break;
                    
                case 'SNAP_TO_EDGE':
                    this.snapToEdge(data.edge);
                    break;
            }
        });
        
        // Send initial backend URL and window state
        contentWindow.postMessage({
            type: 'BACKEND_URL',
            url: 'http://localhost:8888'
        }, '*');
        
        contentWindow.postMessage({
            type: 'WINDOW_STATE',
            state: this.windowState,
            displays: this.availableDisplays
        }, '*');
        
        // Setup keyboard shortcuts
        if (typeof KeyboardShortcuts !== 'undefined') {
            new KeyboardShortcuts(this);
        }
    }
    
    /**
     * Toggle always-on-top functionality
     */
    toggleAlwaysOnTop() {
        if (!this.currentWindow) return;
        
        this.windowState.alwaysOnTop = !this.windowState.alwaysOnTop;
        this.currentWindow.setAlwaysOnTop(this.windowState.alwaysOnTop);
        this.saveWindowState();
        
        console.log(`Always on top: ${this.windowState.alwaysOnTop}`);
        
        // Notify content window
        this.currentWindow.contentWindow.postMessage({
            type: 'ALWAYS_ON_TOP_CHANGED',
            alwaysOnTop: this.windowState.alwaysOnTop
        }, '*');
    }
    
    /**
     * Move window to specified monitor
     */
    moveToMonitor(monitorIndex) {
        if (!this.currentWindow || !this.availableDisplays[monitorIndex]) return;
        
        this.windowState.monitor = monitorIndex;
        const position = this.getOptimalPosition(monitorIndex);
        
        this.currentWindow.moveTo(position.left, position.top);
        this.saveWindowState();
        
        console.log(`Moved to monitor ${monitorIndex}`);
    }
    
    /**
     * Set window size with constraints
     */
    setWindowSize(width, height) {
        if (!this.currentWindow) return;
        
        // Apply size constraints
        width = Math.max(this.windowState.minWidth, Math.min(width, this.windowState.maxWidth));
        height = Math.max(this.windowState.minHeight, Math.min(height, this.windowState.maxHeight));
        
        this.currentWindow.resizeTo(width, height);
        this.windowState.width = width;
        this.windowState.height = height;
        this.saveWindowState();
        
        console.log(`Resized to ${width}x${height}`);
    }
    
    /**
     * Reset window to default position
     */
    resetWindowPosition() {
        if (!this.currentWindow) return;
        
        const position = this.getOptimalPosition(0); // Move to primary monitor
        this.currentWindow.moveTo(position.left, position.top);
        this.currentWindow.resizeTo(this.defaultConfig.width, this.defaultConfig.height);
        
        this.windowState = { ...this.defaultConfig };
        this.saveWindowState();
        
        console.log('Reset window position and size');
    }
    
    /**
     * Send current window state to content window
     */
    sendWindowState(contentWindow) {
        contentWindow.postMessage({
            type: 'WINDOW_STATE',
            state: this.windowState,
            displays: this.availableDisplays
        }, '*');
    }
    
    /**
     * Send display information to content window
     */
    sendDisplayInfo(contentWindow) {
        contentWindow.postMessage({
            type: 'DISPLAY_INFO',
            displays: this.availableDisplays,
            currentMonitor: this.windowState.monitor
        }, '*');
    }
    
    /**
     * Get window constraints for UI
     */
    getConstraints() {
        return {
            minWidth: this.windowState.minWidth,
            minHeight: this.windowState.minHeight,
            maxWidth: this.windowState.maxWidth,
            maxHeight: this.windowState.maxHeight
        };
    }
    
    /**
     * Update window constraints
     */
    setConstraints(constraints) {
        if (constraints.minWidth) this.windowState.minWidth = constraints.minWidth;
        if (constraints.minHeight) this.windowState.minHeight = constraints.minHeight;
        if (constraints.maxWidth) this.windowState.maxWidth = constraints.maxWidth;
        if (constraints.maxHeight) this.windowState.maxHeight = constraints.maxHeight;
        
        // Update current window if exists
        if (this.currentWindow) {
            this.currentWindow.setBounds({
                ...this.currentWindow.getBounds(),
                minWidth: this.windowState.minWidth,
                minHeight: this.windowState.minHeight,
                maxWidth: this.windowState.maxWidth,
                maxHeight: this.windowState.maxHeight
            });
        }
        
        this.saveWindowState();
    }
    
    /**
     * Move window to specific position
     */
    moveToPosition(left, top) {
        if (!this.currentWindow) return;
        
        this.currentWindow.moveTo(left, top);
        this.windowState.left = left;
        this.windowState.top = top;
        this.updateMonitorIndex(left, top);
        this.saveWindowState();
        
        console.log(`Moved to position ${left}, ${top}`);
    }
    
    /**
     * Center window on current monitor
     */
    centerWindow() {
        if (!this.currentWindow || this.availableDisplays.length === 0) return;
        
        const display = this.availableDisplays[this.windowState.monitor] || this.availableDisplays[0];
        const bounds = display.bounds;
        
        const centerX = bounds.left + (bounds.width - this.windowState.width) / 2;
        const centerY = bounds.top + (bounds.height - this.windowState.height) / 2;
        
        this.moveToPosition(centerX, centerY);
        console.log('Window centered');
    }
    
    /**
     * Apply window preset
     */
    applyPreset(presetName) {
        if (!this.currentWindow) return;
        
        const presets = {
            compact: { width: 250, height: 150 },
            standard: { width: 300, height: 200 },
            detailed: { width: 400, height: 300 },
            sidebar: { width: 200, height: 400 },
            wide: { width: 500, height: 200 }
        };
        
        const preset = presets[presetName];
        if (preset) {
            this.setWindowSize(preset.width, preset.height);
            console.log(`Applied preset: ${presetName}`);
        }
    }
    
    /**
     * Snap window to edge of current monitor
     */
    snapToEdge(edge) {
        if (!this.currentWindow || this.availableDisplays.length === 0) return;
        
        const display = this.availableDisplays[this.windowState.monitor] || this.availableDisplays[0];
        const bounds = display.bounds;
        const margin = 20; // Margin from screen edge
        
        let left = this.windowState.left;
        let top = this.windowState.top;
        
        switch (edge) {
            case 'left':
                left = bounds.left + margin;
                break;
            case 'right':
                left = bounds.left + bounds.width - this.windowState.width - margin;
                break;
            case 'top':
                top = bounds.top + margin;
                break;
            case 'bottom':
                top = bounds.top + bounds.height - this.windowState.height - margin;
                break;
            case 'topLeft':
                left = bounds.left + margin;
                top = bounds.top + margin;
                break;
            case 'topRight':
                left = bounds.left + bounds.width - this.windowState.width - margin;
                top = bounds.top + margin;
                break;
            case 'bottomLeft':
                left = bounds.left + margin;
                top = bounds.top + bounds.height - this.windowState.height - margin;
                break;
            case 'bottomRight':
                left = bounds.left + bounds.width - this.windowState.width - margin;
                top = bounds.top + bounds.height - this.windowState.height - margin;
                break;
        }
        
        this.moveToPosition(left, top);
        console.log(`Snapped to ${edge}`);
    }
    
    /**
     * Toggle window between monitors (for dual monitor setups)
     */
    toggleMonitor() {
        if (this.availableDisplays.length <= 1) return;
        
        const nextMonitor = (this.windowState.monitor + 1) % this.availableDisplays.length;
        this.moveToMonitor(nextMonitor);
    }
    
    /**
     * Get window information for debugging
     */
    getWindowInfo() {
        if (!this.currentWindow) return null;
        
        const bounds = this.currentWindow.getBounds();
        const display = this.availableDisplays[this.windowState.monitor];
        
        return {
            bounds,
            monitor: this.windowState.monitor,
            display: display ? display.name : 'Unknown',
            alwaysOnTop: this.windowState.alwaysOnTop,
            totalDisplays: this.availableDisplays.length
        };
    }
}

// Global window manager instance
const windowManager = new WindowManager();
