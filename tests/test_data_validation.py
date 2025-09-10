#!/usr/bin/env python3
"""
Data Validation Tests - Task 7.1
Accuracy and Consistency Testing

This module provides comprehensive tests for data accuracy, validation,
and consistency across all monitoring components.
"""

import unittest
import time
import json
import sys
import os
import platform
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import modules (may need to handle import errors in CI/CD)
try:
    from back_end import hardware, gpu, hdd, monitor
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    MODULES_AVAILABLE = False


class TestDataValidation(unittest.TestCase):
    """Test data validation and accuracy"""
    
    def setUp(self):
        """Set up data validation tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.hardware_monitor = hardware.HardwareMonitor()
        self.gpu_monitor = gpu.GPUMonitor()
        self.hdd_monitor = hdd.HDDMonitor()
        self.system_monitor = monitor.SystemMonitor()
    
    def test_cpu_percentage_bounds(self):
        """Test CPU percentage is within valid bounds"""
        for _ in range(10):  # Multiple readings
            cpu_info = self.hardware_monitor.get_cpu_info()
            cpu_percent = cpu_info.get('cpu_percent', 0)
            
            self.assertIsInstance(cpu_percent, (int, float),
                                "CPU percentage should be numeric")
            self.assertGreaterEqual(cpu_percent, 0,
                                   "CPU percentage should be >= 0")
            self.assertLessEqual(cpu_percent, 100,
                                "CPU percentage should be <= 100")
            time.sleep(0.1)
    
    def test_memory_data_consistency(self):
        """Test memory data internal consistency"""
        memory_info = self.hardware_monitor.get_memory_info()
        
        total = memory_info.get('total', 0)
        used = memory_info.get('used', 0)
        available = memory_info.get('available', 0)
        percent = memory_info.get('percent', 0)
        
        # Basic type checking
        for value in [total, used, available, percent]:
            self.assertIsInstance(value, (int, float),
                                "Memory values should be numeric")
        
        # Logical consistency
        self.assertGreater(total, 0, "Total memory should be > 0")
        self.assertGreaterEqual(used, 0, "Used memory should be >= 0")
        self.assertGreaterEqual(available, 0, "Available memory should be >= 0")
        self.assertLessEqual(used, total, "Used memory should be <= total")
        self.assertGreaterEqual(percent, 0, "Memory percentage should be >= 0")
        self.assertLessEqual(percent, 100, "Memory percentage should be <= 100")
        
        # Mathematical consistency (allowing for small discrepancies)
        calculated_percent = (used / total) * 100
        self.assertAlmostEqual(percent, calculated_percent, delta=5,
                              msg="Memory percentage should match calculation")
    
    def test_disk_usage_accuracy(self):
        """Test disk usage data accuracy"""
        disk_usage = self.hdd_monitor.get_disk_usage()
        
        self.assertIsInstance(disk_usage, dict,
                             "Disk usage should be a dictionary")
        
        for drive, usage in disk_usage.items():
            self.assertIsInstance(drive, str, "Drive identifier should be string")
            self.assertIsInstance(usage, dict, "Usage data should be dictionary")
            
            # Required fields
            required_fields = ['total', 'used', 'free', 'percent']
            for field in required_fields:
                self.assertIn(field, usage, f"Missing field {field} for drive {drive}")
            
            total = usage['total']
            used = usage['used']
            free = usage['free']
            percent = usage['percent']
            
            # Type validation
            for value in [total, used, free, percent]:
                self.assertIsInstance(value, (int, float),
                                    f"Drive {drive} values should be numeric")
            
            # Logical validation
            self.assertGreater(total, 0, f"Drive {drive} total should be > 0")
            self.assertGreaterEqual(used, 0, f"Drive {drive} used should be >= 0")
            self.assertGreaterEqual(free, 0, f"Drive {drive} free should be >= 0")
            self.assertLessEqual(used, total, f"Drive {drive} used should be <= total")
            self.assertGreaterEqual(percent, 0, f"Drive {drive} percent should be >= 0")
            self.assertLessEqual(percent, 100, f"Drive {drive} percent should be <= 100")
            
            # Space calculation consistency (allowing for filesystem overhead)
            space_sum = used + free
            tolerance = total * 0.05  # 5% tolerance for filesystem overhead
            self.assertAlmostEqual(total, space_sum, delta=tolerance,
                                  msg=f"Drive {drive} total space calculation inconsistent")
    
    def test_gpu_data_validation(self):
        """Test GPU data validation when available"""
        if not self.gpu_monitor.is_available():
            self.skipTest("No GPU available for testing")
        
        gpu_info = self.gpu_monitor.get_gpu_info()
        
        self.assertIsInstance(gpu_info, list, "GPU info should be a list")
        
        for i, gpu in enumerate(gpu_info):
            self.assertIsInstance(gpu, dict, f"GPU {i} info should be dictionary")
            
            # Required fields
            required_fields = ['name', 'gpu_utilization', 'memory_utilization', 'gpu_temperature']
            for field in required_fields:
                self.assertIn(field, gpu, f"GPU {i} missing field {field}")
            
            # Data validation
            self.assertIsInstance(gpu['name'], str, f"GPU {i} name should be string")
            
            gpu_util = gpu['gpu_utilization']
            mem_util = gpu['memory_utilization']
            temp = gpu['gpu_temperature']
            
            # Utilization validation
            self.assertIsInstance(gpu_util, (int, float),
                                f"GPU {i} utilization should be numeric")
            self.assertGreaterEqual(gpu_util, 0,
                                   f"GPU {i} utilization should be >= 0")
            self.assertLessEqual(gpu_util, 100,
                                f"GPU {i} utilization should be <= 100")
            
            self.assertIsInstance(mem_util, (int, float),
                                f"GPU {i} memory utilization should be numeric")
            self.assertGreaterEqual(mem_util, 0,
                                   f"GPU {i} memory utilization should be >= 0")
            self.assertLessEqual(mem_util, 100,
                                f"GPU {i} memory utilization should be <= 100")
            
            # Temperature validation
            self.assertIsInstance(temp, (int, float),
                                f"GPU {i} temperature should be numeric")
            self.assertGreater(temp, 0, f"GPU {i} temperature should be > 0")
            self.assertLess(temp, 150, f"GPU {i} temperature should be < 150°C")
    
    def test_timestamp_accuracy(self):
        """Test timestamp accuracy and consistency"""
        before_time = time.time()
        system_data = self.system_monitor.get_system_data()
        after_time = time.time()
        
        timestamp = system_data.get('timestamp')
        
        self.assertIsInstance(timestamp, (int, float),
                             "Timestamp should be numeric")
        self.assertGreaterEqual(timestamp, before_time,
                               "Timestamp should be >= before_time")
        self.assertLessEqual(timestamp, after_time,
                            "Timestamp should be <= after_time")
        
        # Test multiple timestamps are increasing
        timestamps = []
        for _ in range(5):
            data = self.system_monitor.get_system_data()
            timestamps.append(data['timestamp'])
            time.sleep(0.1)
        
        for i in range(1, len(timestamps)):
            self.assertGreater(timestamps[i], timestamps[i-1],
                              "Timestamps should be increasing")
    
    def test_data_type_consistency(self):
        """Test data type consistency across multiple readings"""
        # Collect multiple readings
        readings = []
        for _ in range(3):
            data = self.system_monitor.get_system_data()
            readings.append(data)
            time.sleep(0.5)
        
        # Check type consistency
        for key in readings[0].keys():
            first_type = type(readings[0][key])
            for i, reading in enumerate(readings[1:], 1):
                self.assertEqual(type(reading[key]), first_type,
                               f"Type of {key} inconsistent at reading {i}")
        
        # Check structure consistency for nested data
        for i, reading in enumerate(readings):
            if 'cpu' in reading:
                cpu_data = reading['cpu']
                expected_cpu_keys = {'percent', 'count', 'frequency'}
                self.assertTrue(expected_cpu_keys.issubset(cpu_data.keys()),
                               f"CPU data structure inconsistent at reading {i}")
            
            if 'memory' in reading:
                memory_data = reading['memory']
                expected_memory_keys = {'total', 'used', 'available', 'percent'}
                self.assertTrue(expected_memory_keys.issubset(memory_data.keys()),
                               f"Memory data structure inconsistent at reading {i}")


class TestRangeValidation(unittest.TestCase):
    """Test value ranges and bounds"""
    
    def setUp(self):
        """Set up range validation tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.system_monitor = monitor.SystemMonitor()
    
    def test_percentage_values(self):
        """Test all percentage values are within 0-100 range"""
        data = self.system_monitor.get_system_data()
        
        # CPU percentage
        if 'cpu' in data and 'percent' in data['cpu']:
            cpu_percent = data['cpu']['percent']
            self.assertGreaterEqual(cpu_percent, 0)
            self.assertLessEqual(cpu_percent, 100)
        
        # Memory percentage
        if 'memory' in data and 'percent' in data['memory']:
            memory_percent = data['memory']['percent']
            self.assertGreaterEqual(memory_percent, 0)
            self.assertLessEqual(memory_percent, 100)
        
        # Disk percentages
        if 'disks' in data:
            for drive, usage in data['disks'].items():
                if 'percent' in usage:
                    disk_percent = usage['percent']
                    self.assertGreaterEqual(disk_percent, 0,
                                           f"Drive {drive} percentage below 0")
                    self.assertLessEqual(disk_percent, 100,
                                        f"Drive {drive} percentage above 100")
        
        # GPU percentages
        if 'gpu' in data:
            for i, gpu in enumerate(data['gpu']):
                if 'gpu_utilization' in gpu:
                    gpu_util = gpu['gpu_utilization']
                    self.assertGreaterEqual(gpu_util, 0,
                                           f"GPU {i} utilization below 0")
                    self.assertLessEqual(gpu_util, 100,
                                        f"GPU {i} utilization above 100")
                
                if 'memory_utilization' in gpu:
                    mem_util = gpu['memory_utilization']
                    self.assertGreaterEqual(mem_util, 0,
                                           f"GPU {i} memory utilization below 0")
                    self.assertLessEqual(mem_util, 100,
                                        f"GPU {i} memory utilization above 100")
    
    def test_memory_sizes(self):
        """Test memory size values are reasonable"""
        data = self.system_monitor.get_system_data()
        
        if 'memory' in data:
            memory = data['memory']
            
            # Total memory should be reasonable (at least 1GB, less than 1TB)
            total = memory.get('total', 0)
            self.assertGreater(total, 1024**3, "Total memory should be > 1GB")
            self.assertLess(total, 1024**4, "Total memory should be < 1TB")
            
            # Used memory should be less than total
            used = memory.get('used', 0)
            self.assertGreaterEqual(used, 0)
            self.assertLessEqual(used, total)
            
            # Available memory should be reasonable
            available = memory.get('available', 0)
            self.assertGreaterEqual(available, 0)
            self.assertLessEqual(available, total)
    
    def test_temperature_ranges(self):
        """Test temperature values are within reasonable ranges"""
        data = self.system_monitor.get_system_data()
        
        if 'gpu' in data:
            for i, gpu in enumerate(data['gpu']):
                if 'gpu_temperature' in gpu:
                    temp = gpu['gpu_temperature']
                    
                    # Temperature should be reasonable (0-100°C typical range)
                    self.assertGreater(temp, 0, f"GPU {i} temperature too low")
                    self.assertLess(temp, 120, f"GPU {i} temperature too high")
    
    def test_frequency_values(self):
        """Test frequency values are reasonable"""
        data = self.system_monitor.get_system_data()
        
        if 'cpu' in data and 'frequency' in data['cpu']:
            freq = data['cpu']['frequency']
            
            # CPU frequency should be reasonable (0.5GHz - 10GHz)
            if freq is not None and freq > 0:
                self.assertGreater(freq, 500, "CPU frequency too low")
                self.assertLess(freq, 10000, "CPU frequency too high")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up edge case tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.system_monitor = monitor.SystemMonitor()
    
    def test_high_load_conditions(self):
        """Test data validity under high system load"""
        # Simulate high load by collecting data rapidly
        rapid_readings = []
        start_time = time.time()
        
        while time.time() - start_time < 2.0:  # 2 seconds of rapid collection
            data = self.system_monitor.get_system_data()
            rapid_readings.append(data)
        
        self.assertGreater(len(rapid_readings), 5,
                          "Should collect multiple readings under load")
        
        # All readings should be valid
        for i, reading in enumerate(rapid_readings):
            self.assertIsInstance(reading, dict, f"Reading {i} should be dict")
            self.assertIn('timestamp', reading, f"Reading {i} missing timestamp")
            self.assertIn('cpu', reading, f"Reading {i} missing CPU data")
            self.assertIn('memory', reading, f"Reading {i} missing memory data")
    
    def test_zero_values_handling(self):
        """Test handling of zero values in data"""
        # This test checks that zero values are handled appropriately
        # In some cases, zero might be valid (e.g., 0% CPU usage)
        # In others, it might indicate an error (e.g., 0 total memory)
        
        data = self.system_monitor.get_system_data()
        
        # Memory total should never be zero
        if 'memory' in data:
            total_memory = data['memory'].get('total', 0)
            self.assertGreater(total_memory, 0, "Total memory should never be zero")
        
        # CPU count should never be zero
        if 'cpu' in data:
            cpu_count = data['cpu'].get('count', 0)
            self.assertGreater(cpu_count, 0, "CPU count should never be zero")
    
    def test_missing_data_handling(self):
        """Test handling of missing or unavailable data"""
        # Test behavior when certain hardware is not available
        
        # GPU data might be missing on systems without GPU
        data = self.system_monitor.get_system_data()
        
        if 'gpu' in data:
            gpu_list = data['gpu']
            self.assertIsInstance(gpu_list, list, "GPU data should be list")
            # Empty list is acceptable for systems without GPU
        
        # Essential data should always be present
        essential_keys = ['timestamp', 'cpu', 'memory']
        for key in essential_keys:
            self.assertIn(key, data, f"Essential key {key} missing")
    
    def test_long_running_stability(self):
        """Test data stability over extended period"""
        # Collect data over longer period to test stability
        long_readings = []
        start_time = time.time()
        
        while time.time() - start_time < 10.0:  # 10 seconds
            data = self.system_monitor.get_system_data()
            long_readings.append(data)
            time.sleep(1)
        
        # Check for any degradation or invalid data over time
        for i, reading in enumerate(long_readings):
            self.assertIsInstance(reading, dict, f"Long reading {i} invalid")
            
            # Check timestamp progression
            if i > 0:
                prev_timestamp = long_readings[i-1]['timestamp']
                curr_timestamp = reading['timestamp']
                self.assertGreater(curr_timestamp, prev_timestamp,
                                  f"Timestamp regression at reading {i}")


