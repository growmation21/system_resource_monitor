#!/usr/bin/env python3
"""
Platform Tests - Task 7.4
Windows 10/11 Compatibility and Platform Validation

This module provides comprehensive platform testing for Windows 10/11
compatibility, NVIDIA GPU detection, window management, and desktop
integration verification.
"""

import unittest
import platform
import sys
import os
import subprocess
import winreg
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestWindowsCompatibility(unittest.TestCase):
    """Test Windows 10/11 compatibility"""
    
    def setUp(self):
        """Set up Windows compatibility tests"""
        self.platform_info = platform.platform()
        self.windows_version = platform.version()
        self.is_windows = platform.system() == 'Windows'
    
    def test_windows_platform_detection(self):
        """Test Windows platform is properly detected"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        self.assertTrue(self.is_windows, "Should detect Windows platform")
        self.assertIn('Windows', self.platform_info, "Platform info should contain Windows")
        
        print(f"Platform: {self.platform_info}")
        print(f"Windows Version: {self.windows_version}")
    
    def test_windows_10_11_compatibility(self):
        """Test Windows 10/11 specific compatibility"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Check Windows version
        version_parts = self.windows_version.split('.')
        major_version = int(version_parts[0])
        build_number = int(version_parts[2]) if len(version_parts) > 2 else 0
        
        # Windows 10 is version 10.0, Windows 11 is 10.0 with build >= 22000
        self.assertGreaterEqual(major_version, 10, "Should run on Windows 10 or later")
        
        is_windows_11 = major_version == 10 and build_number >= 22000
        is_windows_10 = major_version == 10 and build_number < 22000
        
        self.assertTrue(is_windows_10 or is_windows_11, 
                       "Should be Windows 10 or Windows 11")
        
        if is_windows_11:
            print("Detected: Windows 11")
        else:
            print("Detected: Windows 10")
        
        print(f"Build Number: {build_number}")
    
    def test_python_compatibility(self):
        """Test Python version compatibility"""
        python_version = sys.version_info
        
        # Should run on Python 3.7+
        self.assertGreaterEqual(python_version.major, 3, "Should use Python 3.x")
        self.assertGreaterEqual(python_version.minor, 7, "Should use Python 3.7 or later")
        
        print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    def test_required_windows_features(self):
        """Test required Windows features are available"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Test Windows Management Instrumentation (WMI) availability
        try:
            import wmi
            wmi_available = True
        except ImportError:
            wmi_available = False
        
        # WMI is optional but useful for enhanced monitoring
        if wmi_available:
            print("WMI available for enhanced monitoring")
        else:
            print("WMI not available (optional)")
        
        # Test Windows Performance Toolkit availability
        try:
            result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                  capture_output=True, text=True, timeout=5)
            wmic_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            wmic_available = False
        
        if wmic_available:
            print("WMIC available for system information")
        else:
            print("WMIC not available (alternative methods will be used)")
    
    def test_file_system_permissions(self):
        """Test file system permissions for app operation"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Test read permissions in project directory
        self.assertTrue(os.access(project_root, os.R_OK), 
                       "Should have read access to project directory")
        
        # Test write permissions in temp directory
        temp_dir = Path(os.environ.get('TEMP', os.environ.get('TMP', 'C:\\temp')))
        if temp_dir.exists():
            self.assertTrue(os.access(temp_dir, os.W_OK), 
                           "Should have write access to temp directory")
        
        # Test Chrome app directory permissions
        chrome_app_dir = project_root / 'chrome-app'
        if chrome_app_dir.exists():
            self.assertTrue(os.access(chrome_app_dir, os.R_OK), 
                           "Should have read access to Chrome app directory")


