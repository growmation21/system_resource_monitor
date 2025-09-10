/**
 * UI Rendering System for System Resource Monitor
 * Handles real-time progress bar updates, tooltips, and multi-GPU support
 */

import { SystemMonitor, ConnectionState } from './monitor.js';

interface ProgressBarConfig {
  label: string;
  value: number;
  max: number;
  unit: string;
  color: string;
  tooltip?: string;
}

interface RenderOptions {
  showLabels: boolean;
  showValues: boolean;
  showTooltips: boolean;
  animationDuration: number;
  compactMode: boolean;
}

export class MonitorUI {
  private container: HTMLElement;
  private statusContainer!: HTMLElement;
  private monitorsContainer!: HTMLElement;
  private systemMonitor: SystemMonitor;
  
  private renderOptions: RenderOptions = {
    showLabels: true,
    showValues: true,
    showTooltips: true,
    animationDuration: 300,
    compactMode: false
  };
  
  // UI Element references
  private progressBars: Map<string, HTMLElement> = new Map();
  private tooltips: Map<string, HTMLElement> = new Map();
  
  // Color scheme
  private colors = {
    cpu: '#2196F3',      // Blue
    memory: '#4CAF50',   // Green
    disk: '#FF9800',     // Orange
    gpu: '#9C27B0',      // Purple
    vram: '#E91E63',     // Pink
    temperature: '#F44336', // Red
    background: '#1a1a1a',
    text: '#ffffff',
    border: '#333333',
    success: '#00ff00',
    warning: '#ffa500',
    error: '#ff4444'
  };
  
  constructor(container: HTMLElement, systemMonitor: SystemMonitor) {
    this.container = container;
    this.systemMonitor = systemMonitor;
    
    this.createBaseLayout();
    this.setupEventListeners();
    this.applyStyles();
  }
  
  /**
   * Create the base HTML layout
   */
  private createBaseLayout(): void {
    this.container.innerHTML = `
      <div id="status-container" class="status-container">
        <div id="connection-status" class="connection-status">
          <div class="spinner"></div>
          <div class="status-text">Connecting to System Monitor...</div>
        </div>
      </div>
      
      <div id="monitors-container" class="monitors-container" style="display: none;">
        <div class="header">
          <h2>System Resource Monitor</h2>
          <div class="settings-toggle" id="settings-toggle">⚙️</div>
        </div>
        
        <div id="monitors-content" class="monitors-content">
          <!-- Monitor displays will be populated here -->
        </div>
        
        <div id="settings-panel" class="settings-panel" style="display: none;">
          <!-- Settings controls will be populated here -->
        </div>
      </div>
    `;
    
    this.statusContainer = this.container.querySelector('#status-container') as HTMLElement;
    this.monitorsContainer = this.container.querySelector('#monitors-container') as HTMLElement;
  }
  
  /**
   * Setup event listeners
   */
  private setupEventListeners(): void {
    // Connection state changes
    this.systemMonitor.onStateChange((state) => {
      this.updateConnectionStatus(state);
    });
    
    // Monitor data updates
    this.systemMonitor.onDataReceived((data) => {
      this.updateMonitorDisplays(data);
    });
    
    // Settings changes
    this.systemMonitor.onSettingsChange((settings) => {
      this.updateSettingsPanel(settings);
    });
    
    // Settings toggle
    const settingsToggle = this.container.querySelector('#settings-toggle');
    if (settingsToggle) {
      settingsToggle.addEventListener('click', () => {
        this.toggleSettingsPanel();
      });
    }
  }
  