def run_data_validation_summary():
    """Run comprehensive data validation summary"""
    print("\\n" + "="*60)
    print("DATA VALIDATION SUMMARY")
    print("="*60)
    
    if not MODULES_AVAILABLE:
        print("Backend modules not available - skipping validation")
        return
    
    try:
        system_monitor = monitor.SystemMonitor()
        
        # Collect sample data
        sample_data = system_monitor.get_system_data()
        
        print("Data Structure Analysis:")
        print(f"- Top-level keys: {list(sample_data.keys())}")
        
        if 'cpu' in sample_data:
            cpu_data = sample_data['cpu']
            print(f"- CPU data keys: {list(cpu_data.keys())}")
            print(f"- CPU usage: {cpu_data.get('percent', 'N/A')}%")
        
        if 'memory' in sample_data:
            memory_data = sample_data['memory']
            total_gb = memory_data.get('total', 0) / (1024**3)
            used_percent = memory_data.get('percent', 0)
            print(f"- Memory total: {total_gb:.1f} GB")
            print(f"- Memory usage: {used_percent:.1f}%")
        
        if 'disks' in sample_data:
            disk_data = sample_data['disks']
            print(f"- Disk drives: {list(disk_data.keys())}")
        
        if 'gpu' in sample_data:
            gpu_data = sample_data['gpu']
            print(f"- GPU count: {len(gpu_data)}")
            if gpu_data:
                for i, gpu in enumerate(gpu_data):
                    name = gpu.get('name', 'Unknown')
                    util = gpu.get('gpu_utilization', 'N/A')
                    print(f"  - GPU {i}: {name} ({util}% util)")
        
        # Data size analysis
        json_data = json.dumps(sample_data)
        data_size = len(json_data.encode('utf-8'))
        print(f"- Data payload size: {data_size} bytes")
        
        print("\\nValidation checks completed successfully!")
        
    except Exception as e:
        print(f"Validation summary error: {e}")
    
    print("="*60)


if __name__ == '__main__':
    # Run data validation tests
    print("Data Validation Tests")
    print("="*60)
    
    if not MODULES_AVAILABLE:
        print("Warning: Backend modules not available")
        print("Some tests will be skipped")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDataValidation))
    test_suite.addTest(unittest.makeSuite(TestRangeValidation))
    test_suite.addTest(unittest.makeSuite(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run validation summary
    run_data_validation_summary()
    
    # Print summary
    print("\\n" + "="*60)
    print("VALIDATION TEST SUMMARY")
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