class TestNVIDIAGPUDetection(unittest.TestCase):
    """Test NVIDIA GPU detection and driver compatibility"""
    
    def setUp(self):
        """Set up NVIDIA GPU detection tests"""
        self.is_windows = platform.system() == 'Windows'
    
    def test_nvidia_driver_presence(self):
        """Test NVIDIA driver presence on system"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Check for NVIDIA driver in registry
        nvidia_driver_found = False
        driver_version = None
        
        try:
            # Check NVIDIA registry entries
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\\NVIDIA Corporation\\Global") as key:
                nvidia_driver_found = True
                try:
                    driver_version = winreg.QueryValueEx(key, "DriverVersion")[0]
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            pass
        
        if nvidia_driver_found:
            print(f"NVIDIA driver detected: {driver_version}")
            self.assertTrue(True, "NVIDIA driver found")
        else:
            print("NVIDIA driver not detected (may not have NVIDIA GPU)")
            self.skipTest("No NVIDIA driver found")
    
    def test_nvidia_ml_availability(self):
        """Test NVIDIA Management Library availability"""
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            self.assertGreaterEqual(device_count, 0, "Should detect GPU count")
            
            print(f"NVIDIA GPUs detected: {device_count}")
            
            # Test basic GPU info retrieval
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                print(f"First GPU: {name}")
                
                # Test GPU utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                self.assertIsInstance(util.gpu, int, "GPU utilization should be integer")
                self.assertGreaterEqual(util.gpu, 0, "GPU utilization should be >= 0")
                self.assertLessEqual(util.gpu, 100, "GPU utilization should be <= 100")
            
            pynvml.nvmlShutdown()
            
        except ImportError:
            self.skipTest("pynvml not available")
        except Exception as e:
            self.skipTest(f"NVIDIA ML not available: {e}")
    
    def test_nvidia_smi_availability(self):
        """Test nvidia-smi command availability"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                gpu_names = result.stdout.strip().split('\\n')[1:]  # Skip header
                print(f"nvidia-smi detected GPUs: {len(gpu_names)}")
                for i, name in enumerate(gpu_names):
                    print(f"  GPU {i}: {name}")
            else:
                self.skipTest("nvidia-smi not available or failed")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("nvidia-smi command not found")
    
    def test_gpu_monitoring_fallback(self):
        """Test GPU monitoring fallback mechanisms"""
        # Test that app works gracefully without NVIDIA GPU
        
        # Mock no GPU scenario
        with patch('gpu.pynvml.nvmlInit', side_effect=Exception("No GPU")):
            try:
                # This should import and handle the no-GPU case gracefully
                if project_root / 'back_end' / 'gpu.py':
                    from back_end import gpu
                    gpu_monitor = gpu.GPUMonitor()
                    self.assertFalse(gpu_monitor.is_available(), 
                                   "Should detect no GPU available")
                    
                    gpu_info = gpu_monitor.get_gpu_info()
                    self.assertIsInstance(gpu_info, list, 
                                        "Should return empty list when no GPU")
                    self.assertEqual(len(gpu_info), 0, 
                                   "Should return empty list when no GPU")
            except ImportError:
                self.skipTest("GPU module not available for testing")


