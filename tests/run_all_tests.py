#!/usr/bin/env python3
"""
Comprehensive Test Runner - Phase 7 Complete
System Resource Monitor Testing Suite

This script runs all tests from Phase 7 (Testing and Validation) including:
- Task 7.1: Unit Testing (Hardware monitoring, WebSocket communication, Data validation)
- Task 7.2: Integration Testing (Chrome app, UI responsiveness, Settings persistence)  
- Task 7.3: Performance Testing (CPU overhead, Memory usage, Refresh rate)
- Task 7.4: Platform Testing (Windows compatibility, NVIDIA GPU, Window management)
"""

import unittest
import sys
import os
import time
import platform
import importlib.util
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestSuiteRunner:
    """Comprehensive test suite runner for all Phase 7 tests"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_skipped = 0
        
    def print_header(self):
        """Print test suite header"""
        print("="*100)
        print("SYSTEM RESOURCE MONITOR - COMPREHENSIVE TEST SUITE")
        print("Phase 7: Testing and Validation - Complete")
        print("="*100)
        print(f"Project Root: {self.project_root}")
        print(f"Test Directory: {self.test_dir}")
        print(f"Platform: {platform.platform()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Architecture: {platform.architecture()[0]}")
        print("="*100)
    
    def check_dependencies(self):
        """Check for required dependencies"""
        print("\\nDEPENDENCY CHECK")
        print("-" * 50)
        
        dependencies = {
            'unittest': ('Unit testing framework', True),
            'json': ('JSON processing', True),
            'time': ('Time utilities', True),
            'platform': ('Platform information', True),
            'pathlib': ('Path handling', True),
            'psutil': ('System monitoring', False),
            'websockets': ('WebSocket communication', False),
            'pynvml': ('NVIDIA GPU monitoring', False),
            'wmi': ('Windows Management Interface', False),
            'win32api': ('Windows API', False)
        }
        
        available_deps = {}
        critical_missing = []
        
        for dep_name, (description, critical) in dependencies.items():
            try:
                spec = importlib.util.find_spec(dep_name)
                if spec is not None:
                    available_deps[dep_name] = True
                    status = "✓ Available"
                else:
                    available_deps[dep_name] = False
                    status = "✗ Missing"
                    if critical:
                        critical_missing.append(dep_name)
            except ImportError:
                available_deps[dep_name] = False
                status = "✗ Import Error"
                if critical:
                    critical_missing.append(dep_name)
            
            print(f"  {dep_name:15} | {description:25} | {status}")
        
        if critical_missing:
            print(f"\\nCRITICAL: Missing required dependencies: {', '.join(critical_missing)}")
            return False
        
        print(f"\\nDependency check completed. Optional dependencies may affect some tests.")
        return True
    
    def check_backend_modules(self):
        """Check backend module availability"""
        print("\\nBACKEND MODULE CHECK")
        print("-" * 50)
        
        backend_modules = ['hardware', 'gpu', 'hdd', 'monitor']
        backend_available = True
        
        for module in backend_modules:
            module_file = self.project_root / 'back_end' / f'{module}.py'
            if module_file.exists():
                print(f"  ✓ {module}.py found")
            else:
                print(f"  ✗ {module}.py missing")
                backend_available = False
        
        if backend_available:
            print("\\nBackend modules available for testing")
        else:
            print("\\nWARNING: Some backend modules missing - unit tests may be skipped")
        
        return backend_available
    
    def check_chrome_app(self):
        """Check Chrome app files"""
        print("\\nCHROME APP CHECK")
        print("-" * 50)
        
        chrome_app_dir = self.project_root / 'chrome-app'
        required_files = [
            'manifest.json',
            'background.js', 
            'monitor.html',
            'monitor.js',
            'monitor.css',
            'settings-panel.js'
        ]
        
        chrome_app_available = True
        
        if chrome_app_dir.exists():
            print(f"  ✓ Chrome app directory found")
            
            for file_name in required_files:
                file_path = chrome_app_dir / file_name
                if file_path.exists():
                    print(f"  ✓ {file_name}")
                else:
                    print(f"  ✗ {file_name} missing")
                    chrome_app_available = False
        else:
            print(f"  ✗ Chrome app directory missing")
            chrome_app_available = False
        
        if chrome_app_available:
            print("\\nChrome app files available for integration testing")
        else:
            print("\\nWARNING: Chrome app files missing - integration tests may be skipped")
        
        return chrome_app_available
    
    def run_task_71_unit_tests(self):
        """Run Task 7.1 - Unit Testing"""
        print("\\n" + "="*100)
        print("TASK 7.1 - UNIT TESTING")
        print("="*100)
        
        test_modules = [
            ('test_hardware_monitoring', 'Hardware Monitoring Tests'),
            ('test_websocket_communication', 'WebSocket Communication Tests'),
            ('test_data_validation', 'Data Validation Tests')
        ]
        
        task_results = {}
        
        for module_name, description in test_modules:
            print(f"\\n{description}")
            print("-" * 60)
            
            try:
                # Import test module
                test_module = importlib.import_module(f'tests.{module_name}')
                
                # Create test suite
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(test_module)
                
                # Run tests
                runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
                result = runner.run(suite)
                
                # Store results
                task_results[module_name] = {
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                    'success': result.wasSuccessful()
                }
                
                self.total_tests += result.testsRun
                self.total_failures += len(result.failures)
                self.total_errors += len(result.errors)
                
            except ImportError as e:
                print(f"Could not import {module_name}: {e}")
                task_results[module_name] = {
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'skipped': 0,
                    'success': False,
                    'import_error': str(e)
                }
                self.total_errors += 1
        
        self.results['task_7_1'] = task_results
        return task_results
    
    def run_task_72_integration_tests(self):
        """Run Task 7.2 - Integration Testing"""
        print("\\n" + "="*100)
        print("TASK 7.2 - INTEGRATION TESTING")
        print("="*100)
        
        try:
            from tests.test_integration import run_integration_test_suite
            result = run_integration_test_suite()
            
            task_result = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success': result.wasSuccessful()
            }
            
            self.total_tests += result.testsRun
            self.total_failures += len(result.failures)
            self.total_errors += len(result.errors)
            
        except ImportError as e:
            print(f"Could not import integration tests: {e}")
            task_result = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success': False,
                'import_error': str(e)
            }
            self.total_errors += 1
        
        self.results['task_7_2'] = task_result
        return task_result
    
    def run_task_73_performance_tests(self):
        """Run Task 7.3 - Performance Testing"""
        print("\\n" + "="*100)
        print("TASK 7.3 - PERFORMANCE TESTING")
        print("="*100)
        
        try:
            from tests.test_performance import TestCPUOverhead, TestMemoryUsage, TestRefreshRateTesting, TestGPUAccuracyValidation
            
            # Create test suite
            suite = unittest.TestSuite()
            suite.addTest(unittest.makeSuite(TestCPUOverhead))
            suite.addTest(unittest.makeSuite(TestMemoryUsage))
            suite.addTest(unittest.makeSuite(TestRefreshRateTesting))
            suite.addTest(unittest.makeSuite(TestGPUAccuracyValidation))
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)
            
            task_result = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success': result.wasSuccessful()
            }
            
            self.total_tests += result.testsRun
            self.total_failures += len(result.failures)
            self.total_errors += len(result.errors)
            
        except ImportError as e:
            print(f"Could not import performance tests: {e}")
            task_result = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success': False,
                'import_error': str(e)
            }
            self.total_errors += 1
        
        self.results['task_7_3'] = task_result
        return task_result
    
    def run_task_74_platform_tests(self):
        """Run Task 7.4 - Platform Testing"""
        print("\\n" + "="*100)
        print("TASK 7.4 - PLATFORM TESTING")
        print("="*100)
        
        try:
            from tests.test_platform import run_platform_test_suite
            result = run_platform_test_suite()
            
            task_result = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success': result.wasSuccessful()
            }
            
            self.total_tests += result.testsRun
            self.total_failures += len(result.failures)
            self.total_errors += len(result.errors)
            
        except ImportError as e:
            print(f"Could not import platform tests: {e}")
            task_result = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success': False,
                'import_error': str(e)
            }
            self.total_errors += 1
        
        self.results['task_7_4'] = task_result
        return task_result
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\\n" + "="*100)
        print("COMPREHENSIVE TEST REPORT")
        print("="*100)
        
        # Overall statistics
        print(f"\\nOVERALL STATISTICS")
        print("-" * 50)
        print(f"Total Tests Run:      {self.total_tests:5d}")
        print(f"Total Failures:       {self.total_failures:5d}")
        print(f"Total Errors:         {self.total_errors:5d}")
        
        if self.total_tests > 0:
            success_rate = ((self.total_tests - self.total_failures - self.total_errors) / self.total_tests) * 100
            print(f"Overall Success Rate: {success_rate:5.1f}%")
        else:
            print(f"Overall Success Rate:   N/A")
        
        # Task-by-task breakdown
        print(f"\\nTASK BREAKDOWN")
        print("-" * 50)
        
        task_names = {
            'task_7_1': 'Task 7.1 - Unit Testing',
            'task_7_2': 'Task 7.2 - Integration Testing', 
            'task_7_3': 'Task 7.3 - Performance Testing',
            'task_7_4': 'Task 7.4 - Platform Testing'
        }
        
        for task_id, task_name in task_names.items():
            if task_id in self.results:
                result = self.results[task_id]
                
                if isinstance(result, dict) and 'tests_run' in result:
                    # Single task result
                    tests = result['tests_run']
                    failures = result['failures']
                    errors = result['errors']
                    success = "PASS" if result['success'] else "FAIL"
                    
                    if tests > 0:
                        rate = ((tests - failures - errors) / tests) * 100
                        print(f"{task_name:35} | {tests:3d} tests | {rate:5.1f}% | {success}")
                    else:
                        print(f"{task_name:35} | {tests:3d} tests |   N/A | {success}")
                        
                else:
                    # Multiple subtask results (Task 7.1)
                    total_tests = sum(r.get('tests_run', 0) for r in result.values())
                    total_failures = sum(r.get('failures', 0) for r in result.values())
                    total_errors = sum(r.get('errors', 0) for r in result.values())
                    
                    if total_tests > 0:
                        rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
                        success = "PASS" if total_failures == 0 and total_errors == 0 else "FAIL"
                        print(f"{task_name:35} | {total_tests:3d} tests | {rate:5.1f}% | {success}")
                    else:
                        print(f"{task_name:35} |   0 tests |   N/A | SKIP")
            else:
                print(f"{task_name:35} |   - tests |   N/A | SKIP")
        
        # Detailed failure analysis
        print(f"\\nFAILURE ANALYSIS")
        print("-" * 50)
        
        has_failures = False
        for task_id, task_name in task_names.items():
            if task_id in self.results:
                result = self.results[task_id]
                
                if isinstance(result, dict) and 'import_error' in result:
                    print(f"{task_name}: Import Error - {result['import_error']}")
                    has_failures = True
                elif isinstance(result, dict) and (result.get('failures', 0) > 0 or result.get('errors', 0) > 0):
                    failures = result.get('failures', 0)
                    errors = result.get('errors', 0)
                    print(f"{task_name}: {failures} failures, {errors} errors")
                    has_failures = True
                elif isinstance(result, dict):
                    # Check subtasks
                    for subtask, subresult in result.items():
                        if isinstance(subresult, dict):
                            if 'import_error' in subresult:
                                print(f"{task_name} ({subtask}): Import Error - {subresult['import_error']}")
                                has_failures = True
                            elif subresult.get('failures', 0) > 0 or subresult.get('errors', 0) > 0:
                                failures = subresult.get('failures', 0)
                                errors = subresult.get('errors', 0)
                                print(f"{task_name} ({subtask}): {failures} failures, {errors} errors")
                                has_failures = True
        
        if not has_failures:
            print("No failures detected!")
        
        # Recommendations
        print(f"\\nRECOMMENDATIONS")
        print("-" * 50)
        
        if self.total_errors > 0:
            print("- Address import errors by installing missing dependencies")
            print("- Implement missing backend modules")
        
        if self.total_failures > 0:
            print("- Review and fix failing test cases")
            print("- Check system compatibility and requirements")
        
        if self.total_tests == 0:
            print("- Ensure test modules can be imported")
            print("- Check Python path and module structure")
        
        # Success criteria
        print(f"\\nSUCCESS CRITERIA")
        print("-" * 50)
        
        criteria = [
            ("Unit tests pass", self.results.get('task_7_1', {})),
            ("Integration tests pass", self.results.get('task_7_2', {})),
            ("Performance tests pass", self.results.get('task_7_3', {})),
            ("Platform tests pass", self.results.get('task_7_4', {}))
        ]
        
        all_passed = True
        for criterion, result in criteria:
            if isinstance(result, dict) and 'success' in result:
                status = "✓ PASS" if result['success'] else "✗ FAIL"
                if not result['success']:
                    all_passed = False
            elif isinstance(result, dict):
                # Multiple subtasks
                subtask_success = all(r.get('success', False) for r in result.values() if isinstance(r, dict))
                status = "✓ PASS" if subtask_success else "✗ FAIL"
                if not subtask_success:
                    all_passed = False
            else:
                status = "- SKIP"
            
            print(f"{criterion:25} | {status}")
        
        print(f"\\nPHASE 7 STATUS: {'✓ COMPLETE' if all_passed else '⚠ NEEDS ATTENTION'}")
        
        return all_passed
    
    def save_results_json(self):
        """Save test results to JSON file"""
        results_file = self.test_dir / 'test_results.json'
        
        try:
            report_data = {
                'timestamp': time.time(),
                'platform': platform.platform(),
                'python_version': sys.version.split()[0],
                'total_tests': self.total_tests,
                'total_failures': self.total_failures,
                'total_errors': self.total_errors,
                'success_rate': ((self.total_tests - self.total_failures - self.total_errors) / self.total_tests * 100) if self.total_tests > 0 else 0,
                'tasks': self.results
            }
            
            with open(results_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\\nTest results saved to: {results_file}")
            
        except Exception as e:
            print(f"\\nCould not save results to JSON: {e}")
    
    def run_all_tests(self):
        """Run all Phase 7 tests"""
        start_time = time.time()
        
        # Print header
        self.print_header()
        
        # Check dependencies and environment
        deps_ok = self.check_dependencies()
        backend_ok = self.check_backend_modules()
        chrome_ok = self.check_chrome_app()
        
        if not deps_ok:
            print("\\nCritical dependencies missing. Aborting test run.")
            return False
        
        # Run all test tasks
        print("\\nRunning all Phase 7 test tasks...")
        
        self.run_task_71_unit_tests()
        self.run_task_72_integration_tests()
        self.run_task_73_performance_tests()
        self.run_task_74_platform_tests()
        
        # Generate comprehensive report
        success = self.generate_comprehensive_report()
        
        # Save results
        self.save_results_json()
        
        # Final summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\\n" + "="*100)
        print(f"PHASE 7 TESTING COMPLETED IN {duration:.1f} SECONDS")
        print(f"OVERALL RESULT: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
        print("="*100)
        
        return success


def main():
    """Main entry point"""
    runner = TestSuiteRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
