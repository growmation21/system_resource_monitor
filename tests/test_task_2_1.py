"""
Test for Task 2.1: Hardware Information Classes

This test verifies that the hardware monitoring classes are working correctly
and can collect system information without external dependencies.
"""

import sys
import logging
from pathlib import Path
import asyncio
import time

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_hardware_info():
    """Test the HardwareInfo class"""
    print("🔧 Testing HardwareInfo class...")
    
    try:
        from src.hardware import HardwareInfo
        
        # Create logger
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('test_hardware')
        
        # Test initialization
        hardware = HardwareInfo(logger=logger)
        print("✅ HardwareInfo initialized successfully")
        
        # Test system info
        system_info = hardware.get_system_info()
        print(f"✅ System Info: {system_info['summary']}")
        
        # Test CPU info
        cpu_info = hardware.get_cpu_info()
        print(f"✅ CPU Info: {cpu_info.get('utilization_percent', 'N/A')}% utilization")
        
        # Test RAM info
        ram_info = hardware.get_ram_info()
        if ram_info.get('enabled'):
            print(f"✅ RAM Info: {ram_info.get('used_percent', 'N/A')}% used ({ram_info.get('used_bytes', 0) // (1024**3)}GB/{ram_info.get('total_bytes', 0) // (1024**3)}GB)")
        
        # Test disk info
        disk_info = hardware.get_disk_info()
        if disk_info.get('enabled'):
            total = disk_info.get('total', {})
            print(f"✅ Disk Info: {total.get('used_percent', 'N/A')}% used")
        
        # Test full status
        status = hardware.get_status()
        print(f"✅ Full Status: {len(status)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ HardwareInfo test failed: {e}")
        return False

def test_gpu_info():
    """Test the GPUInfo class"""
    print("\n🎮 Testing GPUInfo class...")
    
    try:
        from src.gpu import GPUInfo
        
        # Create logger
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('test_gpu')
        
        # Test initialization
        gpu = GPUInfo(logger=logger)
        print("✅ GPUInfo initialized successfully")
        
        # Test GPU info
        gpu_info = gpu.get_gpu_info()
        print(f"✅ GPU Info: {gpu_info.get('gpu_count', 0)} GPU(s) detected")
        print(f"   - PyTorch available: {gpu_info.get('torch_available', False)}")
        print(f"   - CUDA available: {gpu_info.get('cuda_available', False)}")
        print(f"   - pynvml available: {gpu_info.get('pynvml_available', False)}")
        
        # Test status
        status = gpu.get_status()
        print(f"✅ GPU Status: Device type = {status.get('device_type', 'unknown')}")
        
        # Clean up
        gpu.close()
        
        return True
        
    except Exception as e:
        print(f"❌ GPUInfo test failed: {e}")
        return False

def test_system_monitor():
    """Test the integrated SystemMonitor class"""
    print("\n🖥️ Testing SystemMonitor class...")
    
    try:
        from src.monitor import SystemMonitor
        
        # Create logger
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('test_monitor')
        
        # Test initialization
        monitor = SystemMonitor(logger=logger)
        print("✅ SystemMonitor initialized successfully")
        
        # Test capabilities
        capabilities = monitor.get_monitoring_capabilities()
        print(f"✅ Monitoring Capabilities:")
        for feature, available in capabilities.get('features', {}).items():
            status = "✅" if available else "❌"
            print(f"   {status} {feature}")
        
        # Test full status
        print("\n📊 Getting system status...")
        status = monitor.get_full_status()
        
        # Display key metrics
        if 'cpu_utilization' in status and status['cpu_utilization'] != -1:
            print(f"✅ CPU: {status['cpu_utilization']:.1f}%")
        
        if 'ram_used_percent' in status and status['ram_used_percent'] != -1:
            print(f"✅ RAM: {status['ram_used_percent']:.1f}%")
        
        if 'hdd_used_percent' in status and status['hdd_used_percent'] != -1:
            print(f"✅ Disk: {status['hdd_used_percent']:.1f}%")
        
        if 'gpu_utilization' in status and status['gpu_utilization'] != -1:
            print(f"✅ GPU: {status['gpu_utilization']:.1f}%")
        
        print(f"✅ System monitoring healthy: {monitor.is_healthy()}")
        
        # Clean up
        monitor.close()
        
        return True
        
    except Exception as e:
        print(f"❌ SystemMonitor test failed: {e}")
        return False

def test_server_integration():
    """Test server integration with monitoring"""
    print("\n🌐 Testing server integration...")
    
    try:
        from src.config import load_config
        from src.logger import setup_logger
        from src.server import SystemMonitorServer
        
        # Load configuration
        config = load_config()
        logger = setup_logger(config.logging)
        
        # Create server (this should initialize monitoring)
        server = SystemMonitorServer(config, logger)
        print("✅ Server created with monitoring integration")
        
        # Check if monitoring is available
        if server.system_monitor:
            print("✅ System monitor integrated successfully")
            
            # Test getting status through server
            if hasattr(server.system_monitor, 'get_full_status'):
                status = server.system_monitor.get_full_status()
                print(f"✅ Status retrieval working: {len(status)} fields")
            
            # Clean up
            server.system_monitor.close()
        else:
            print("⚠️ System monitor not available in server")
        
        return True
        
    except Exception as e:
        print(f"❌ Server integration test failed: {e}")
        return False

def main():
    """Run all tests for Task 2.1"""
    print("=" * 60)
    print("🧪 TASK 2.1 TESTING: Hardware Information Classes")
    print("=" * 60)
    
    tests = [
        test_hardware_info,
        test_gpu_info,
        test_system_monitor,
        test_server_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TASK 2.1 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Task 2.1 completed successfully!")
        print("✅ Hardware monitoring classes are working correctly")
        print("✅ System integration is functional")
        return True
    else:
        print("⚠️ Some tests failed - check dependencies")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