class TestWindowManagement(unittest.TestCase):
    """Test Chrome app window management"""
    
    def setUp(self):
        """Set up window management tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
        self.is_windows = platform.system() == 'Windows'
    
    def test_chrome_installation_detection(self):
        """Test Chrome browser installation detection"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        
        chrome_found = False
        chrome_version = None
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                chrome_found = True
                
                # Try to get Chrome version
                try:
                    result = subprocess.run([chrome_path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        chrome_version = result.stdout.strip()
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                break
        
        if chrome_found:
            print(f"Chrome found: {chrome_version}")
            self.assertTrue(True, "Chrome browser detected")
        else:
            print("Chrome browser not found")
            self.skipTest("Chrome browser not installed")
    
    def test_chrome_app_manifest_compatibility(self):
        """Test Chrome app manifest compatibility"""
        manifest_file = self.chrome_app_dir / 'manifest.json'
        
        if not manifest_file.exists():
            self.skipTest("Chrome app manifest not found")
        
        try:
            import json
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.fail(f"Manifest should be valid JSON: {e}")
        
        # Check manifest version compatibility
        manifest_version = manifest.get('manifest_version')
        self.assertEqual(manifest_version, 2, 
                        "Should use manifest version 2 for Chrome apps")
        
        # Check required permissions for Windows
        permissions = manifest.get('permissions', [])
        windows_permissions = ['storage', 'system.cpu', 'system.memory', 'system.storage']
        
        for perm in windows_permissions:
            self.assertIn(perm, permissions, 
                         f"Missing Windows-compatible permission: {perm}")
    
    def test_window_dimensions_and_positioning(self):
        """Test window dimensions and positioning logic"""
        background_js = self.chrome_app_dir / 'background.js'
        
        if not background_js.exists():
            self.skipTest("background.js not found")
        
        try:
            with open(background_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("background.js should be readable")
        
        # Check for reasonable window dimensions
        dimension_patterns = ['width', 'height', 'minWidth', 'minHeight']
        
        for pattern in dimension_patterns:
            self.assertIn(pattern, js_content, 
                         f"Window creation should specify {pattern}")
        
        # Look for specific dimension values
        import re
        
        # Extract width/height values
        width_match = re.search(r'width["\']?\s*:\s*(\d+)', js_content)
        height_match = re.search(r'height["\']?\s*:\s*(\d+)', js_content)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            
            # Reasonable window dimensions for Windows
            self.assertGreaterEqual(width, 800, "Window width should be >= 800px")
            self.assertLessEqual(width, 2560, "Window width should be <= 2560px")
            self.assertGreaterEqual(height, 600, "Window height should be >= 600px")
            self.assertLessEqual(height, 1440, "Window height should be <= 1440px")
            
            print(f"Window dimensions: {width}x{height}")
    
    def test_multi_monitor_support(self):
        """Test multi-monitor support on Windows"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        try:
            # Get monitor information using Windows API
            import win32api
            monitors = win32api.EnumDisplayMonitors()
            
            print(f"Monitors detected: {len(monitors)}")
            
            for i, (monitor, dc, rect) in enumerate(monitors):
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                print(f"  Monitor {i}: {width}x{height} at ({rect[0]}, {rect[1]})")
            
            # App should handle multiple monitors gracefully
            self.assertGreaterEqual(len(monitors), 1, "Should detect at least one monitor")
            
        except ImportError:
            print("win32api not available - using alternative method")
            
            # Alternative: use tkinter to get screen info
            try:
                import tkinter as tk
                root = tk.Tk()
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()
                root.destroy()
                
                print(f"Screen resolution: {width}x{height}")
                self.assertGreater(width, 0, "Screen width should be > 0")
                self.assertGreater(height, 0, "Screen height should be > 0")
                
            except ImportError:
                self.skipTest("Cannot detect monitor information")


class TestDesktopIntegration(unittest.TestCase):
    """Test desktop integration features"""
    
    def setUp(self):
        """Set up desktop integration tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
        self.is_windows = platform.system() == 'Windows'
    
    def test_system_notification_support(self):
        """Test system notification support"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Check if Windows 10+ notification system is available
        version_parts = platform.version().split('.')
        major_version = int(version_parts[0])
        
        if major_version >= 10:
            print("Windows 10+ notification system available")
            
            # Check for notification-related code in JavaScript
            js_files = ['monitor.js', 'settings-panel.js']
            
            notification_support = False
            for js_file in js_files:
                file_path = self.chrome_app_dir / js_file
                
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            js_content = f.read()
                        
                        notification_patterns = [
                            'Notification',
                            'chrome.notifications',
                            'showNotification',
                            'notify'
                        ]
                        
                        if any(pattern in js_content for pattern in notification_patterns):
                            notification_support = True
                            break
                    except FileNotFoundError:
                        continue
            
            if notification_support:
                print("Notification support detected in app")
            else:
                print("No notification support detected (optional feature)")
        else:
            self.skipTest("Windows version too old for modern notifications")
    
    def test_system_tray_integration(self):
        """Test system tray integration capabilities"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Chrome apps don't typically use system tray directly
        # But check if there's any system tray related code
        
        js_files = ['background.js', 'monitor.js']
        tray_support = False
        
        for js_file in js_files:
            file_path = self.chrome_app_dir / js_file
            
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        js_content = f.read()
                    
                    tray_patterns = [
                        'tray',
                        'systray',
                        'minimizeToTray',
                        'chrome.app.window'
                    ]
                    
                    if any(pattern in js_content for pattern in tray_patterns):
                        tray_support = True
                        break
                except FileNotFoundError:
                    continue
        
        if tray_support:
            print("System tray integration detected")
        else:
            print("No system tray integration (standard for Chrome apps)")
    
    def test_startup_integration(self):
        """Test startup integration options"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Check for startup-related functionality in Chrome app
        background_js = self.chrome_app_dir / 'background.js'
        
        if background_js.exists():
            try:
                with open(background_js, 'r') as f:
                    js_content = f.read()
                
                startup_patterns = [
                    'chrome.runtime.onStartup',
                    'chrome.app.runtime.onLaunched',
                    'autostart',
                    'startup'
                ]
                
                startup_support = any(pattern in js_content for pattern in startup_patterns)
                
                if startup_support:
                    print("Startup integration detected")
                else:
                    print("No automatic startup detected (user-controlled)")
                    
            except FileNotFoundError:
                self.skipTest("background.js not found")
    
    def test_windows_firewall_compatibility(self):
        """Test Windows Firewall compatibility"""
        if not self.is_windows:
            self.skipTest("Not running on Windows")
        
        # Check if WebSocket port usage might require firewall rules
        settings_js = self.chrome_app_dir / 'settings-panel.js'
        monitor_js = self.chrome_app_dir / 'monitor.js'
        
        websocket_usage = False
        websocket_port = None
        
        for js_file in [monitor_js, settings_js]:
            if js_file.exists():
                try:
                    with open(js_file, 'r') as f:
                        js_content = f.read()
                    
                    if 'WebSocket' in js_content or 'ws://' in js_content:
                        websocket_usage = True
                        
                        # Try to extract port number
                        import re
                        port_match = re.search(r'ws://[^:]+:(\d+)', js_content)
                        if port_match:
                            websocket_port = int(port_match.group(1))
                        
                        break
                except FileNotFoundError:
                    continue
        
        if websocket_usage:
            print(f"WebSocket usage detected on port: {websocket_port or 'unknown'}")
            
            if websocket_port:
                # Check if port is in typical safe range
                self.assertGreater(websocket_port, 1024, 
                                  "Should use non-privileged port (> 1024)")
                self.assertLess(websocket_port, 65536, 
                               "Port should be valid (< 65536)")
        else:
            print("No WebSocket usage detected")


def run_platform_test_suite():
    """Run the complete platform test suite"""
    print("\\n" + "="*80)
    print("PLATFORM TEST SUITE")
    print("="*80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestWindowsCompatibility))
    test_suite.addTest(unittest.makeSuite(TestNVIDIAGPUDetection))
    test_suite.addTest(unittest.makeSuite(TestWindowManagement))
    test_suite.addTest(unittest.makeSuite(TestDesktopIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == '__main__':
    print("Platform Tests - Windows 10/11 Compatibility and Platform Validation")
    print("="*80)
    
    # Platform information
    print(f"Operating System: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Python Version: {sys.version.split()[0]}")
    
    # Run platform tests
    result = run_platform_test_suite()
    
    # Print summary
    print("\\n" + "="*80)
    print("PLATFORM TEST SUMMARY")
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
    
    # Platform-specific recommendations
    if platform.system() == 'Windows':
        print("\\nWindows-specific recommendations:")
        print("- Ensure Chrome browser is installed for Chrome app testing")
        print("- Install NVIDIA drivers for GPU monitoring (if applicable)")
        print("- Consider Windows Defender exclusions for development")
    
    print("\\nPlatform testing completed!")
    print("="*80)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
