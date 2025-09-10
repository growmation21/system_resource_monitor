"""
Configuration management for System Resource Monitor

Handles loading and managing application settings from JSON files
with fallback defaults and validation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Union
from dataclasses import dataclass, asdict, field

@dataclass
class ServerConfig:
    """Server configuration settings"""
    host: str = 'localhost'
    port: int = 8888
    cors_origins: list = field(default_factory=lambda: ['*'])
    static_path: str = '/static'
    websocket_path: str = '/ws'

@dataclass
class MonitoringConfig:
    """Hardware monitoring configuration"""
    refresh_rate: float = 5.0  # seconds
    enable_cpu: bool = True
    enable_ram: bool = True
    enable_disk: bool = True
    enable_gpu: bool = True
    enable_vram: bool = True
    enable_temperature: bool = True
    selected_drives: list = field(default_factory=lambda: ['C:\\'])
    gpu_indices: list = field(default_factory=list)  # Empty = all GPUs

@dataclass
class UIConfig:
    """User interface configuration"""
    width: int = 300
    height: int = 200
    always_on_top: bool = True
    position_x: int = 100
    position_y: int = 100
    opacity: float = 0.9
    theme: str = 'dark'
    show_tooltips: bool = True

@dataclass
class AppConfig:
    """General application configuration"""
    auto_open_browser: bool = True
    auto_start_monitoring: bool = True
    minimize_to_tray: bool = False
    check_for_updates: bool = True
    save_settings_on_exit: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    log_to_file: bool = True
    log_to_console: bool = True

class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: Union[str, Path] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        
        # Initialize with defaults
        self.server = ServerConfig()
        self.monitoring = MonitoringConfig()
        self.ui = UIConfig()
        self.app = AppConfig()
        self.logging = LoggingConfig()
        
        # Load from file if it exists
        self.load()
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path"""
        return Path(__file__).parent.parent / 'config' / 'settings.json'
    
    def load(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not self.config_path.exists():
            logging.info(f"Config file not found: {self.config_path}, using defaults")
            self.save()  # Create default config file
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update configurations with loaded data
            if 'server' in data:
                self.server = ServerConfig(**data['server'])
            if 'monitoring' in data:
                self.monitoring = MonitoringConfig(**data['monitoring'])
            if 'ui' in data:
                self.ui = UIConfig(**data['ui'])
            if 'app' in data:
                self.app = AppConfig(**data['app'])
            if 'logging' in data:
                self.logging = LoggingConfig(**data['logging'])
            
            logging.info(f"Configuration loaded from: {self.config_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            logging.info("Using default configuration")
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary
            data = {
                'server': asdict(self.server),
                'monitoring': asdict(self.monitoring),
                'ui': asdict(self.ui),
                'app': asdict(self.app),
                'logging': asdict(self.logging)
            }
            
            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Configuration saved to: {self.config_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            return False
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary
        
        Args:
            data: Dictionary with configuration updates
        """
        if 'server' in data:
            for key, value in data['server'].items():
                if hasattr(self.server, key):
                    setattr(self.server, key, value)
        
        if 'monitoring' in data:
            for key, value in data['monitoring'].items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
        
        if 'ui' in data:
            for key, value in data['ui'].items():
                if hasattr(self.ui, key):
                    setattr(self.ui, key, value)
        
        if 'app' in data:
            for key, value in data['app'].items():
                if hasattr(self.app, key):
                    setattr(self.app, key, value)
        
        if 'logging' in data:
            for key, value in data['logging'].items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dict: Configuration as dictionary
        """
        return {
            'server': asdict(self.server),
            'monitoring': asdict(self.monitoring),
            'ui': asdict(self.ui),
            'app': asdict(self.app),
            'logging': asdict(self.logging)
        }
    
    def validate(self) -> bool:
        """
        Validate configuration values
        
        Returns:
            bool: True if configuration is valid
        """
        # Server validation
        if not (1 <= self.server.port <= 65535):
            logging.error(f"Invalid server port: {self.server.port}")
            return False
        
        # Monitoring validation
        if not (0.1 <= self.monitoring.refresh_rate <= 300):
            logging.error(f"Invalid refresh rate: {self.monitoring.refresh_rate}")
            return False
        
        # UI validation
        if not (100 <= self.ui.width <= 2000):
            logging.warning(f"UI width {self.ui.width} may be out of range")
        
        if not (50 <= self.ui.height <= 1500):
            logging.warning(f"UI height {self.ui.height} may be out of range")
        
        if not (0.1 <= self.ui.opacity <= 1.0):
            logging.error(f"Invalid opacity: {self.ui.opacity}")
            return False
        
        return True


def load_config(config_path: Union[str, Path] = None) -> Config:
    """
    Load configuration from file or create default
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Config: Loaded configuration object
    """
    return Config(config_path)