  /**
   * Apply CSS styles
   */
  private applyStyles(): void {
    const style = document.createElement('style');
    style.textContent = `
      .status-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        text-align: center;
      }
      
      .connection-status {
        padding: 20px;
      }
      
      .connection-status.connecting {
        color: ${this.colors.warning};
      }
      
      .connection-status.connected {
        color: ${this.colors.success};
      }
      
      .connection-status.error {
        color: ${this.colors.error};
      }
      
      .spinner {
        border: 2px solid ${this.colors.border};
        border-top: 2px solid ${this.colors.warning};
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 10px auto;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .monitors-container {
        width: 100%;
        height: 100vh;
        padding: 10px;
        box-sizing: border-box;
        overflow-y: auto;
      }
      
      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid ${this.colors.border};
      }
      
      .header h2 {
        margin: 0;
        color: ${this.colors.text};
        font-size: 16px;
      }
      
      .settings-toggle {
        cursor: pointer;
        padding: 5px;
        border-radius: 3px;
        transition: background-color 0.2s;
      }
      
      .settings-toggle:hover {
        background-color: ${this.colors.border};
      }
      
      .monitor-item {
        margin: 8px 0;
        padding: 8px;
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.05);
        transition: background-color 0.2s;
      }
      
      .monitor-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
      }
      
      .monitor-label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        margin-bottom: 4px;
        color: ${this.colors.text};
      }
      
      .monitor-value {
        font-weight: bold;
        font-size: 12px;
      }
      
      .progress-bar {
        width: 100%;
        height: 18px;
        background-color: ${this.colors.border};
        border-radius: 3px;
        overflow: hidden;
        position: relative;
      }
      
      .progress-fill {
        height: 100%;
        transition: width ${this.renderOptions.animationDuration}ms ease;
        position: relative;
      }
      
      .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 10px;
        font-weight: bold;
        color: ${this.colors.text};
        text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.7);
        z-index: 1;
      }
      
      .tooltip {
        position: absolute;
        background-color: rgba(0, 0, 0, 0.9);
        color: ${this.colors.text};
        padding: 8px;
        border-radius: 4px;
        font-size: 10px;
        white-space: nowrap;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.2s;
      }
      
      .tooltip.visible {
        opacity: 1;
      }
      
      .settings-panel {
        margin-top: 15px;
        padding: 15px;
        border: 1px solid ${this.colors.border};
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.05);
      }
      
      .settings-group {
        margin-bottom: 15px;
      }
      
      .settings-group h4 {
        margin: 0 0 8px 0;
        color: ${this.colors.text};
        font-size: 12px;
      }
      
      .settings-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
      }
      
      .settings-label {
        font-size: 10px;
        color: ${this.colors.text};
      }
      
      .settings-control {
        font-size: 10px;
      }
      
      .toggle-switch {
        position: relative;
        width: 30px;
        height: 16px;
        background-color: ${this.colors.border};
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
      }
      
      .toggle-switch.active {
        background-color: ${this.colors.cpu};
      }
      
      .toggle-switch::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        width: 12px;
        height: 12px;
        background-color: white;
        border-radius: 50%;
        transition: transform 0.2s;
      }
      
      .toggle-switch.active::after {
        transform: translateX(14px);
      }
      
      .compact-mode .monitor-item {
        margin: 3px 0;
        padding: 4px;
      }
      
      .compact-mode .monitor-label {
        font-size: 10px;
        margin-bottom: 2px;
      }
      
      .compact-mode .progress-bar {
        height: 12px;
      }
      
      .compact-mode .progress-text {
        font-size: 8px;
      }
    `;
    
    document.head.appendChild(style);
  }
  
  /**
   * Update connection status display
   */
  private updateConnectionStatus(state: ConnectionState): void {
    const statusElement = this.statusContainer.querySelector('.connection-status') as HTMLElement;
    const statusText = this.statusContainer.querySelector('.status-text') as HTMLElement;
    const spinner = this.statusContainer.querySelector('.spinner') as HTMLElement;
    
    statusElement.className = `connection-status ${state}`;
    
    switch (state) {
      case ConnectionState.Connecting:
        statusText.textContent = 'Connecting to System Monitor...';
        spinner.style.display = 'block';
        break;
        
      case ConnectionState.Connected:
        statusText.textContent = '✓ Connected to System Monitor';
        spinner.style.display = 'none';
        // Show monitors after brief delay
        setTimeout(() => {
          this.statusContainer.style.display = 'none';
          this.monitorsContainer.style.display = 'block';
          this.initializeMonitorDisplays();
        }, 1000);
        break;
        
      case ConnectionState.Error:
        statusText.innerHTML = `
          ❌ Connection Error<br>
          <div style="font-size: 10px; margin-top: 5px;">
            Make sure Python backend is running:<br>
            <code>python main.py</code>
          </div>
        `;
        spinner.style.display = 'none';
        break;
        
      case ConnectionState.Disconnected:
        statusText.textContent = 'Disconnected from System Monitor';
        spinner.style.display = 'none';
        this.statusContainer.style.display = 'block';
        this.monitorsContainer.style.display = 'none';
        break;
    }
  }
  
