#!/usr/bin/env python3
"""
Unit Tests for System Resource Monitor - Task 7.1
Hardware Monitoring Classes Testing

This module provides comprehensive unit tests for all hardware monitoring
components including CPU, memory, disk, and GPU monitoring functionality.
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from back_end import hardware, gpu, hdd

class TestHardwareMonitoring(unittest.TestCase):
    """Test cases for hardware monitoring functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.hardware_monitor = hardware.HardwareMonitor()
        self.gpu_monitor = gpu.GPUMonitor()
        self.hdd_monitor = hdd.HDDMonitor()
    
    def test_hardware_monitor_initialization(self):
        """Test HardwareMonitor class initialization"""
        self.assertIsNotNone(self.hardware_monitor)
        self.assertTrue(hasattr(self.hardware_monitor, 'get_system_info'))
        self.assertTrue(hasattr(self.hardware_monitor, 'get_cpu_info'))
        self.assertTrue(hasattr(self.hardware_monitor, 'get_memory_info'))
    
    def test_cpu_info_structure(self):
        """Test CPU information structure and data types"""
        cpu_info = self.hardware_monitor.get_cpu_info()
        
        self.assertIsInstance(cpu_info, dict)
        self.assertIn('cpu_percent', cpu_info)
        self.assertIn('cpu_count', cpu_info)
        self.assertIn('cpu_freq', cpu_info)
        
        # Validate data types and ranges
        self.assertIsInstance(cpu_info['cpu_percent'], (int, float))
        self.assertGreaterEqual(cpu_info['cpu_percent'], 0)
        self.assertLessEqual(cpu_info['cpu_percent'], 100)
        
        self.assertIsInstance(cpu_info['cpu_count'], int)
        self.assertGreater(cpu_info['cpu_count'], 0)
    
    def test_memory_info_structure(self):
        """Test memory information structure and data types"""
        memory_info = self.hardware_monitor.get_memory_info()
        
        self.assertIsInstance(memory_info, dict)
        self.assertIn('total', memory_info)
        self.assertIn('used', memory_info)
        self.assertIn('available', memory_info)
        self.assertIn('percent', memory_info)
        
        # Validate data types and logical relationships
        self.assertIsInstance(memory_info['total'], int)
        self.assertIsInstance(memory_info['used'], int)
        self.assertIsInstance(memory_info['available'], int)
        self.assertIsInstance(memory_info['percent'], (int, float))
        
        # Logical validations
        self.assertGreater(memory_info['total'], 0)
        self.assertGreaterEqual(memory_info['used'], 0)
        self.assertGreaterEqual(memory_info['available'], 0)
        self.assertLessEqual(memory_info['used'], memory_info['total'])
        self.assertGreaterEqual(memory_info['percent'], 0)
        self.assertLessEqual(memory_info['percent'], 100)
    
    def test_system_info_completeness(self):
        """Test system information completeness"""
        system_info = self.hardware_monitor.get_system_info()
        
        self.assertIsInstance(system_info, dict)
        required_fields = ['platform', 'architecture', 'hostname', 'boot_time']
        
        for field in required_fields:
            self.assertIn(field, system_info, f"Missing required field: {field}")
            self.assertIsNotNone(system_info[field], f"Field {field} is None")


