"""
Hardware Information Classes

Adapted from ComfyUI-Crystools for the System Resource Monitor.
Provides comprehensive system monitoring capabilities for CPU, RAM, 
and disk usage without GPU dependencies.
"""

import os
import platform
import re
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

try:
    import cpuinfo
    from cpuinfo import DataSource
except ImportError:
    cpuinfo = None
    DataSource = None

class HardwareInfo:
    """
    Main hardware information class for system monitoring.
    Provides CPU, RAM, and disk monitoring capabilities.
    """
    
    def __init__(self, 
                 enable_cpu: bool = True,
                 enable_ram: bool = True, 
                 enable_disk: bool = True,
                 selected_drives: Optional[List[str]] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize hardware monitoring
        
        Args:
            enable_cpu: Enable CPU utilization monitoring
            enable_ram: Enable RAM usage monitoring
            enable_disk: Enable disk usage monitoring
            selected_drives: List of drives to monitor (default: all available)
            logger: Logger instance for output
        """
        # Check for required dependencies
        if psutil is None:
            raise ImportError("psutil is required for hardware monitoring. Install it with: pip install psutil")
        
        self.enable_cpu = enable_cpu
        self.enable_ram = enable_ram
        self.enable_disk = enable_disk
        self.selected_drives = selected_drives or []
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize system information
        self._system_info = self._get_system_info()
        self.logger.info(f"Hardware Monitor initialized: {self._system_info['summary']}")
        
        # Auto-detect drives if none specified
        if self.enable_disk and not self.selected_drives:
            self.selected_drives = self._get_available_drives()
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get comprehensive system information"""
        
        # Get CPU brand information
        cpu_brand = self._get_cpu_brand()
        
        # Get architecture information
        try:
            if DataSource is not None:
                arch_string = DataSource.arch_string_raw
            else:
                arch_string = platform.machine()
        except:
            arch_string = platform.machine()
        
        # Get OS information
        os_info = f"{platform.system()} {platform.release()}"
        
        # Get additional system details
        total_ram = psutil.virtual_memory().total
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)
        
        system_info = {
            'cpu_brand': cpu_brand,
            'architecture': arch_string,
            'os': os_info,
            'cpu_cores_physical': cpu_count,
            'cpu_cores_logical': cpu_count_logical,
            'total_ram_gb': round(total_ram / (1024**3), 2),
            'total_ram_bytes': total_ram,
            'summary': f"CPU: {cpu_brand} | Arch: {arch_string} | OS: {os_info}"
        }
        
        return system_info
    
    def _get_cpu_brand(self) -> str:
        """Get CPU brand string using multiple detection methods"""
        brand = None
        
        # Only use cpuinfo methods if available
        if DataSource is not None:
            # Windows detection
            if DataSource.is_windows:
                try:
                    brand = DataSource.winreg_processor_brand().strip()
                except:
                    pass
            
            # Linux detection
            elif DataSource.has_proc_cpuinfo():
                try:
                    return_code, output = DataSource.cat_proc_cpuinfo()
                    if return_code == 0 and output:
                        for line in output.splitlines():
                            match = re.search(r'model name\s*:\s*(.+)', line)
                            if match:
                                brand = match.group(1)
                                break
                except:
                    pass
            
            # macOS detection
            elif DataSource.has_sysctl():
                try:
                    return_code, output = DataSource.sysctl_machdep_cpu_hw_cpufrequency()
                    if return_code == 0 and output:
                        for line in output.splitlines():
                            match = re.search(r'machdep\.cpu\.brand_string\s*:\s*(.+)', line)
                            if match:
                                brand = match.group(1)
                                break
                except:
                    pass
        
        # Fallback to cpuinfo library if available
        if not brand and cpuinfo is not None:
            try:
                cpu_info = cpuinfo.get_cpu_info()
                brand = cpu_info.get('brand_raw', cpu_info.get('brand', 'Unknown CPU'))
            except:
                brand = 'Unknown CPU'
        
        # Final fallback to platform detection
        if not brand:
            try:
                brand = platform.processor() or 'Unknown CPU'
            except:
                brand = 'Unknown CPU'
        
        return brand or 'Unknown CPU'
    
    def _get_available_drives(self) -> List[str]:
        """Get list of available disk drives/mount points"""
        drives = []
        
        try:
            for partition in psutil.disk_partitions():
                # Skip virtual/special filesystems on Linux
                if platform.system() == 'Linux':
                    # Common virtual filesystems to skip
                    virtual_fs = ['proc', 'sys', 'dev', 'tmpfs', 'devpts', 'sysfs', 'cgroup']
                    if partition.fstype in virtual_fs:
                        continue
                    if partition.mountpoint.startswith(('/proc', '/sys', '/dev')):
                        continue
                
                # Try to access the drive to ensure it's valid
                try:
                    psutil.disk_usage(partition.mountpoint)
                    drives.append(partition.mountpoint)
                except (PermissionError, OSError) as e:
                    self.logger.debug(f"Skipping inaccessible drive {partition.mountpoint}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error detecting drives: {e}")
            # Fallback to common drives based on OS
            if platform.system() == 'Windows':
                drives = ['C:\\']
            else:
                drives = ['/']
        
        self.logger.info(f"Available drives detected: {drives}")
        return drives
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get current CPU utilization and information"""
        if not self.enable_cpu:
            return {'enabled': False}
        
        try:
            # Get CPU percentage (1 second interval for accuracy)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get per-CPU core usage
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            
            # Get CPU frequency information
            try:
                cpu_freq = psutil.cpu_freq()
                cpu_freq_info = {
                    'current': cpu_freq.current if cpu_freq else None,
                    'min': cpu_freq.min if cpu_freq else None,
                    'max': cpu_freq.max if cpu_freq else None
                }
            except:
                cpu_freq_info = {'current': None, 'min': None, 'max': None}
            
            # Get load average (Unix systems only)
            load_avg = None
            try:
                if hasattr(os, 'getloadavg'):
                    load_avg = os.getloadavg()
            except:
                pass
            
            return {
                'enabled': True,
                'utilization_percent': cpu_percent,
                'utilization_per_core': cpu_per_core,
                'cores_physical': self._system_info['cpu_cores_physical'],
                'cores_logical': self._system_info['cpu_cores_logical'],
                'frequency_mhz': cpu_freq_info,
                'load_average': load_avg,
                'brand': self._system_info['cpu_brand']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            return {
                'enabled': True,
                'error': str(e),
                'utilization_percent': -1
            }
    
    def get_ram_info(self) -> Dict[str, Any]:
        """Get current RAM usage information"""
        if not self.enable_ram:
            return {'enabled': False}
        
        try:
            # Get virtual memory information
            ram = psutil.virtual_memory()
            
            # Get swap information
            swap = psutil.swap_memory()
            
            return {
                'enabled': True,
                'total_bytes': ram.total,
                'used_bytes': ram.used,
                'available_bytes': ram.available,
                'free_bytes': ram.free,
                'used_percent': ram.percent,
                'cached_bytes': getattr(ram, 'cached', 0),
                'buffers_bytes': getattr(ram, 'buffers', 0),
                'swap': {
                    'total_bytes': swap.total,
                    'used_bytes': swap.used,
                    'free_bytes': swap.free,
                    'used_percent': swap.percent
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting RAM info: {e}")
            return {
                'enabled': True,
                'error': str(e),
                'total_bytes': -1,
                'used_bytes': -1,
                'used_percent': -1
            }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information for all monitored drives"""
        if not self.enable_disk:
            return {'enabled': False}
        
        drives_info = {}
        total_disk_info = {
            'total_bytes': 0,
            'used_bytes': 0,
            'free_bytes': 0,
            'used_percent': 0
        }
        
        for drive in self.selected_drives:
            try:
                disk_usage = psutil.disk_usage(drive)
                
                # Get additional disk information
                disk_info = {
                    'path': drive,
                    'total_bytes': disk_usage.total,
                    'used_bytes': disk_usage.used,
                    'free_bytes': disk_usage.free,
                    'used_percent': (disk_usage.used / disk_usage.total) * 100
                }
                
                # Try to get filesystem type
                try:
                    for partition in psutil.disk_partitions():
                        if partition.mountpoint == drive:
                            disk_info['filesystem'] = partition.fstype
                            disk_info['device'] = partition.device
                            break
                except:
                    pass
                
                drives_info[drive] = disk_info
                
                # Add to totals
                total_disk_info['total_bytes'] += disk_usage.total
                total_disk_info['used_bytes'] += disk_usage.used
                total_disk_info['free_bytes'] += disk_usage.free
                
            except Exception as e:
                self.logger.error(f"Error getting disk info for {drive}: {e}")
                drives_info[drive] = {
                    'path': drive,
                    'error': str(e),
                    'total_bytes': -1,
                    'used_bytes': -1,
                    'used_percent': -1
                }
        
        # Calculate overall percentage
        if total_disk_info['total_bytes'] > 0:
            total_disk_info['used_percent'] = (
                total_disk_info['used_bytes'] / total_disk_info['total_bytes']
            ) * 100
        
        return {
            'enabled': True,
            'drives': drives_info,
            'total': total_disk_info,
            'monitored_drives': self.selected_drives
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return self._system_info.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete hardware status information
        
        Returns:
            Dict containing all hardware monitoring data
        """
        status = {
            'timestamp': time.time(),
            'boot_time': psutil.boot_time(),
            'uptime_seconds': time.time() - psutil.boot_time(),
            'system': self.get_system_info()
        }
        
        # Add CPU information
        if self.enable_cpu:
            cpu_info = self.get_cpu_info()
            status['cpu'] = cpu_info
            # Legacy field for compatibility
            status['cpu_utilization'] = cpu_info.get('utilization_percent', -1)
        else:
            status['cpu_utilization'] = -1
        
        # Add RAM information
        if self.enable_ram:
            ram_info = self.get_ram_info()
            status['ram'] = ram_info
            # Legacy fields for compatibility
            status['ram_total'] = ram_info.get('total_bytes', -1)
            status['ram_used'] = ram_info.get('used_bytes', -1)
            status['ram_used_percent'] = ram_info.get('used_percent', -1)
        else:
            status['ram_total'] = -1
            status['ram_used'] = -1
            status['ram_used_percent'] = -1
        
        # Add disk information
        if self.enable_disk:
            disk_info = self.get_disk_info()
            status['disk'] = disk_info
            # Legacy fields for compatibility (use totals)
            total = disk_info.get('total', {})
            status['hdd_total'] = total.get('total_bytes', -1)
            status['hdd_used'] = total.get('used_bytes', -1)
            status['hdd_used_percent'] = total.get('used_percent', -1)
        else:
            status['hdd_total'] = -1
            status['hdd_used'] = -1
            status['hdd_used_percent'] = -1
        
        return status
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """
        Update monitoring configuration
        
        Args:
            config: Dictionary with configuration updates
        """
        if 'enable_cpu' in config:
            self.enable_cpu = config['enable_cpu']
        
        if 'enable_ram' in config:
            self.enable_ram = config['enable_ram']
        
        if 'enable_disk' in config:
            self.enable_disk = config['enable_disk']
        
        if 'selected_drives' in config:
            self.selected_drives = config['selected_drives']
            if self.enable_disk and not self.selected_drives:
                self.selected_drives = self._get_available_drives()
        
        self.logger.info(f"Hardware monitoring configuration updated")
    
    def get_available_drives(self) -> List[str]:
        """Public method to get available drives"""
        return self._get_available_drives()

# For backward compatibility with original ComfyUI-Crystools code
CHardwareInfo = HardwareInfo
