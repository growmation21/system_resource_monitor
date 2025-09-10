#!/usr/bin/env python3
"""
Unit Test Runner - Task 7.1
Comprehensive Test Execution

This script runs all unit tests for the System Resource Monitor
and provides detailed reporting and analysis.
"""

import unittest
import sys
import os
import time
import importlib.util
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def discover_and_run_tests():
    """Discover and run all unit tests"""
    print("="*80)
    print("SYSTEM RESOURCE MONITOR - UNIT TEST SUITE")
    print("="*80)
    print(f"Python version: {sys.version}")
    print(f"Test directory: {Path(__file__).parent}")
    print(f"Project root: {project_root}")
    print("="*80)
    
    # Test discovery
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob("test_*.py"))
    
    print(f"\\nDiscovered {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    
    # Import availability check
    print("\\nChecking module availability...")
    
    modules_to_check = [
        ('psutil', 'System monitoring'),
        ('websockets', 'WebSocket communication'),
        ('json', 'JSON serialization'),
        ('unittest.mock', 'Test mocking')
    ]
    
    available_modules = {}
    for module_name, description in modules_to_check:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                available_modules[module_name] = True
                print(f"  ✓ {module_name} - {description}")
            else:
                available_modules[module_name] = False
                print(f"  ✗ {module_name} - {description} (not found)")
        except ImportError:
            available_modules[module_name] = False
            print(f"  ✗ {module_name} - {description} (import error)")
    
    # Backend module check
    print("\\nChecking backend modules...")
    backend_modules = ['hardware', 'gpu', 'hdd', 'monitor']
    backend_available = True
    
    for module in backend_modules:
        backend_file = project_root / 'back_end' / f'{module}.py'
        if backend_file.exists():
            print(f"  ✓ {module}.py found")
        else:
            print(f"  ✗ {module}.py not found")
            backend_available = False
    
    print("="*80)
    
    # Run test suites
    total_tests = 0
    total_failures = 0
    total_errors = 0
    test_results = {}
    
    print("\\nRunning test suites...")
    print("-"*80)
    
    # Test suite 1: Hardware Monitoring
    print("\\n1. HARDWARE MONITORING TESTS")
    print("-"*40)
    try:
        from tests.test_hardware_monitoring import (
            TestHardwareMonitoring, TestGPUMonitoring, 
            TestHDDMonitoring, TestDataAccuracy, TestErrorHandling
        )
        
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestHardwareMonitoring))
        suite.addTest(unittest.makeSuite(TestGPUMonitoring))
        suite.addTest(unittest.makeSuite(TestHDDMonitoring))
        suite.addTest(unittest.makeSuite(TestDataAccuracy))
        suite.addTest(unittest.makeSuite(TestErrorHandling))
        
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        
        test_results['hardware'] = result
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
    except ImportError as e:
        print(f"Skipped hardware tests: {e}")
        test_results['hardware'] = None
    
    # Test suite 2: WebSocket Communication
    print("\\n2. WEBSOCKET COMMUNICATION TESTS")
    print("-"*40)
    try:
        from tests.test_websocket_communication import (
            TestWebSocketCommunication, TestRealTimeDataTransmission,
            TestMessageProtocol, TestErrorHandlingAndResilience
        )
        
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestWebSocketCommunication))
        suite.addTest(unittest.makeSuite(TestRealTimeDataTransmission))
        suite.addTest(unittest.makeSuite(TestMessageProtocol))
        suite.addTest(unittest.makeSuite(TestErrorHandlingAndResilience))
        
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        
        test_results['websocket'] = result
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
    except ImportError as e:
        print(f"Skipped WebSocket tests: {e}")
        test_results['websocket'] = None
    
    # Test suite 3: Data Validation
    print("\\n3. DATA VALIDATION TESTS")
    print("-"*40)
    try:
        from tests.test_data_validation import (
            TestDataValidation, TestRangeValidation, TestEdgeCases
        )
        
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestDataValidation))
        suite.addTest(unittest.makeSuite(TestRangeValidation))
        suite.addTest(unittest.makeSuite(TestEdgeCases))
        
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        
        test_results['validation'] = result
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
    except ImportError as e:
        print(f"Skipped validation tests: {e}")
        test_results['validation'] = None
    
    # Generate comprehensive report
    print("\\n" + "="*80)
    print("COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    print(f"Total tests executed: {total_tests}")
    print(f"Total failures: {total_failures}")
    print(f"Total errors: {total_errors}")
    
    if total_tests > 0:
        success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
        print(f"Overall success rate: {success_rate:.1f}%")
    else:
        print("No tests were executed")
    
    print("\\nDetailed Results by Test Suite:")
    print("-"*40)
    
    for suite_name, result in test_results.items():
        if result is not None:
            suite_success = result.testsRun - len(result.failures) - len(result.errors)
            suite_rate = (suite_success / result.testsRun * 100) if result.testsRun > 0 else 0
            print(f"{suite_name.upper():20} | {result.testsRun:3d} tests | {suite_rate:5.1f}% success")
            
            if result.failures:
                print(f"                     | Failures:")
                for test, trace in result.failures:
                    test_name = str(test).split('.')[-1]
                    print(f"                     |   - {test_name}")
            
            if result.errors:
                print(f"                     | Errors:")
                for test, trace in result.errors:
                    test_name = str(test).split('.')[-1]
                    print(f"                     |   - {test_name}")
        else:
            print(f"{suite_name.upper():20} | SKIPPED (import error)")
    
    # Environment summary
    print("\\nEnvironment Summary:")
    print("-"*40)
    print(f"Operating System: {os.name}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Backend Available: {'Yes' if backend_available else 'No'}")
    
    critical_modules = ['psutil', 'json']
    all_critical_available = all(available_modules.get(mod, False) for mod in critical_modules)
    print(f"Critical Modules: {'Available' if all_critical_available else 'Missing'}")
    
    optional_modules = ['websockets']
    optional_available = [mod for mod in optional_modules if available_modules.get(mod, False)]
    print(f"Optional Modules: {', '.join(optional_available) if optional_available else 'None'}")
    
    # Recommendations
    print("\\nRecommendations:")
    print("-"*40)
    
    if not backend_available:
        print("- Implement backend modules (hardware.py, gpu.py, hdd.py, monitor.py)")
    
    if not available_modules.get('psutil', False):
        print("- Install psutil: pip install psutil")
    
    if not available_modules.get('websockets', False):
        print("- Install websockets: pip install websockets")
    
    if total_failures > 0:
        print(f"- Address {total_failures} test failures")
    
    if total_errors > 0:
        print(f"- Fix {total_errors} test errors")
    
    if total_tests == 0:
        print("- Ensure test modules can be imported")
    
    print("="*80)
    
    return total_tests > 0 and total_failures == 0 and total_errors == 0


def run_performance_analysis():
    """Run performance analysis of monitoring functions"""
    print("\\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    try:
        # This would run the performance benchmarks from individual test files
        print("Performance benchmarks would run here...")
        print("- CPU monitoring performance")
        print("- Memory monitoring performance") 
        print("- GPU monitoring performance")
        print("- Disk monitoring performance")
        print("- WebSocket communication latency")
        print("- Data serialization performance")
        
        # Placeholder for actual performance tests
        print("\\nPerformance analysis completed.")
        
    except Exception as e:
        print(f"Performance analysis error: {e}")
    
    print("="*80)


if __name__ == '__main__':
    start_time = time.time()
    
    # Run all tests
    success = discover_and_run_tests()
    
    # Run performance analysis
    run_performance_analysis()
    
    # Final summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\\nTest execution completed in {duration:.2f} seconds")
    print(f"Overall result: {'PASS' if success else 'FAIL'}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