class TestGPUMonitoring(unittest.TestCase):
    """Test cases for GPU monitoring functionality"""
    
    def setUp(self):
        """Set up GPU monitor test fixtures"""
        self.gpu_monitor = gpu.GPUMonitor()
    
    def test_gpu_monitor_initialization(self):
        """Test GPU monitor initialization"""
        self.assertIsNotNone(self.gpu_monitor)
        self.assertTrue(hasattr(self.gpu_monitor, 'get_gpu_info'))
        self.assertTrue(hasattr(self.gpu_monitor, 'is_available'))
    
    def test_gpu_availability_check(self):
        """Test GPU availability detection"""
        is_available = self.gpu_monitor.is_available()
        self.assertIsInstance(is_available, bool)
        
        if is_available:
            # If GPU is available, test GPU info retrieval
            gpu_info = self.gpu_monitor.get_gpu_info()
            self.assertIsInstance(gpu_info, list)
            self.assertGreater(len(gpu_info), 0)
    
    @patch('gpu.pynvml')
    def test_gpu_info_with_mock(self, mock_pynvml):
        """Test GPU info retrieval with mocked NVIDIA libraries"""
        # Mock NVIDIA GPU detection
        mock_pynvml.nvmlInit.return_value = None
        mock_pynvml.nvmlDeviceGetCount.return_value = 2
        
        # Mock GPU device handles
        mock_handle_0 = Mock()
        mock_handle_1 = Mock()
        mock_pynvml.nvmlDeviceGetHandleByIndex.side_effect = [mock_handle_0, mock_handle_1]
        
        # Mock GPU properties
        mock_pynvml.nvmlDeviceGetName.side_effect = [
            b"NVIDIA GeForce RTX 3070",
            b"NVIDIA GeForce RTX 3060"
        ]
        mock_pynvml.nvmlDeviceGetUtilizationRates.side_effect = [
            Mock(gpu=45, memory=60),
            Mock(gpu=25, memory=40)
        ]
        mock_pynvml.nvmlDeviceGetMemoryInfo.side_effect = [
            Mock(total=8589934592, used=4294967296),  # 8GB total, 4GB used
            Mock(total=12884901888, used=2147483648)  # 12GB total, 2GB used
        ]
        mock_pynvml.nvmlDeviceGetTemperature.side_effect = [65, 58]
        
        # Test GPU info retrieval
        gpu_info = self.gpu_monitor.get_gpu_info()
        
        self.assertIsInstance(gpu_info, list)
        self.assertEqual(len(gpu_info), 2)
        
        # Validate first GPU
        gpu_0 = gpu_info[0]
        self.assertEqual(gpu_0['name'], 'NVIDIA GeForce RTX 3070')
        self.assertEqual(gpu_0['gpu_utilization'], 45)
        self.assertEqual(gpu_0['memory_utilization'], 60)
        self.assertEqual(gpu_0['gpu_temperature'], 65)
        
        # Validate second GPU
        gpu_1 = gpu_info[1]
        self.assertEqual(gpu_1['name'], 'NVIDIA GeForce RTX 3060')
        self.assertEqual(gpu_1['gpu_utilization'], 25)
        self.assertEqual(gpu_1['memory_utilization'], 40)
        self.assertEqual(gpu_1['gpu_temperature'], 58)
    
    def test_gpu_info_validation(self):
        """Test GPU info data validation"""
        if self.gpu_monitor.is_available():
            gpu_info = self.gpu_monitor.get_gpu_info()
            
            for i, gpu in enumerate(gpu_info):
                self.assertIsInstance(gpu, dict, f"GPU {i} info is not a dict")
                
                # Required fields
                required_fields = ['name', 'gpu_utilization', 'memory_utilization', 'gpu_temperature']
                for field in required_fields:
                    self.assertIn(field, gpu, f"GPU {i} missing field: {field}")
                
                # Data type validations
                self.assertIsInstance(gpu['name'], str)
                self.assertIsInstance(gpu['gpu_utilization'], (int, float))
                self.assertIsInstance(gpu['memory_utilization'], (int, float))
                self.assertIsInstance(gpu['gpu_temperature'], (int, float))
                
                # Range validations
                self.assertGreaterEqual(gpu['gpu_utilization'], 0)
                self.assertLessEqual(gpu['gpu_utilization'], 100)
                self.assertGreaterEqual(gpu['memory_utilization'], 0)
                self.assertLessEqual(gpu['memory_utilization'], 100)
                self.assertGreater(gpu['gpu_temperature'], 0)
                self.assertLess(gpu['gpu_temperature'], 150)  # Reasonable temperature range


