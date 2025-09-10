/**
 * Window Management Utilities
 * 
 * Additional utilities and helpers for advanced window management features
 */

class WindowUtils {
    static calculateOptimalPosition(windowSize, displayBounds, position = 'topRight', offset = { x: 0, y: 0 }) {
        const { width, height } = windowSize;
        const { left, top, width: displayWidth, height: displayHeight } = displayBounds;
        
        let x, y;
        
        switch (position) {
            case 'topLeft':
                x = left + offset.x;
                y = top + offset.y;
                break;
            case 'topRight':
                x = left + displayWidth - width + offset.x;
                y = top + offset.y;
                break;
            case 'bottomLeft':
                x = left + offset.x;
                y = top + displayHeight - height + offset.y;
                break;
            case 'bottomRight':
                x = left + displayWidth - width + offset.x;
                y = top + displayHeight - height + offset.y;
                break;
            case 'center':
                x = left + (displayWidth - width) / 2 + offset.x;
                y = top + (displayHeight - height) / 2 + offset.y;
                break;
            default:
                x = left + offset.x;
                y = top + offset.y;
        }
        
        return { x, y };
    }
    
    static isPointOnScreen(x, y, displays) {
        return displays.some(display => {
            const bounds = display.bounds;
            return x >= bounds.left && 
                   x < bounds.left + bounds.width &&
                   y >= bounds.top && 
                   y < bounds.top + bounds.height;
        });
    }
    
    static findDisplayAt(x, y, displays) {
        return displays.find(display => {
            const bounds = display.bounds;
            return x >= bounds.left && 
                   x < bounds.left + bounds.width &&
                   y >= bounds.top && 
                   y < bounds.top + bounds.height;
        });
    }
    
    static constrainToDisplay(windowBounds, displayBounds) {
        const { left, top, width, height } = windowBounds;
        const display = displayBounds;
        
        let newLeft = Math.max(display.left, Math.min(left, display.left + display.width - width));
        let newTop = Math.max(display.top, Math.min(top, display.top + display.height - height));
        
        return { left: newLeft, top: newTop, width, height };
    }
    
    static snapToEdges(windowBounds, displayBounds, snapDistance = 10) {
        const { left, top, width, height } = windowBounds;
        const display = displayBounds;
        
        let newLeft = left;
        let newTop = top;
        
        // Snap to left edge
        if (Math.abs(left - display.left) <= snapDistance) {
            newLeft = display.left;
        }
        
        // Snap to right edge
        if (Math.abs((left + width) - (display.left + display.width)) <= snapDistance) {
            newLeft = display.left + display.width - width;
        }
        
        // Snap to top edge
        if (Math.abs(top - display.top) <= snapDistance) {
            newTop = display.top;
        }
        
        // Snap to bottom edge
        if (Math.abs((top + height) - (display.top + display.height)) <= snapDistance) {
            newTop = display.top + display.height - height;
        }
        
        return { left: newLeft, top: newTop, width, height };
    }
    
    static getDisplayScale(display) {
        // Chrome apps may have different scaling
        return display.workArea ? 
               (display.workArea.width / display.bounds.width) : 1;
    }
    
    static formatDisplayInfo(display, index) {
        const bounds = display.bounds;
        const name = display.name || `Monitor ${index + 1}`;
        const resolution = `${bounds.width}×${bounds.height}`;
        const position = `(${bounds.left}, ${bounds.top})`;
        
        return {
            index,
            name,
            resolution,
            position,
            isPrimary: display.isPrimary || index === 0,
            bounds: bounds
        };
    }
}

class WindowPresets {
    static presets = {
        compact: { width: 250, height: 150 },
        standard: { width: 300, height: 200 },
        detailed: { width: 400, height: 300 },
        sidebar: { width: 200, height: 400 },
        wide: { width: 500, height: 200 },
        square: { width: 250, height: 250 }
    };
    
    static getPreset(name) {
        return this.presets[name] || this.presets.standard;
    }
    
    static getAllPresets() {
        return Object.keys(this.presets).map(name => ({
            name,
            ...this.presets[name],
            displayName: name.charAt(0).toUpperCase() + name.slice(1)
        }));
    }
    
    static addCustomPreset(name, dimensions) {
        this.presets[name] = dimensions;
    }
}

