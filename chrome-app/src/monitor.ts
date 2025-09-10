/**
 * Core System Monitor TypeScript Component
 * Manages WebSocket connections, API communication, and settings
 */

interface SystemSettings {
  enable_cpu: boolean;
  enable_ram: boolean;
  enable_disk: boolean;
  enable_gpu: boolean;
  enable_vram: boolean;
  enable_temperature: boolean;
  update_interval: number;
  selected_drives: string[];
  save: boolean;
}

interface GPUInfo {
  index: number;
  name: string;
  gpu_utilization: number;
  gpu_temperature: number;
  vram_total: number;
  vram_used: number;
  vram_used_percent: number;
  device_type: string;
}

interface DriveInfo {
  path: string;
  available: boolean;
  total_bytes: number;
  used_bytes: number;
  free_bytes: number;
  used_percent: number;
  filesystem: string;
  device: string;
}

interface MonitorData {
  timestamp: number;
  cpu?: {
    usage: number;
    cores: number;
    frequency: number;
  };
  memory?: {
    total: number;
    used: number;
    available: number;
    percent: number;
  };
  gpus?: GPUInfo[];
  drives?: DriveInfo[];
}

export enum ConnectionState {
  Disconnected = 'disconnected',
  Connecting = 'connecting',
  Connected = 'connected',
  Error = 'error'
}

export class SystemMonitor {
  private backendUrl: string = 'http://localhost:8888';
  private websocket: WebSocket | null = null;
  private connectionState: ConnectionState = ConnectionState.Disconnected;
  private reconnectInterval: number | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  
  // Settings management
  private currentSettings: SystemSettings = {
    enable_cpu: true,
    enable_ram: true,
    enable_disk: true,
    enable_gpu: true,
    enable_vram: true,
    enable_temperature: true,
    update_interval: 1.0,
    selected_drives: [],
    save: false
  };
  
  // Event handlers
  private onConnectionStateChange: ((state: ConnectionState) => void) | null = null;
  private onMonitorDataReceived: ((data: MonitorData) => void) | null = null;
  private onSettingsChanged: ((settings: SystemSettings) => void) | null = null;
  
  constructor(backendUrl?: string) {
    if (backendUrl) {
      this.backendUrl = backendUrl;
    }
    
    this.init();
  }
  
  /**
   * Initialize the monitor system
   */
  private init(): void {
    // Listen for backend URL updates from background script
    window.addEventListener('message', (event) => {
      if (event.data.type === 'BACKEND_URL') {
        this.backendUrl = event.data.url;
        this.connect();
      }
    });
    
    // Try initial connection
    setTimeout(() => this.connect(), 1000);
    
    // Set up periodic reconnection attempts
    this.setupReconnectTimer();
  }
  
