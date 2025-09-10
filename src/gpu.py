"""
GPU Information Classes

Adapted from ComfyUI-Crystools for the System Resource Monitor.
Provides GPU monitoring capabilities with optional dependencies.
"""

import logging
import platform
from typing import Dict, List, Any, Optional

try:
    import torch
except ImportError:
    torch = None

try:
    import pynvml
except ImportError:
    pynvml = None

class GPUInfo:
    """
    GPU monitoring class that handles NVIDIA GPUs via pynvml.
    Gracefully handles missing dependencies and provides fallback information.
    """
    
    def __init__(self, 
                 enable_gpu: bool = True,
                 enable_vram: bool = True,
                 enable_temperature: bool = True,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize GPU monitoring
        
        Args:
            enable_gpu: Enable GPU utilization monitoring
            enable_vram: Enable VRAM usage monitoring  
            enable_temperature: Enable GPU temperature monitoring
            logger: Logger instance for output
        """
        self.enable_gpu = enable_gpu
        self.enable_vram = enable_vram
        self.enable_temperature = enable_temperature
        self.logger = logger or logging.getLogger(__name__)
        
        # GPU monitoring state
        self.pynvml_loaded = False
        self.torch_available = False
        self.cuda_available = False
        self.gpu_count = 0
        self.gpus = []
        
        # Error tracking to prevent spam
        self.gpu_error_logged = False
        self.vram_error_logged = False
        self.temp_error_logged = False
        
        self._initialize_gpu_monitoring()
    
    def _initialize_gpu_monitoring(self):
        """Initialize GPU monitoring libraries and detect available GPUs"""
        
        # Check PyTorch availability
        if torch is not None:
            self.torch_available = True
            try:
                self.cuda_available = torch.cuda.is_available()
                if self.cuda_available:
                    self.logger.info(f"PyTorch CUDA available: {torch.version.cuda}")
                else:
                    self.logger.info("PyTorch available but CUDA not detected")
            except Exception as e:
                self.logger.warning(f"Error checking PyTorch CUDA: {e}")
        else:
            self.logger.info("PyTorch not available")
        
        # Check pynvml availability
        if pynvml is not None:
            try:
                pynvml.nvmlInit()
                self.pynvml_loaded = True
                self.gpu_count = pynvml.nvmlDeviceGetCount()
                self.logger.info(f"pynvml initialized, {self.gpu_count} GPU(s) detected")
                
                # Get GPU information
                for i in range(self.gpu_count):
                    try:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        name = pynvml.nvmlDeviceGetName(handle)
                        
                        # Handle bytes vs string for different pynvml versions
                        if isinstance(name, bytes):
                            name = name.decode('utf-8')
                        
                        gpu_info = {
                            'index': i,
                            'name': name,
                            'handle': handle
                        }
                        self.gpus.append(gpu_info)
                        self.logger.info(f"GPU {i}: {name}")
                        
                    except Exception as e:
                        self.logger.error(f"Error getting info for GPU {i}: {e}")
                
                # Get driver version
                try:
                    driver_version = pynvml.nvmlSystemGetDriverVersion()
                    if isinstance(driver_version, bytes):
                        driver_version = driver_version.decode('utf-8')
                    self.logger.info(f"NVIDIA Driver: {driver_version}")
                except Exception as e:
                    self.logger.warning(f"Could not get driver version: {e}")
                    
            except Exception as e:
                self.logger.warning(f"Could not initialize pynvml: {e}")
        else:
            self.logger.info("pynvml not available (install with: pip install pynvml)")
        
        # Overall status
        if not self.pynvml_loaded and not self.cuda_available:
            self.logger.info("No GPU monitoring available")
        elif self.gpu_count == 0:
            self.logger.info("No NVIDIA GPUs detected")
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get basic GPU information"""
        return {
            'enabled': self.enable_gpu,
            'pynvml_available': self.pynvml_loaded,
            'torch_available': self.torch_available,
            'cuda_available': self.cuda_available,
            'gpu_count': self.gpu_count,
            'gpus': [{'index': gpu['index'], 'name': gpu['name']} for gpu in self.gpus]
        }
    
    def get_gpu_utilization(self, gpu_index: int = 0) -> float:
        """Get GPU utilization percentage for specified GPU"""
        if not self.enable_gpu or not self.pynvml_loaded or gpu_index >= len(self.gpus):
            return -1
        
        try:
            handle = self.gpus[gpu_index]['handle']
            util_rates = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return util_rates.gpu
        except Exception as e:
            if not self.gpu_error_logged:
                self.logger.error(f"Error getting GPU utilization: {e}")
                self.gpu_error_logged = True
            return -1
    
    def get_vram_info(self, gpu_index: int = 0) -> Dict[str, Any]:
        """Get VRAM usage information for specified GPU"""
        if not self.enable_vram or not self.pynvml_loaded or gpu_index >= len(self.gpus):
            return {
                'enabled': self.enable_vram,
                'total_bytes': -1,
                'used_bytes': -1,
                'free_bytes': -1,
                'used_percent': -1
            }
        
        try:
            handle = self.gpus[gpu_index]['handle']
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            total = mem_info.total
            used = mem_info.used
            free = mem_info.free
            used_percent = (used / total) * 100 if total > 0 else 0
            
            return {
                'enabled': True,
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'used_percent': used_percent
            }
            
        except Exception as e:
            if not self.vram_error_logged:
                self.logger.error(f"Error getting VRAM info: {e}")
                self.vram_error_logged = True
            return {
                'enabled': True,
                'error': str(e),
                'total_bytes': -1,
                'used_bytes': -1,
                'free_bytes': -1,
                'used_percent': -1
            }
    
    def get_gpu_temperature(self, gpu_index: int = 0) -> float:
        """Get GPU temperature in Celsius for specified GPU"""
        if not self.enable_temperature or not self.pynvml_loaded or gpu_index >= len(self.gpus):
            return -1
        
        try:
            handle = self.gpus[gpu_index]['handle']
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            return temp
        except Exception as e:
            if not self.temp_error_logged:
                self.logger.error(f"Error getting GPU temperature: {e}")
                self.temp_error_logged = True
            return -1
    
    def get_all_gpus_status(self) -> List[Dict[str, Any]]:
        """Get status information for all available GPUs"""
        gpus_status = []
        
        if not self.pynvml_loaded or self.gpu_count == 0:
            # Return CPU fallback
            return [{
                'index': -1,
                'name': 'CPU',
                'gpu_utilization': -1,
                'gpu_temperature': -1,
                'vram_total': -1,
                'vram_used': -1,
                'vram_used_percent': -1,
                'device_type': 'cpu'
            }]
        
        for i, gpu in enumerate(self.gpus):
            utilization = self.get_gpu_utilization(i)
            vram_info = self.get_vram_info(i)
            temperature = self.get_gpu_temperature(i)
            
            gpu_status = {
                'index': i,
                'name': gpu['name'],
                'gpu_utilization': utilization,
                'gpu_temperature': temperature,
                'vram_total': vram_info.get('total_bytes', -1),
                'vram_used': vram_info.get('used_bytes', -1),
                'vram_used_percent': vram_info.get('used_percent', -1),
                'device_type': 'cuda'
            }
            
            gpus_status.append(gpu_status)
        
        return gpus_status
    
    def get_device_type(self) -> str:
        """Get the device type (cpu/cuda)"""
        if self.cuda_available and self.gpu_count > 0:
            return 'cuda'
        return 'cpu'
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete GPU status information
        
        Returns:
            Dict containing all GPU monitoring data
        """
        gpus_status = self.get_all_gpus_status()
        device_type = self.get_device_type()
        
        # Legacy compatibility - use first GPU for legacy fields
        first_gpu = gpus_status[0] if gpus_status else {}
        
        status = {
            'device_type': device_type,
            'gpus': gpus_status,
            'gpu_count': self.gpu_count,
            'pynvml_available': self.pynvml_loaded,
            'torch_available': self.torch_available,
            'cuda_available': self.cuda_available,
            
            # Legacy fields for compatibility
            'gpu_utilization': first_gpu.get('gpu_utilization', -1),
            'gpu_temperature': first_gpu.get('gpu_temperature', -1),
            'vram_total': first_gpu.get('vram_total', -1),
            'vram_used': first_gpu.get('vram_used', -1),
            'vram_used_percent': first_gpu.get('vram_used_percent', -1)
        }
        
        return status
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """
        Update GPU monitoring configuration
        
        Args:
            config: Dictionary with configuration updates
        """
        if 'enable_gpu' in config:
            self.enable_gpu = config['enable_gpu']
        
        if 'enable_vram' in config:
            self.enable_vram = config['enable_vram']
        
        if 'enable_temperature' in config:
            self.enable_temperature = config['enable_temperature']
        
        # Reset error flags when re-enabling features
        self.gpu_error_logged = False
        self.vram_error_logged = False
        self.temp_error_logged = False
        
        self.logger.info("GPU monitoring configuration updated")
    
    def is_available(self) -> bool:
        """Check if any GPU monitoring is available"""
        return self.pynvml_loaded and self.gpu_count > 0
    
    def close(self):
        """Clean up GPU monitoring resources"""
        if self.pynvml_loaded:
            try:
                pynvml.nvmlShutdown()
                self.logger.info("pynvml shutdown")
            except Exception as e:
                self.logger.warning(f"Error shutting down pynvml: {e}")

# For backward compatibility with original ComfyUI-Crystools code
CGPUInfo = GPUInfo