class KeyboardShortcuts {
    constructor(windowManager) {
        this.windowManager = windowManager;
        this.shortcuts = {
            'ctrl+t': () => this.windowManager.toggleAlwaysOnTop(),
            'ctrl+m': () => this.moveToNextMonitor(),
            'ctrl+r': () => this.windowManager.resetWindowPosition(),
            'ctrl+s': () => this.toggleSettings(),
            'ctrl+1': () => this.applyPreset('compact'),
            'ctrl+2': () => this.applyPreset('standard'),
            'ctrl+3': () => this.applyPreset('detailed'),
            'escape': () => this.hideSettings()
        };
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyCombo(e);
            const handler = this.shortcuts[key];
            
            if (handler) {
                e.preventDefault();
                handler();
            }
        });
    }
    
    getKeyCombo(event) {
        const parts = [];
        
        if (event.ctrlKey) parts.push('ctrl');
        if (event.altKey) parts.push('alt');
        if (event.shiftKey) parts.push('shift');
        
        const key = event.key.toLowerCase();
        if (key !== 'control' && key !== 'alt' && key !== 'shift') {
            parts.push(key);
        }
        
        return parts.join('+');
    }
    
    moveToNextMonitor() {
        if (this.windowManager.availableDisplays.length <= 1) return;
        
        const currentMonitor = this.windowManager.windowState.monitor;
        const nextMonitor = (currentMonitor + 1) % this.windowManager.availableDisplays.length;
        
        this.windowManager.moveToMonitor(nextMonitor);
    }
    
    applyPreset(presetName) {
        const preset = WindowPresets.getPreset(presetName);
        this.windowManager.setWindowSize(preset.width, preset.height);
    }
    
    toggleSettings() {
        const windowControls = document.querySelector('.window-controls');
        if (windowControls) {
            const toggle = windowControls.querySelector('#window-controls-toggle');
            if (toggle) toggle.click();
        }
    }
    
    hideSettings() {
        const content = document.getElementById('window-controls-content');
        if (content && content.classList.contains('visible')) {
            const toggle = document.getElementById('window-controls-toggle');
            if (toggle) toggle.click();
        }
    }
}

class WindowAnimation {
    static animateMove(element, fromPos, toPos, duration = 300) {
        const startTime = performance.now();
        const deltaX = toPos.x - fromPos.x;
        const deltaY = toPos.y - fromPos.y;
        
        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            
            const currentX = fromPos.x + deltaX * easeOut;
            const currentY = fromPos.y + deltaY * easeOut;
            
            if (element.moveTo) {
                element.moveTo(currentX, currentY);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    static animateResize(element, fromSize, toSize, duration = 300) {
        const startTime = performance.now();
        const deltaWidth = toSize.width - fromSize.width;
        const deltaHeight = toSize.height - fromSize.height;
        
        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            
            const currentWidth = fromSize.width + deltaWidth * easeOut;
            const currentHeight = fromSize.height + deltaHeight * easeOut;
            
            if (element.resizeTo) {
                element.resizeTo(currentWidth, currentHeight);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }
}

class WindowValidator {
    static validateBounds(bounds, constraints) {
        const errors = [];
        
        if (bounds.width < constraints.minWidth) {
            errors.push(`Width ${bounds.width} is below minimum ${constraints.minWidth}`);
        }
        
        if (bounds.height < constraints.minHeight) {
            errors.push(`Height ${bounds.height} is below minimum ${constraints.minHeight}`);
        }
        
        if (bounds.width > constraints.maxWidth) {
            errors.push(`Width ${bounds.width} exceeds maximum ${constraints.maxWidth}`);
        }
        
        if (bounds.height > constraints.maxHeight) {
            errors.push(`Height ${bounds.height} exceeds maximum ${constraints.maxHeight}`);
        }
        
        return errors;
    }
    
    static validatePosition(position, displays) {
        if (displays.length === 0) return [];
        
        const isOnScreen = WindowUtils.isPointOnScreen(position.x, position.y, displays);
        
        return isOnScreen ? [] : ['Window position is off-screen'];
    }
    
    static sanitizeBounds(bounds, constraints, displays) {
        let sanitized = { ...bounds };
        
        // Apply size constraints
        sanitized.width = Math.max(constraints.minWidth, 
                         Math.min(sanitized.width, constraints.maxWidth));
        sanitized.height = Math.max(constraints.minHeight, 
                          Math.min(sanitized.height, constraints.maxHeight));
        
        // Ensure position is on screen
        if (displays.length > 0) {
            const display = WindowUtils.findDisplayAt(sanitized.left, sanitized.top, displays) || displays[0];
            sanitized = WindowUtils.constrainToDisplay(sanitized, display.bounds);
        }
        
        return sanitized;
    }
}