class TestHDDMonitoring(unittest.TestCase):
    """Test cases for HDD/storage monitoring functionality"""
    
    def setUp(self):
        """Set up HDD monitor test fixtures"""
        self.hdd_monitor = hdd.HDDMonitor()
    
    def test_hdd_monitor_initialization(self):
        """Test HDD monitor initialization"""
        self.assertIsNotNone(self.hdd_monitor)
        self.assertTrue(hasattr(self.hdd_monitor, 'get_disk_info'))
        self.assertTrue(hasattr(self.hdd_monitor, 'get_disk_usage'))
    
    def test_disk_info_structure(self):
        """Test disk information structure"""
        disk_info = self.hdd_monitor.get_disk_info()
        
        self.assertIsInstance(disk_info, list)
        self.assertGreater(len(disk_info), 0, "No disk drives detected")
        
        for disk in disk_info:
            self.assertIsInstance(disk, dict)
            self.assertIn('device', disk)
            self.assertIn('mountpoint', disk)
            self.assertIn('fstype', disk)
            
            self.assertIsInstance(disk['device'], str)
            self.assertIsInstance(disk['mountpoint'], str)
            self.assertIsInstance(disk['fstype'], str)
    
    def test_disk_usage_validation(self):
        """Test disk usage data validation"""
        disk_usage = self.hdd_monitor.get_disk_usage()
        
        self.assertIsInstance(disk_usage, dict)
        
        for drive, usage in disk_usage.items():
            self.assertIsInstance(drive, str)
            self.assertIsInstance(usage, dict)
            
            # Required fields
            required_fields = ['total', 'used', 'free', 'percent']
            for field in required_fields:
                self.assertIn(field, usage, f"Drive {drive} missing field: {field}")
            
            # Data type validations
            self.assertIsInstance(usage['total'], int)
            self.assertIsInstance(usage['used'], int)
            self.assertIsInstance(usage['free'], int)
            self.assertIsInstance(usage['percent'], (int, float))
            
            # Logical validations
            self.assertGreater(usage['total'], 0)
            self.assertGreaterEqual(usage['used'], 0)
            self.assertGreaterEqual(usage['free'], 0)
            self.assertLessEqual(usage['used'], usage['total'])
            self.assertGreaterEqual(usage['percent'], 0)
            self.assertLessEqual(usage['percent'], 100)
            
            # Total space should equal used + free (with small tolerance for filesystem overhead)
            calculated_total = usage['used'] + usage['free']
            tolerance = usage['total'] * 0.05  # 5% tolerance
            self.assertAlmostEqual(usage['total'], calculated_total, delta=tolerance)


class TestDataAccuracy(unittest.TestCase):
    """Test data accuracy against system tools and expected values"""
    
    def setUp(self):
        """Set up accuracy test fixtures"""
        self.hardware_monitor = hardware.HardwareMonitor()
        self.gpu_monitor = gpu.GPUMonitor()
        self.hdd_monitor = hdd.HDDMonitor()
    
    @patch('psutil.cpu_percent')
    def test_cpu_accuracy_with_mock(self, mock_cpu_percent):
        """Test CPU monitoring accuracy with controlled data"""
        # Mock specific CPU percentage
        mock_cpu_percent.return_value = 45.5
        
        cpu_info = self.hardware_monitor.get_cpu_info()
        self.assertEqual(cpu_info['cpu_percent'], 45.5)
    
    def test_memory_consistency(self):
        """Test memory data consistency over multiple readings"""
        readings = []
        for _ in range(3):
            memory_info = self.hardware_monitor.get_memory_info()
            readings.append(memory_info)
            time.sleep(0.1)
        
        # Memory total should be consistent
        totals = [reading['total'] for reading in readings]
        self.assertTrue(all(total == totals[0] for total in totals), 
                       "Memory total should be consistent across readings")
        
        # Memory percentages should be reasonable
        percentages = [reading['percent'] for reading in readings]
        for percent in percentages:
            self.assertGreaterEqual(percent, 0)
            self.assertLessEqual(percent, 100)
    
    def test_gpu_multi_scenario(self):
        """Test GPU monitoring in various scenarios"""
        if not self.gpu_monitor.is_available():
            self.skipTest("No GPU available for testing")
        
        # Test multiple readings for consistency
        readings = []
        for _ in range(3):
            gpu_info = self.gpu_monitor.get_gpu_info()
            readings.append(gpu_info)
            time.sleep(0.1)
        
        # GPU count should be consistent
        gpu_counts = [len(reading) for reading in readings]
        self.assertTrue(all(count == gpu_counts[0] for count in gpu_counts),
                       "GPU count should be consistent across readings")
        
        # GPU names should be consistent
        if readings:
            first_reading = readings[0]
            for i, reading in enumerate(readings[1:], 1):
                for j, gpu in enumerate(reading):
                    self.assertEqual(gpu['name'], first_reading[j]['name'],
                                   f"GPU {j} name inconsistent at reading {i}")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_hardware_monitor_error_handling(self):
        """Test hardware monitor error handling"""
        with patch('psutil.cpu_percent', side_effect=Exception("Mock error")):
            # Should handle errors gracefully
            try:
                hardware_monitor = hardware.HardwareMonitor()
                cpu_info = hardware_monitor.get_cpu_info()
                # Should return default/fallback values or handle error appropriately
                self.assertIsInstance(cpu_info, dict)
            except Exception as e:
                self.fail(f"Hardware monitor should handle errors gracefully: {e}")
    
    def test_gpu_monitor_no_gpu_scenario(self):
        """Test GPU monitor behavior when no GPU is available"""
        with patch('gpu.pynvml.nvmlInit', side_effect=Exception("No GPU")):
            gpu_monitor = gpu.GPUMonitor()
            self.assertFalse(gpu_monitor.is_available())
            
            # Should return empty list or handle gracefully
            gpu_info = gpu_monitor.get_gpu_info()
            self.assertIsInstance(gpu_info, list)
    
    def test_hdd_monitor_inaccessible_drive(self):
        """Test HDD monitor behavior with inaccessible drives"""
        with patch('psutil.disk_usage', side_effect=PermissionError("Access denied")):
            try:
                hdd_monitor = hdd.HDDMonitor()
                disk_usage = hdd_monitor.get_disk_usage()
                # Should handle permission errors gracefully
                self.assertIsInstance(disk_usage, dict)
            except PermissionError:
                self.fail("HDD monitor should handle permission errors gracefully")