  /**
   * Initialize monitor displays
   */
  private initializeMonitorDisplays(): void {
    const content = this.monitorsContainer.querySelector('.monitors-content') as HTMLElement;
    content.innerHTML = ''; // Clear existing content
    
    // Create basic monitor templates that will be populated with real data
    this.createProgressBar('cpu', 'CPU Usage', 0, 100, '%', this.colors.cpu);
    this.createProgressBar('memory', 'Memory Usage', 0, 100, '%', this.colors.memory);
    this.createProgressBar('disk-total', 'Total Disk Usage', 0, 100, '%', this.colors.disk);
    
    // GPU monitors will be created dynamically based on detected GPUs
  }
  
  /**
   * Create a progress bar element
   */
  private createProgressBar(id: string, label: string, value: number, max: number, unit: string, color: string): HTMLElement {
    const content = this.monitorsContainer.querySelector('.monitors-content') as HTMLElement;
    
    const percent = max > 0 ? (value / max) * 100 : 0;
    const displayValue = unit === 'bytes' ? this.formatBytes(value) : `${value.toFixed(1)}${unit}`;
    const displayMax = unit === 'bytes' ? this.formatBytes(max) : `${max}${unit}`;
    
    const monitorItem = document.createElement('div');
    monitorItem.className = 'monitor-item';
    monitorItem.id = `monitor-${id}`;
    
    monitorItem.innerHTML = `
      <div class="monitor-label">
        <span>${label}</span>
        <span class="monitor-value">${displayValue} / ${displayMax}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${percent}%; background-color: ${color};"></div>
        <div class="progress-text">${percent.toFixed(1)}%</div>
      </div>
    `;
    
    content.appendChild(monitorItem);
    this.progressBars.set(id, monitorItem);
    
    // Add tooltip support
    if (this.renderOptions.showTooltips) {
      this.addTooltipSupport(monitorItem, id);
    }
    
    return monitorItem;
  }
  
  /**
   * Update monitor displays with new data
   */
  private updateMonitorDisplays(data: any): void {
    console.log('Updating monitor displays with:', data);
    
    // Update CPU
    if (data.cpu) {
      this.updateProgressBar('cpu', 'CPU Usage', data.cpu.usage, 100, '%', this.colors.cpu);
    }
    
    // Update Memory
    if (data.memory) {
      this.updateProgressBar('memory', 'Memory Usage', data.memory.percent, 100, '%', this.colors.memory);
      this.updateProgressBarTooltip('memory', `Used: ${this.formatBytes(data.memory.used)} / ${this.formatBytes(data.memory.total)}\\nAvailable: ${this.formatBytes(data.memory.available)}`);
    }
    
    // Update Disk
    if (data.drives && data.drives.length > 0) {
      // Calculate total disk usage
      let totalUsed = 0;
      let totalSpace = 0;
      
      data.drives.forEach((drive: any) => {
        totalUsed += drive.used_bytes;
        totalSpace += drive.total_bytes;
      });
      
      const totalPercent = totalSpace > 0 ? (totalUsed / totalSpace) * 100 : 0;
      this.updateProgressBar('disk-total', 'Total Disk Usage', totalPercent, 100, '%', this.colors.disk);
      
      // Create/update individual drive monitors
      data.drives.forEach((drive: any, index: number) => {
        const driveId = `disk-${drive.path.replace(/[^a-zA-Z0-9]/g, '_')}`;
        if (!this.progressBars.has(driveId)) {
          this.createProgressBar(driveId, `Drive ${drive.path}`, drive.used_percent, 100, '%', this.colors.disk);
        } else {
          this.updateProgressBar(driveId, `Drive ${drive.path}`, drive.used_percent, 100, '%', this.colors.disk);
        }
        this.updateProgressBarTooltip(driveId, `Used: ${this.formatBytes(drive.used_bytes)} / ${this.formatBytes(drive.total_bytes)}\\nFree: ${this.formatBytes(drive.free_bytes)}\\nFilesystem: ${drive.filesystem}`);
      });
    }
    
    // Update GPUs
    if (data.gpus && data.gpus.length > 0) {
      data.gpus.forEach((gpu: any, index: number) => {
        const gpuId = `gpu-${index}`;
        const vramId = `vram-${index}`;
        const tempId = `temp-${index}`;
        
        // GPU Utilization
        if (!this.progressBars.has(gpuId)) {
          this.createProgressBar(gpuId, `GPU ${index} (${gpu.name})`, gpu.gpu_utilization, 100, '%', this.colors.gpu);
        } else {
          this.updateProgressBar(gpuId, `GPU ${index} (${gpu.name})`, gpu.gpu_utilization, 100, '%', this.colors.gpu);
        }
        
        // VRAM Usage
        if (gpu.vram_total > 0) {
          if (!this.progressBars.has(vramId)) {
            this.createProgressBar(vramId, `GPU ${index} VRAM`, gpu.vram_used_percent, 100, '%', this.colors.vram);
          } else {
            this.updateProgressBar(vramId, `GPU ${index} VRAM`, gpu.vram_used_percent, 100, '%', this.colors.vram);
          }
          this.updateProgressBarTooltip(vramId, `Used: ${this.formatBytes(gpu.vram_used)} / ${this.formatBytes(gpu.vram_total)}`);
        }
        
        // Temperature
        if (gpu.gpu_temperature > 0) {
          if (!this.progressBars.has(tempId)) {
            this.createProgressBar(tempId, `GPU ${index} Temp`, gpu.gpu_temperature, 90, '°C', this.colors.temperature);
          } else {
            this.updateProgressBar(tempId, `GPU ${index} Temp`, gpu.gpu_temperature, 90, '°C', this.colors.temperature);
          }
        }
      });
    }
  }
  
