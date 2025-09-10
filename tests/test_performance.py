#!/usr/bin/env python3
"""
Performance Tests - Task 7.3
CPU Overhead, Memory Usage, and Refresh Rate Testing

This module provides comprehensive performance testing for the System
Resource Monitor including CPU overhead measurement, memory usage
monitoring, refresh rate testing, and GPU accuracy validation.
"""

import unittest
import time
import psutil
import threading
import sys
import os
import gc
import json
from pathlib import Path
from unittest.mock import Mock, patch
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to import modules
try:
    from back_end import hardware, gpu, hdd, monitor
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    MODULES_AVAILABLE = False


class TestCPUOverhead(unittest.TestCase):
    """Test CPU overhead of monitoring operations"""
    
    def setUp(self):
        """Set up CPU overhead tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.hardware_monitor = hardware.HardwareMonitor()
        self.gpu_monitor = gpu.GPUMonitor()
        self.hdd_monitor = hdd.HDDMonitor()
        self.system_monitor = monitor.SystemMonitor()
        
        # Baseline CPU measurement
        self.baseline_cpu = self._measure_baseline_cpu()
    
    def _measure_baseline_cpu(self):
        """Measure baseline CPU usage"""
        measurements = []
        for _ in range(10):
            cpu_percent = psutil.cpu_percent(interval=0.1)
            measurements.append(cpu_percent)
        return sum(measurements) / len(measurements)
    
    def _measure_cpu_during_operation(self, operation, duration=5.0):
        """Measure CPU usage during a specific operation"""
        measurements = []
        stop_flag = threading.Event()
        
        def cpu_monitor():
            while not stop_flag.is_set():
                cpu_percent = psutil.cpu_percent(interval=0.1)
                measurements.append(cpu_percent)
        
        # Start CPU monitoring
        cpu_thread = threading.Thread(target=cpu_monitor)
        cpu_thread.daemon = True
        cpu_thread.start()
        
        # Run the operation
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < duration:
            operation()
            operation_count += 1
        
        # Stop monitoring
        stop_flag.set()
        cpu_thread.join(timeout=1.0)
        
        avg_cpu = sum(measurements) / len(measurements) if measurements else 0
        overhead = avg_cpu - self.baseline_cpu
        operations_per_second = operation_count / duration
        
        return {
            'average_cpu': avg_cpu,
            'baseline_cpu': self.baseline_cpu,
            'overhead': overhead,
            'operations_per_second': operations_per_second,
            'total_operations': operation_count
        }
    
    def test_cpu_monitoring_overhead(self):
        """Test CPU overhead of CPU monitoring"""
        def cpu_operation():
            self.hardware_monitor.get_cpu_info()
        
        result = self._measure_cpu_during_operation(cpu_operation)
        
        # CPU monitoring should have minimal overhead (< 5% additional CPU)
        self.assertLess(result['overhead'], 5.0, 
                       f"CPU monitoring overhead too high: {result['overhead']:.2f}%")
        
        # Should be able to perform many operations per second
        self.assertGreater(result['operations_per_second'], 50, 
                          f"CPU monitoring too slow: {result['operations_per_second']:.1f} ops/sec")
        
        print(f"CPU Monitoring Performance:")
        print(f"  Operations/sec: {result['operations_per_second']:.1f}")
        print(f"  CPU Overhead: {result['overhead']:.2f}%")
    
    def test_memory_monitoring_overhead(self):
        """Test CPU overhead of memory monitoring"""
        def memory_operation():
            self.hardware_monitor.get_memory_info()
        
        result = self._measure_cpu_during_operation(memory_operation)
        
        # Memory monitoring should have minimal overhead
        self.assertLess(result['overhead'], 3.0, 
                       f"Memory monitoring overhead too high: {result['overhead']:.2f}%")
        
        self.assertGreater(result['operations_per_second'], 100, 
                          f"Memory monitoring too slow: {result['operations_per_second']:.1f} ops/sec")
        
        print(f"Memory Monitoring Performance:")
        print(f"  Operations/sec: {result['operations_per_second']:.1f}")
        print(f"  CPU Overhead: {result['overhead']:.2f}%")
    
    def test_disk_monitoring_overhead(self):
        """Test CPU overhead of disk monitoring"""
        def disk_operation():
            self.hdd_monitor.get_disk_usage()
        
        result = self._measure_cpu_during_operation(disk_operation)
        
        # Disk monitoring may have slightly higher overhead due to I/O
        self.assertLess(result['overhead'], 8.0, 
                       f"Disk monitoring overhead too high: {result['overhead']:.2f}%")
        
        self.assertGreater(result['operations_per_second'], 20, 
                          f"Disk monitoring too slow: {result['operations_per_second']:.1f} ops/sec")
        
        print(f"Disk Monitoring Performance:")
        print(f"  Operations/sec: {result['operations_per_second']:.1f}")
        print(f"  CPU Overhead: {result['overhead']:.2f}%")
    
    def test_gpu_monitoring_overhead(self):
        """Test CPU overhead of GPU monitoring"""
        if not self.gpu_monitor.is_available():
            self.skipTest("No GPU available for testing")
        
        def gpu_operation():
            self.gpu_monitor.get_gpu_info()
        
        result = self._measure_cpu_during_operation(gpu_operation)
        
        # GPU monitoring may have higher overhead due to NVIDIA library calls
        self.assertLess(result['overhead'], 10.0, 
                       f"GPU monitoring overhead too high: {result['overhead']:.2f}%")
        
        self.assertGreater(result['operations_per_second'], 10, 
                          f"GPU monitoring too slow: {result['operations_per_second']:.1f} ops/sec")
        
        print(f"GPU Monitoring Performance:")
        print(f"  Operations/sec: {result['operations_per_second']:.1f}")
        print(f"  CPU Overhead: {result['overhead']:.2f}%")
    
    def test_full_system_monitoring_overhead(self):
        """Test CPU overhead of complete system monitoring"""
        def system_operation():
            self.system_monitor.get_system_data()
        
        result = self._measure_cpu_during_operation(system_operation)
        
        # Full system monitoring should still be efficient
        self.assertLess(result['overhead'], 15.0, 
                       f"Full system monitoring overhead too high: {result['overhead']:.2f}%")
        
        self.assertGreater(result['operations_per_second'], 5, 
                          f"Full system monitoring too slow: {result['operations_per_second']:.1f} ops/sec")
        
        print(f"Full System Monitoring Performance:")
        print(f"  Operations/sec: {result['operations_per_second']:.1f}")
        print(f"  CPU Overhead: {result['overhead']:.2f}%")


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage and memory leaks"""
    
    def setUp(self):
        """Set up memory usage tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.hardware_monitor = hardware.HardwareMonitor()
        self.gpu_monitor = gpu.GPUMonitor()
        self.hdd_monitor = hdd.HDDMonitor()
        self.system_monitor = monitor.SystemMonitor()
        
        # Force garbage collection
        gc.collect()
        
        # Get baseline memory
        self.process = psutil.Process()
        self.baseline_memory = self.process.memory_info().rss
    
    def _measure_memory_usage(self, operation, iterations=1000):
        """Measure memory usage during operations"""
        gc.collect()
        start_memory = self.process.memory_info().rss
        
        for _ in range(iterations):
            operation()
        
        gc.collect()
        end_memory = self.process.memory_info().rss
        
        memory_increase = end_memory - start_memory
        memory_per_operation = memory_increase / iterations
        
        return {
            'start_memory': start_memory,
            'end_memory': end_memory,
            'memory_increase': memory_increase,
            'memory_per_operation': memory_per_operation,
            'iterations': iterations
        }
    
    def test_cpu_monitoring_memory_usage(self):
        """Test memory usage of CPU monitoring"""
        def cpu_operation():
            data = self.hardware_monitor.get_cpu_info()
            # Ensure data is used to prevent optimization
            _ = data['cpu_percent']
        
        result = self._measure_memory_usage(cpu_operation)
        
        # Memory per operation should be minimal (< 1KB per operation)
        self.assertLess(result['memory_per_operation'], 1024, 
                       f"CPU monitoring uses too much memory: {result['memory_per_operation']} bytes/op")
        
        print(f"CPU Monitoring Memory Usage:")
        print(f"  Memory per operation: {result['memory_per_operation']:.1f} bytes")
        print(f"  Total increase: {result['memory_increase'] / 1024:.1f} KB")
    
    def test_memory_monitoring_memory_usage(self):
        """Test memory usage of memory monitoring"""
        def memory_operation():
            data = self.hardware_monitor.get_memory_info()
            _ = data['total']
        
        result = self._measure_memory_usage(memory_operation)
        
        self.assertLess(result['memory_per_operation'], 1024, 
                       f"Memory monitoring uses too much memory: {result['memory_per_operation']} bytes/op")
        
        print(f"Memory Monitoring Memory Usage:")
        print(f"  Memory per operation: {result['memory_per_operation']:.1f} bytes")
        print(f"  Total increase: {result['memory_increase'] / 1024:.1f} KB")
    
    def test_disk_monitoring_memory_usage(self):
        """Test memory usage of disk monitoring"""
        def disk_operation():
            data = self.hdd_monitor.get_disk_usage()
            _ = len(data)
        
        result = self._measure_memory_usage(disk_operation, iterations=500)  # Fewer iterations for I/O
        
        # Disk monitoring may use slightly more memory due to data structures
        self.assertLess(result['memory_per_operation'], 2048, 
                       f"Disk monitoring uses too much memory: {result['memory_per_operation']} bytes/op")
        
        print(f"Disk Monitoring Memory Usage:")
        print(f"  Memory per operation: {result['memory_per_operation']:.1f} bytes")
        print(f"  Total increase: {result['memory_increase'] / 1024:.1f} KB")
    
    def test_json_serialization_memory_usage(self):
        """Test memory usage of JSON serialization"""
        def json_operation():
            data = self.system_monitor.get_system_data()
            json_string = json.dumps(data)
            _ = len(json_string)
        
        result = self._measure_memory_usage(json_operation, iterations=500)
        
        # JSON serialization should be efficient
        self.assertLess(result['memory_per_operation'], 4096, 
                       f"JSON serialization uses too much memory: {result['memory_per_operation']} bytes/op")
        
        print(f"JSON Serialization Memory Usage:")
        print(f"  Memory per operation: {result['memory_per_operation']:.1f} bytes")
        print(f"  Total increase: {result['memory_increase'] / 1024:.1f} KB")
    
    def test_long_running_memory_stability(self):
        """Test memory stability over long periods"""
        gc.collect()
        start_memory = self.process.memory_info().rss
        
        # Run monitoring for extended period
        for i in range(100):
            self.system_monitor.get_system_data()
            
            # Check memory every 10 iterations
            if i % 10 == 0:
                current_memory = self.process.memory_info().rss
                memory_increase = current_memory - start_memory
                
                # Memory should not grow excessively (< 10MB increase)
                self.assertLess(memory_increase, 10 * 1024 * 1024, 
                               f"Memory leak detected: {memory_increase / 1024 / 1024:.1f} MB increase")
        
        gc.collect()
        final_memory = self.process.memory_info().rss
        total_increase = final_memory - start_memory
        
        print(f"Long-running Memory Stability:")
        print(f"  Total memory increase: {total_increase / 1024:.1f} KB")
        print(f"  Memory increase per operation: {total_increase / 100:.1f} bytes")


class TestRefreshRateTesting(unittest.TestCase):
    """Test refresh rate and timing accuracy"""
    
    def setUp(self):
        """Set up refresh rate tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.system_monitor = monitor.SystemMonitor()
    
    def test_timestamp_accuracy(self):
        """Test timestamp accuracy and consistency"""
        timestamps = []
        system_time = []
        
        for _ in range(10):
            before_time = time.time()
            data = self.system_monitor.get_system_data()
            after_time = time.time()
            
            timestamps.append(data['timestamp'])
            system_time.append((before_time + after_time) / 2)
        
        # Check timestamp accuracy (should be within 100ms of system time)
        for i, (ts, sys_time) in enumerate(zip(timestamps, system_time)):
            difference = abs(ts - sys_time)
            self.assertLess(difference, 0.1, 
                           f"Timestamp {i} inaccurate: {difference:.3f}s difference")
        
        # Check timestamp monotonicity
        for i in range(1, len(timestamps)):
            self.assertGreater(timestamps[i], timestamps[i-1], 
                              f"Timestamp {i} not monotonic")
    
    def test_refresh_rate_1hz(self):
        """Test 1Hz refresh rate accuracy"""
        self._test_refresh_rate(1.0, tolerance=0.1)
    
    def test_refresh_rate_2hz(self):
        """Test 2Hz refresh rate accuracy"""
        self._test_refresh_rate(0.5, tolerance=0.05)
    
    def test_refresh_rate_5hz(self):
        """Test 5Hz refresh rate accuracy"""
        self._test_refresh_rate(0.2, tolerance=0.02)
    
    def test_refresh_rate_10hz(self):
        """Test 10Hz refresh rate accuracy"""
        self._test_refresh_rate(0.1, tolerance=0.01)
    
    def _test_refresh_rate(self, target_interval, tolerance):
        """Test a specific refresh rate"""
        timestamps = []
        
        # Collect data at target interval
        for _ in range(10):
            start_time = time.time()
            data = self.system_monitor.get_system_data()
            timestamps.append(data['timestamp'])
            
            # Sleep for target interval
            elapsed = time.time() - start_time
            sleep_time = max(0, target_interval - elapsed)
            time.sleep(sleep_time)
        
        # Calculate actual intervals
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        # Check interval accuracy
        for i, interval in enumerate(intervals):
            self.assertAlmostEqual(interval, target_interval, delta=tolerance,
                                  msg=f"Interval {i} inaccurate: {interval:.3f}s vs {target_interval:.3f}s")
        
        avg_interval = sum(intervals) / len(intervals)
        print(f"Refresh Rate {1/target_interval:.1f}Hz:")
        print(f"  Target interval: {target_interval:.3f}s")
        print(f"  Average interval: {avg_interval:.3f}s")
        print(f"  Accuracy: {abs(avg_interval - target_interval):.3f}s")
    
    def test_high_frequency_monitoring(self):
        """Test high-frequency monitoring capabilities"""
        # Test maximum sustainable refresh rate
        start_time = time.time()
        operation_count = 0
        duration = 2.0  # 2 seconds
        
        while time.time() - start_time < duration:
            self.system_monitor.get_system_data()
            operation_count += 1
        
        actual_duration = time.time() - start_time
        max_frequency = operation_count / actual_duration
        
        # Should be able to sustain at least 20Hz
        self.assertGreater(max_frequency, 20, 
                          f"Maximum frequency too low: {max_frequency:.1f} Hz")
        
        print(f"High-Frequency Monitoring:")
        print(f"  Maximum sustained frequency: {max_frequency:.1f} Hz")
        print(f"  Operations in {actual_duration:.1f}s: {operation_count}")
    
    def test_timing_consistency_under_load(self):
        """Test timing consistency under system load"""
        # Create some background load
        def background_load():
            end_time = time.time() + 3.0
            while time.time() < end_time:
                _ = [i**2 for i in range(1000)]
        
        load_thread = threading.Thread(target=background_load)
        load_thread.daemon = True
        load_thread.start()
        
        # Measure timing consistency during load
        timestamps = []
        for _ in range(15):
            start_time = time.time()
            data = self.system_monitor.get_system_data()
            timestamps.append(data['timestamp'])
            
            # Target 0.2s interval (5Hz)
            elapsed = time.time() - start_time
            sleep_time = max(0, 0.2 - elapsed)
            time.sleep(sleep_time)
        
        # Calculate timing variance
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((interval - avg_interval)**2 for interval in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        # Standard deviation should be reasonable even under load
        self.assertLess(std_dev, 0.05, 
                       f"Timing too inconsistent under load: {std_dev:.3f}s std dev")
        
        print(f"Timing Consistency Under Load:")
        print(f"  Average interval: {avg_interval:.3f}s")
        print(f"  Standard deviation: {std_dev:.3f}s")


class TestGPUAccuracyValidation(unittest.TestCase):
    """Test GPU monitoring accuracy and validation"""
    
    def setUp(self):
        """Set up GPU accuracy tests"""
        if not MODULES_AVAILABLE:
            self.skipTest("Backend modules not available")
        
        self.gpu_monitor = gpu.GPUMonitor()
        
        if not self.gpu_monitor.is_available():
            self.skipTest("No GPU available for testing")
    
    def test_gpu_utilization_range(self):
        """Test GPU utilization is within valid range"""
        for _ in range(10):
            gpu_info = self.gpu_monitor.get_gpu_info()
            
            for i, gpu in enumerate(gpu_info):
                utilization = gpu.get('gpu_utilization', 0)
                
                self.assertIsInstance(utilization, (int, float), 
                                    f"GPU {i} utilization should be numeric")
                self.assertGreaterEqual(utilization, 0, 
                                       f"GPU {i} utilization should be >= 0")
                self.assertLessEqual(utilization, 100, 
                                    f"GPU {i} utilization should be <= 100")
            
            time.sleep(0.1)
    
    def test_gpu_memory_consistency(self):
        """Test GPU memory data consistency"""
        gpu_info = self.gpu_monitor.get_gpu_info()
        
        for i, gpu in enumerate(gpu_info):
            if 'memory_total' in gpu and 'memory_used' in gpu:
                total = gpu['memory_total']
                used = gpu['memory_used']
                
                self.assertGreater(total, 0, f"GPU {i} total memory should be > 0")
                self.assertGreaterEqual(used, 0, f"GPU {i} used memory should be >= 0")
                self.assertLessEqual(used, total, f"GPU {i} used memory should be <= total")
                
                # Check memory utilization calculation
                if 'memory_utilization' in gpu:
                    util = gpu['memory_utilization']
                    calculated_util = (used / total) * 100
                    self.assertAlmostEqual(util, calculated_util, delta=1.0,
                                          msg=f"GPU {i} memory utilization calculation error")
    
    def test_gpu_temperature_validation(self):
        """Test GPU temperature readings"""
        gpu_info = self.gpu_monitor.get_gpu_info()
        
        for i, gpu in enumerate(gpu_info):
            if 'gpu_temperature' in gpu:
                temp = gpu['gpu_temperature']
                
                self.assertIsInstance(temp, (int, float), 
                                    f"GPU {i} temperature should be numeric")
                self.assertGreater(temp, 0, f"GPU {i} temperature should be > 0°C")
                self.assertLess(temp, 150, f"GPU {i} temperature should be < 150°C")
                
                # Temperature should be reasonable for normal operation
                self.assertLess(temp, 100, f"GPU {i} temperature very high: {temp}°C")
    
    def test_gpu_data_stability(self):
        """Test GPU data stability over time"""
        readings = []
        
        for _ in range(5):
            gpu_info = self.gpu_monitor.get_gpu_info()
            readings.append(gpu_info)
            time.sleep(0.5)
        
        # Check that GPU count remains consistent
        gpu_counts = [len(reading) for reading in readings]
        self.assertTrue(all(count == gpu_counts[0] for count in gpu_counts),
                       "GPU count should remain consistent")
        
        # Check that GPU names remain consistent
        if readings:
            first_reading = readings[0]
            for i, reading in enumerate(readings[1:], 1):
                self.assertEqual(len(reading), len(first_reading),
                               f"GPU count changed at reading {i}")
                
                for j, (gpu1, gpu2) in enumerate(zip(first_reading, reading)):
                    self.assertEqual(gpu1.get('name'), gpu2.get('name'),
                                   f"GPU {j} name changed at reading {i}")


def run_performance_benchmark_suite():
    """Run comprehensive performance benchmark"""
    print("\\n" + "="*80)
    print("PERFORMANCE BENCHMARK SUITE")
    print("="*80)
    
    if not MODULES_AVAILABLE:
        print("Backend modules not available - skipping benchmarks")
        return {}
    
    try:
        system_monitor = monitor.SystemMonitor()
        
        # Benchmark different operations
        benchmarks = {}
        
        print("\\nRunning performance benchmarks...")
        
        # CPU monitoring benchmark
        start_time = time.time()
        for _ in range(100):
            system_monitor.get_system_data()
        duration = time.time() - start_time
        
        benchmarks['full_monitoring'] = {
            'operations': 100,
            'duration': duration,
            'ops_per_second': 100 / duration,
            'ms_per_operation': (duration / 100) * 1000
        }
        
        print(f"\\nBenchmark Results:")
        print(f"Full System Monitoring:")
        print(f"  Operations/second: {benchmarks['full_monitoring']['ops_per_second']:.1f}")
        print(f"  ms per operation: {benchmarks['full_monitoring']['ms_per_operation']:.2f}")
        
        # Memory usage benchmark
        process = psutil.Process()
        start_memory = process.memory_info().rss
        
        for _ in range(1000):
            data = system_monitor.get_system_data()
            json.dumps(data)  # Include serialization
        
        end_memory = process.memory_info().rss
        memory_increase = end_memory - start_memory
        
        benchmarks['memory_efficiency'] = {
            'memory_increase_kb': memory_increase / 1024,
            'memory_per_op_bytes': memory_increase / 1000
        }
        
        print(f"\\nMemory Efficiency:")
        print(f"  Memory increase: {benchmarks['memory_efficiency']['memory_increase_kb']:.1f} KB")
        print(f"  Memory per operation: {benchmarks['memory_efficiency']['memory_per_op_bytes']:.1f} bytes")
        
        return benchmarks
        
    except Exception as e:
        print(f"Benchmark error: {e}")
        return {}


if __name__ == '__main__':
    print("Performance Tests - CPU Overhead, Memory Usage, and Refresh Rate Testing")
    print("="*80)
    
    if not MODULES_AVAILABLE:
        print("Warning: Backend modules not available")
        print("Some tests will be skipped")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestCPUOverhead))
    test_suite.addTest(unittest.makeSuite(TestMemoryUsage))
    test_suite.addTest(unittest.makeSuite(TestRefreshRateTesting))
    test_suite.addTest(unittest.makeSuite(TestGPUAccuracyValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance benchmarks
    benchmarks = run_performance_benchmark_suite()
    
    # Print summary
    print("\\n" + "="*80)
    print("PERFORMANCE TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\\nFAILURES:")
        for test, trace in result.failures:
            test_name = str(test).split('.')[-1]
            print(f"- {test_name}")
    
    if result.errors:
        print("\\nERRORS:")
        for test, trace in result.errors:
            test_name = str(test).split('.')[-1]
            print(f"- {test_name}")
    
    print("\\nPerformance testing completed!")
    print("="*80)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
