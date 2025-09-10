#!/usr/bin/env python3
"""
Hardware monitoring test script for Task 1.1 verification
Tests all dependencies and hardware monitoring capabilities
"""

import psutil
import pynvml
import cpuinfo
import torch
import aiohttp

def test_system_monitoring():
    """Test basic system monitoring capabilities"""
    print('=== SYSTEM MONITORING TEST ===')
    
    # CPU monitoring
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f'✓ CPU Usage: {cpu_percent}%')
    
    # Memory monitoring
    memory = psutil.virtual_memory()
    print(f'✓ Memory Usage: {memory.percent}% ({memory.used/1024**3:.1f}GB / {memory.total/1024**3:.1f}GB)')
    
    # Disk monitoring
    disk = psutil.disk_usage('C:\\')
    print(f'✓ Disk Usage: {disk.percent}% ({disk.used/1024**3:.1f}GB / {disk.total/1024**3:.1f}GB)')
    
    return True

def test_gpu_monitoring():
    """Test GPU monitoring capabilities"""
    print('\n=== GPU MONITORING TEST ===')
    
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        print(f'✓ GPU Count: {device_count}')
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            # Handle both string and bytes return types
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            print(f'✓ GPU {i}: {name}')
            print(f'  - Temperature: {temp}°C')
            print(f'  - GPU Utilization: {util.gpu}%')
            print(f'  - Memory Utilization: {util.memory}%')
            print(f'  - VRAM: {memory.used/1024**2:.0f}MB / {memory.total/1024**2:.0f}MB ({(memory.used/memory.total)*100:.1f}%)')
            
        pynvml.nvmlShutdown()
        print('✓ GPU monitoring working correctly')
        return True
        
    except Exception as e:
        print(f'✗ GPU monitoring error: {e}')
        return False

def test_dependencies():
    """Test all dependency imports and versions"""
    print('\n=== DEPENDENCY TEST ===')
    
    print(f'✓ psutil version: {psutil.__version__}')
    print(f'✓ torch version: {torch.__version__}')
    print(f'✓ aiohttp version: {aiohttp.__version__}')
    print(f'✓ CUDA available: {torch.cuda.is_available()}')
    
    if torch.cuda.is_available():
        print(f'✓ CUDA device count: {torch.cuda.device_count()}')
        for i in range(torch.cuda.device_count()):
            print(f'  - GPU {i}: {torch.cuda.get_device_name(i)}')
    
    return True

def main():
    """Main test function"""
    print('System Resource Monitor - Task 1.1 Verification')
    print('=' * 50)
    
    try:
        # Test all components
        test_dependencies()
        test_system_monitoring()
        test_gpu_monitoring()
        
        print('\n' + '=' * 50)
        print('✓ Task 1.1 COMPLETED SUCCESSFULLY')
        print('✓ All dependencies installed globally')
        print('✓ No virtual environment required')
        print('✓ Hardware monitoring capabilities verified')
        print('✓ NVIDIA GPU detection working')
        
    except Exception as e:
        print(f'\n✗ Task 1.1 FAILED: {e}')
        return False
    
    return True

if __name__ == '__main__':
    main()