  /**
   * Establish WebSocket connection to backend
   */
  public connect(): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      return; // Already connected
    }
    
    this.setConnectionState(ConnectionState.Connecting);
    
    try {
      const wsUrl = this.backendUrl.replace('http', 'ws') + '/ws';
      console.log('Connecting to:', wsUrl);
      
      this.websocket = new WebSocket(wsUrl);
      
      this.websocket.onopen = () => {
        this.onWebSocketOpen();
      };
      
      this.websocket.onmessage = (event) => {
        this.onWebSocketMessage(event);
      };
      
      this.websocket.onclose = (event) => {
        this.onWebSocketClose(event);
      };
      
      this.websocket.onerror = (error) => {
        this.onWebSocketError(error);
      };
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.setConnectionState(ConnectionState.Error);
    }
  }
  
  /**
   * Disconnect from backend
   */
  public disconnect(): void {
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval);
      this.reconnectInterval = null;
    }
    
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    this.setConnectionState(ConnectionState.Disconnected);
  }
  
  /**
   * Handle WebSocket connection open
   */
  private onWebSocketOpen(): void {
    console.log('WebSocket connected');
    this.setConnectionState(ConnectionState.Connected);
    this.reconnectAttempts = 0;
    
    // Send initial handshake
    this.sendMessage({
      type: 'connect',
      client_info: {
        client_type: 'chrome_app',
        version: '1.0.0'
      }
    });
    
    // Request initial status and settings
    this.requestInitialData();
  }
  
  /**
   * Handle WebSocket message
   */
  private onWebSocketMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      console.log('Received WebSocket message:', data);
      
      switch (data.type) {
        case 'connected':
          console.log('Server connection confirmed:', data.message);
          break;
          
        case 'monitor_data':
          this.handleMonitorData(data.data);
          break;
          
        case 'settings_updated':
          this.handleSettingsUpdate(data.data);
          break;
          
        case 'pong':
          console.log('Pong received');
          break;
          
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }
  
  /**
   * Handle WebSocket connection close
   */
  private onWebSocketClose(event: CloseEvent): void {
    console.log('WebSocket disconnected:', event.code, event.reason);
    this.websocket = null;
    
    if (event.code !== 1000) { // Not a normal closure
      this.setConnectionState(ConnectionState.Error);
    } else {
      this.setConnectionState(ConnectionState.Disconnected);
    }
    
    // Attempt to reconnect
    this.scheduleReconnect();
  }
  
  /**
   * Handle WebSocket error
   */
  private onWebSocketError(error: Event): void {
    console.error('WebSocket error:', error);
    this.setConnectionState(ConnectionState.Error);
  }
  
  /**
   * Send message to backend via WebSocket
   */
  private sendMessage(message: any): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  }
  
  /**
   * Request initial data from backend
   */
  private requestInitialData(): void {
    // Request current system status
    this.sendMessage({
      type: 'get_status'
    });
    
    // Load available drives and GPU information via API
    this.loadSystemCapabilities();
  }
  
  /**
   * Load system capabilities via API endpoints
   */
  private async loadSystemCapabilities(): Promise<void> {
    try {
      // Load GPU information
      const gpuResponse = await fetch(`${this.backendUrl}/resources/monitor/GPU`);
      if (gpuResponse.ok) {
        const gpuData = await gpuResponse.json();
        console.log('GPU capabilities:', gpuData);
      }
      
      // Load HDD information
      const hddResponse = await fetch(`${this.backendUrl}/resources/monitor/HDD`);
      if (hddResponse.ok) {
        const hddData = await hddResponse.json();
        console.log('HDD capabilities:', hddData);
        
        // Update available drives in settings
        if (hddData.success && hddData.available_drives) {
          this.currentSettings.selected_drives = hddData.available_drives.slice(0, 3); // Default to first 3 drives
        }
      }
      
    } catch (error) {
      console.error('Failed to load system capabilities:', error);
    }
  }
  
  /**
   * Handle incoming monitor data
   */
  private handleMonitorData(data: MonitorData): void {
    if (this.onMonitorDataReceived) {
      this.onMonitorDataReceived(data);
    }
  }
  
  /**
   * Handle settings update from backend
   */
  private handleSettingsUpdate(settings: SystemSettings): void {
    this.currentSettings = { ...this.currentSettings, ...settings };
    if (this.onSettingsChanged) {
      this.onSettingsChanged(this.currentSettings);
    }
  }
  
  /**
   * Update monitor settings via API
   */
  public async updateSettings(newSettings: Partial<SystemSettings>): Promise<boolean> {
    try {
      const updatedSettings = { ...this.currentSettings, ...newSettings };
      
      const response = await fetch(`${this.backendUrl}/resources/monitor`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedSettings)
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          this.currentSettings = updatedSettings;
          if (this.onSettingsChanged) {
            this.onSettingsChanged(this.currentSettings);
          }
          return true;
        }
      }
      
      console.error('Failed to update settings:', response.statusText);
      return false;
      
    } catch (error) {
      console.error('Error updating settings:', error);
      return false;
    }
  }
  
  /**
   * Update GPU-specific settings
   */
  public async updateGPUSettings(gpuIndex: number, settings: {
    enable_monitoring?: boolean;
    enable_vram?: boolean;
    enable_temperature?: boolean;
    save?: boolean;
  }): Promise<boolean> {
    try {
      const response = await fetch(`${this.backendUrl}/resources/monitor/GPU/${gpuIndex}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });
      
      if (response.ok) {
        const result = await response.json();
        return result.success;
      }
      
      console.error('Failed to update GPU settings:', response.statusText);
      return false;
      
    } catch (error) {
      console.error('Error updating GPU settings:', error);
      return false;
    }
  }
  
  /**
   * Set connection state and notify listeners
   */
  private setConnectionState(state: ConnectionState): void {
    if (this.connectionState !== state) {
      this.connectionState = state;
      console.log('Connection state changed:', state);
      
      if (this.onConnectionStateChange) {
        this.onConnectionStateChange(state);
      }
    }
  }
  
  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000); // Exponential backoff, max 30s
    
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (this.connectionState !== ConnectionState.Connected) {
        this.connect();
      }
    }, delay);
  }
  
  /**
   * Setup reconnect timer for periodic connection checks
   */
  private setupReconnectTimer(): void {
    this.reconnectInterval = window.setInterval(() => {
      if (this.connectionState !== ConnectionState.Connected) {
        this.connect();
      }
    }, 10000); // Check every 10 seconds
  }
  
  /**
   * Public getters and setters
   */
  public get isConnected(): boolean {
    return this.connectionState === ConnectionState.Connected;
  }
  
  public get state(): ConnectionState {
    return this.connectionState;
  }
  
  public get settings(): SystemSettings {
    return { ...this.currentSettings };
  }
  
  /**
   * Event listener registration
   */
  public onStateChange(callback: (state: ConnectionState) => void): void {
    this.onConnectionStateChange = callback;
  }
  
  public onDataReceived(callback: (data: MonitorData) => void): void {
    this.onMonitorDataReceived = callback;
  }
  
  public onSettingsChange(callback: (settings: SystemSettings) => void): void {
    this.onSettingsChanged = callback;
  }
  
  /**
   * Cleanup resources
   */
  public destroy(): void {
    this.disconnect();
    this.onConnectionStateChange = null;
    this.onMonitorDataReceived = null;
    this.onSettingsChanged = null;
  }
}