  /**
   * Update a specific progress bar
   */
  private updateProgressBar(id: string, label: string, value: number, max: number, unit: string, color: string): void {
    const element = this.progressBars.get(id);
    if (!element) return;
    
    const percent = max > 0 ? Math.min((value / max) * 100, 100) : 0;
    const displayValue = unit === 'bytes' ? this.formatBytes(value) : `${value.toFixed(1)}${unit}`;
    const displayMax = unit === 'bytes' ? this.formatBytes(max) : `${max}${unit}`;
    
    const labelElement = element.querySelector('.monitor-label span') as HTMLElement;
    const valueElement = element.querySelector('.monitor-value') as HTMLElement;
    const fillElement = element.querySelector('.progress-fill') as HTMLElement;
    const textElement = element.querySelector('.progress-text') as HTMLElement;
    
    if (labelElement) labelElement.textContent = label;
    if (valueElement) valueElement.textContent = `${displayValue} / ${displayMax}`;
    if (fillElement) {
      fillElement.style.width = `${percent}%`;
      fillElement.style.backgroundColor = color;
    }
    if (textElement) textElement.textContent = `${percent.toFixed(1)}%`;
  }
  
  /**
   * Add tooltip support to an element
   */
  private addTooltipSupport(element: HTMLElement, id: string): void {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    document.body.appendChild(tooltip);
    this.tooltips.set(id, tooltip);
    
    element.addEventListener('mouseenter', (event) => {
      this.showTooltip(id, event as MouseEvent);
    });
    
    element.addEventListener('mousemove', (event) => {
      this.updateTooltipPosition(id, event as MouseEvent);
    });
    
    element.addEventListener('mouseleave', () => {
      this.hideTooltip(id);
    });
  }
  
  /**
   * Show tooltip
   */
  private showTooltip(id: string, event: MouseEvent): void {
    const tooltip = this.tooltips.get(id);
    if (tooltip) {
      tooltip.classList.add('visible');
      this.updateTooltipPosition(id, event);
    }
  }
  
  /**
   * Update tooltip position
   */
  private updateTooltipPosition(id: string, event: MouseEvent): void {
    const tooltip = this.tooltips.get(id);
    if (tooltip) {
      tooltip.style.left = `${event.clientX + 10}px`;
      tooltip.style.top = `${event.clientY - 10}px`;
    }
  }
  
  /**
   * Hide tooltip
   */
  private hideTooltip(id: string): void {
    const tooltip = this.tooltips.get(id);
    if (tooltip) {
      tooltip.classList.remove('visible');
    }
  }
  
  /**
   * Update tooltip content
   */
  private updateProgressBarTooltip(id: string, content: string): void {
    const tooltip = this.tooltips.get(id);
    if (tooltip) {
      tooltip.innerHTML = content.replace(/\\n/g, '<br>');
    }
  }
  
  /**
   * Toggle settings panel
   */
  private toggleSettingsPanel(): void {
    const panel = this.container.querySelector('#settings-panel') as HTMLElement;
    if (panel) {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
      
      if (panel.style.display === 'block') {
        this.populateSettingsPanel();
      }
    }
  }
  
