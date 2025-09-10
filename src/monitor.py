"""
Integrated System Monitor

Combines hardware and GPU monitoring for comprehensive system resource tracking.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from .hardware import HardwareInfo
from .gpu import GPUInfo

class SystemMonitor:
    """
    Integrated system monitor that combines CPU, RAM, disk, and GPU monitoring.
    Provides a unified interface for all system resource monitoring.
    """
    
    def __init__(self, 
                 enable_cpu: bool = True,
                 enable_ram: bool = True,
                 enable_disk: bool = True,
                 enable_gpu: bool = True,
                 enable_vram: bool = True,
                 enable_temperature: bool = True,
                 selected_drives: Optional[List[str]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize integrated system monitoring
        
        Args:
            enable_cpu: Enable CPU utilization monitoring
            enable_ram: Enable RAM usage monitoring
            enable_disk: Enable disk usage monitoring
            enable_gpu: Enable GPU utilization monitoring
            enable_vram: Enable VRAM usage monitoring
            enable_temperature: Enable GPU temperature monitoring
            selected_drives: List of drives to monitor (default: all available)
            logger: Logger instance for output
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize hardware monitoring
        try:
            self.hardware = HardwareInfo(
                enable_cpu=enable_cpu,
                enable_ram=enable_ram,
                enable_disk=enable_disk,
                selected_drives=selected_drives,
                logger=self.logger
            )
            self.hardware_available = True
        except Exception as e:
            self.logger.error(f"Failed to initialize hardware monitoring: {e}")
            self.hardware = None
            self.hardware_available = False
        
        # Initialize GPU monitoring
        try:
            self.gpu = GPUInfo(
                enable_gpu=enable_gpu,
                enable_vram=enable_vram,
                enable_temperature=enable_temperature,
                logger=self.logger
            )
            self.gpu_available = self.gpu.is_available()
        except Exception as e:
            self.logger.error(f"Failed to initialize GPU monitoring: {e}")
            self.gpu = None
            self.gpu_available = False
        
        self.logger.info(f"System Monitor initialized - Hardware: {'✓' if self.hardware_available else '✗'}, "
                        f"GPU: {'✓' if self.gpu_available else '✗'}")
    
    def get_full_status(self) -> Dict[str, Any]:
        """
        Get complete system status including all monitoring data
        
        Returns:
            Dict containing all system resource information
        """
        status = {
            'timestamp': time.time(),
            'monitoring_status': {
                'hardware_available': self.hardware_available,
                'gpu_available': self.gpu_available
            }
        }
        
        # Add hardware information
        if self.hardware_available and self.hardware:
            try:
                hardware_status = self.hardware.get_status()
                status.update(hardware_status)
            except Exception as e:
                self.logger.error(f"Error getting hardware status: {e}")
                # Add error fields
                status.update({
                    'cpu_utilization': -1,
                    'ram_total': -1,
                    'ram_used': -1,
                    'ram_used_percent': -1,
                    'hdd_total': -1,
                    'hdd_used': -1,
                    'hdd_used_percent': -1
                })
        else:
            # Add default values when hardware monitoring is unavailable
            status.update({
                'cpu_utilization': -1,
                'ram_total': -1,
                'ram_used': -1,
                'ram_used_percent': -1,
                'hdd_total': -1,
                'hdd_used': -1,
                'hdd_used_percent': -1
            })
        
        # Add GPU information
        if self.gpu_available and self.gpu:
            try:
                gpu_status = self.gpu.get_status()
                
                # Add GPU data to main status
                status['gpu_info'] = gpu_status
                
                # Legacy GPU fields for compatibility
                status['gpu_utilization'] = gpu_status.get('gpu_utilization', -1)
                status['gpu_temperature'] = gpu_status.get('gpu_temperature', -1)
                status['vram_total'] = gpu_status.get('vram_total', -1)
                status['vram_used'] = gpu_status.get('vram_used', -1)
                status['vram_used_percent'] = gpu_status.get('vram_used_percent', -1)
                status['device_type'] = gpu_status.get('device_type', 'cpu')
                
            except Exception as e:
                self.logger.error(f"Error getting GPU status: {e}")
                # Add error fields
                status.update({
                    'gpu_utilization': -1,
                    'gpu_temperature': -1,
                    'vram_total': -1,
                    'vram_used': -1,
                    'vram_used_percent': -1,
                    'device_type': 'cpu'
                })
        else:
            # Add default values when GPU monitoring is unavailable
            status.update({
                'gpu_utilization': -1,
                'gpu_temperature': -1,
                'vram_total': -1,
                'vram_used': -1,
                'vram_used_percent': -1,
                'device_type': 'cpu'
            })
        
        return status
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware-only monitoring information"""
        if self.hardware_available and self.hardware:
            return self.hardware.get_status()
        return {'error': 'Hardware monitoring not available'}
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU-only monitoring information"""
        if self.gpu_available and self.gpu:
            return self.gpu.get_status()
        return {'error': 'GPU monitoring not available'}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        if self.hardware_available and self.hardware:
            return self.hardware.get_system_info()
        return {'error': 'System information not available'}
    
    def get_available_drives(self) -> List[str]:
        """Get list of available disk drives"""
        if self.hardware_available and self.hardware:
            return self.hardware.get_available_drives()
        return []
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """
        Update monitoring configuration
        
        Args:
            config: Dictionary with configuration updates
        """
        # Update hardware configuration
        if self.hardware_available and self.hardware:
            hardware_config = {
                k: v for k, v in config.items() 
                if k in ['enable_cpu', 'enable_ram', 'enable_disk', 'selected_drives']
            }
            if hardware_config:
                self.hardware.update_configuration(hardware_config)
        
        # Update GPU configuration
        if self.gpu and self.gpu:
            gpu_config = {
                k: v for k, v in config.items() 
                if k in ['enable_gpu', 'enable_vram', 'enable_temperature']
            }
            if gpu_config:
                self.gpu.update_configuration(gpu_config)
        
        self.logger.info("System monitor configuration updated")
    
    def is_healthy(self) -> bool:
        """Check if monitoring is working properly"""
        return self.hardware_available or self.gpu_available
    
    def get_monitoring_capabilities(self) -> Dict[str, Any]:
        """Get information about available monitoring capabilities"""
        capabilities = {
            'hardware_monitoring': self.hardware_available,
            'gpu_monitoring': self.gpu_available,
            'features': {
                'cpu': self.hardware_available,
                'ram': self.hardware_available,
                'disk': self.hardware_available,
                'gpu_utilization': self.gpu_available,
                'vram': self.gpu_available,
                'gpu_temperature': self.gpu_available
            }
        }
        
        if self.gpu and self.gpu_available:
            gpu_info = self.gpu.get_gpu_info()
            capabilities['gpu_details'] = {
                'gpu_count': gpu_info.get('gpu_count', 0),
                'cuda_available': gpu_info.get('cuda_available', False),
                'torch_available': gpu_info.get('torch_available', False),
                'pynvml_available': gpu_info.get('pynvml_available', False)
            }
        
        if self.hardware and self.hardware_available:
            capabilities['available_drives'] = self.get_available_drives()
        
        return capabilities
    
    def close(self):
        """Clean up monitoring resources"""
        if self.gpu:
            try:
                self.gpu.close()
            except Exception as e:
                self.logger.warning(f"Error closing GPU monitor: {e}")
        
        self.logger.info("System monitor closed")

# For backward compatibility
CSystemMonitor = SystemMonitor