def run_performance_benchmark():
    """Run performance benchmarks for monitoring functions"""
    print("\\n" + "="*60)
    print("PERFORMANCE BENCHMARKS")
    print("="*60)
    
    hardware_monitor = hardware.HardwareMonitor()
    gpu_monitor = gpu.GPUMonitor()
    hdd_monitor = hdd.HDDMonitor()
    
    # CPU monitoring benchmark
    start_time = time.time()
    for _ in range(100):
        hardware_monitor.get_cpu_info()
    cpu_time = time.time() - start_time
    print(f"CPU Info (100 calls): {cpu_time:.4f}s ({cpu_time*10:.2f}ms avg)")
    
    # Memory monitoring benchmark
    start_time = time.time()
    for _ in range(100):
        hardware_monitor.get_memory_info()
    memory_time = time.time() - start_time
    print(f"Memory Info (100 calls): {memory_time:.4f}s ({memory_time*10:.2f}ms avg)")
    
    # GPU monitoring benchmark (if available)
    if gpu_monitor.is_available():
        start_time = time.time()
        for _ in range(10):  # Fewer calls as GPU monitoring can be slower
            gpu_monitor.get_gpu_info()
        gpu_time = time.time() - start_time
        print(f"GPU Info (10 calls): {gpu_time:.4f}s ({gpu_time*100:.2f}ms avg)")
    else:
        print("GPU Info: Not available (no GPU detected)")
    
    # Disk monitoring benchmark
    start_time = time.time()
    for _ in range(50):
        hdd_monitor.get_disk_usage()
    disk_time = time.time() - start_time
    print(f"Disk Usage (50 calls): {disk_time:.4f}s ({disk_time*20:.2f}ms avg)")
    
    print("="*60)


if __name__ == '__main__':
    # Run unit tests
    print("System Resource Monitor - Unit Tests")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestHardwareMonitoring))
    test_suite.addTest(unittest.makeSuite(TestGPUMonitoring))
    test_suite.addTest(unittest.makeSuite(TestHDDMonitoring))
    test_suite.addTest(unittest.makeSuite(TestDataAccuracy))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance benchmarks
    run_performance_benchmark()
    
    # Print summary
    print("\\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\\nFAILURES:")
        for test, trace in result.failures:
            print(f"- {test}: {trace.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\\nERRORS:")
        for test, trace in result.errors:
            print(f"- {test}: {trace.split('Exception:')[-1].strip()}")
    
    print("="*60)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