  /**
   * Populate settings panel
   */
  private populateSettingsPanel(): void {
    const panel = this.container.querySelector('#settings-panel') as HTMLElement;
    if (!panel) return;
    
    const settings = this.systemMonitor.settings;
    
    panel.innerHTML = `
      <div class="settings-group">
        <h4>Monitoring Options</h4>
        <div class="settings-row">
          <span class="settings-label">CPU Monitoring</span>
          <div class="toggle-switch ${settings.enable_cpu ? 'active' : ''}" data-setting="enable_cpu"></div>
        </div>
        <div class="settings-row">
          <span class="settings-label">Memory Monitoring</span>
          <div class="toggle-switch ${settings.enable_ram ? 'active' : ''}" data-setting="enable_ram"></div>
        </div>
        <div class="settings-row">
          <span class="settings-label">Disk Monitoring</span>
          <div class="toggle-switch ${settings.enable_disk ? 'active' : ''}" data-setting="enable_disk"></div>
        </div>
        <div class="settings-row">
          <span class="settings-label">GPU Monitoring</span>
          <div class="toggle-switch ${settings.enable_gpu ? 'active' : ''}" data-setting="enable_gpu"></div>
        </div>
        <div class="settings-row">
          <span class="settings-label">VRAM Monitoring</span>
          <div class="toggle-switch ${settings.enable_vram ? 'active' : ''}" data-setting="enable_vram"></div>
        </div>
        <div class="settings-row">
          <span class="settings-label">Temperature Monitoring</span>
          <div class="toggle-switch ${settings.enable_temperature ? 'active' : ''}" data-setting="enable_temperature"></div>
        </div>
      </div>
      
      <div class="settings-group">
        <h4>Update Interval</h4>
        <div class="settings-row">
          <span class="settings-label">Refresh Rate</span>
          <select class="settings-control" data-setting="update_interval">
            <option value="0.5" ${settings.update_interval === 0.5 ? 'selected' : ''}>0.5s</option>
            <option value="1.0" ${settings.update_interval === 1.0 ? 'selected' : ''}>1.0s</option>
            <option value="2.0" ${settings.update_interval === 2.0 ? 'selected' : ''}>2.0s</option>
            <option value="5.0" ${settings.update_interval === 5.0 ? 'selected' : ''}>5.0s</option>
          </select>
        </div>
      </div>
    `;
    
    // Add event listeners for settings controls
    panel.querySelectorAll('.toggle-switch').forEach(toggle => {
      toggle.addEventListener('click', (event) => {
        const element = event.target as HTMLElement;
        const setting = element.getAttribute('data-setting');
        if (setting) {
          const currentValue = settings[setting as keyof typeof settings] as boolean;
          this.systemMonitor.updateSettings({ [setting]: !currentValue });
        }
      });
    });
    
    panel.querySelectorAll('select[data-setting]').forEach(select => {
      select.addEventListener('change', (event) => {
        const element = event.target as HTMLSelectElement;
        const setting = element.getAttribute('data-setting');
        if (setting) {
          const value = parseFloat(element.value);
          this.systemMonitor.updateSettings({ [setting]: value });
        }
      });
    });
  }
  
  /**
   * Update settings panel with new settings
   */
  private updateSettingsPanel(settings: any): void {
    // Update toggle switches
    this.container.querySelectorAll('.toggle-switch[data-setting]').forEach(toggle => {
      const setting = toggle.getAttribute('data-setting');
      if (setting && typeof settings[setting] === 'boolean') {
        toggle.classList.toggle('active', settings[setting]);
      }
    });
    
    // Update select elements
    this.container.querySelectorAll('select[data-setting]').forEach(select => {
      const setting = select.getAttribute('data-setting');
      if (setting && settings[setting] !== undefined) {
        (select as HTMLSelectElement).value = settings[setting].toString();
      }
    });
  }
  
  /**
   * Format bytes to human readable format
   */
  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }
  
  /**
   * Set render options
   */
  public setRenderOptions(options: Partial<RenderOptions>): void {
    this.renderOptions = { ...this.renderOptions, ...options };
    
    // Apply compact mode
    if (options.compactMode !== undefined) {
      this.container.classList.toggle('compact-mode', options.compactMode);
    }
    
    // Update animation duration
    if (options.animationDuration !== undefined) {
      const style = document.querySelector('style');
      if (style) {
        style.textContent = style.textContent?.replace(
          /transition: width \d+ms ease/g,
          `transition: width ${options.animationDuration}ms ease`
        ) || '';
      }
    }
  }
  
  /**
   * Cleanup resources
   */
  public destroy(): void {
    // Remove tooltips
    this.tooltips.forEach(tooltip => {
      tooltip.remove();
    });
    this.tooltips.clear();
    this.progressBars.clear();
  }
}
