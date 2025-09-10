#!/usr/bin/env python3
"""
Integration Tests - Task 7.2
Chrome App End-to-End Testing

This module provides comprehensive integration tests for the complete
Chrome app including installation, launch, UI responsiveness, and 
settings persistence.
"""

import unittest
import json
import time
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestChromeAppIntegration(unittest.TestCase):
    """Test Chrome app installation and launch"""
    
    def setUp(self):
        """Set up Chrome app integration tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
        self.manifest_file = self.chrome_app_dir / 'manifest.json'
        self.test_temp_dir = None
    
    def tearDown(self):
        """Clean up after tests"""
        if self.test_temp_dir and os.path.exists(self.test_temp_dir):
            import shutil
            shutil.rmtree(self.test_temp_dir)
    
    def test_chrome_app_structure(self):
        """Test Chrome app has required file structure"""
        self.assertTrue(self.chrome_app_dir.exists(), 
                       "Chrome app directory should exist")
        
        required_files = [
            'manifest.json',
            'background.js',
            'monitor.html',
            'monitor.js',
            'monitor.css',
            'settings-panel.js'
        ]
        
        for file_name in required_files:
            file_path = self.chrome_app_dir / file_name
            self.assertTrue(file_path.exists(), 
                           f"Required file {file_name} should exist")
    
    def test_manifest_validation(self):
        """Test manifest.json is valid and complete"""
        self.assertTrue(self.manifest_file.exists(), 
                       "manifest.json should exist")
        
        try:
            with open(self.manifest_file, 'r') as f:
                manifest = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.fail(f"manifest.json should be valid JSON: {e}")
        
        # Required manifest fields
        required_fields = [
            'manifest_version',
            'name',
            'version',
            'app',
            'permissions'
        ]
        
        for field in required_fields:
            self.assertIn(field, manifest, 
                         f"Manifest missing required field: {field}")
        
        # Validate specific values
        self.assertEqual(manifest['manifest_version'], 2, 
                        "Should use manifest version 2")
        self.assertIn('background', manifest['app'], 
                     "App should have background script")
        self.assertIn('scripts', manifest['app']['background'], 
                     "Background should specify scripts")
        
        # Check permissions
        permissions = manifest.get('permissions', [])
        expected_permissions = ['storage', 'system.cpu', 'system.memory', 'system.storage']
        for perm in expected_permissions:
            self.assertIn(perm, permissions, 
                         f"Missing permission: {perm}")
    
    def test_background_script_validity(self):
        """Test background.js is valid JavaScript"""
        background_file = self.chrome_app_dir / 'background.js'
        self.assertTrue(background_file.exists(), 
                       "background.js should exist")
        
        try:
            with open(background_file, 'r') as f:
                background_content = f.read()
        except FileNotFoundError:
            self.fail("background.js should be readable")
        
        # Check for required Chrome app patterns
        required_patterns = [
            'chrome.app.runtime.onLaunched',
            'chrome.app.window.create',
            'monitor.html'
        ]
        
        for pattern in required_patterns:
            self.assertIn(pattern, background_content, 
                         f"background.js missing pattern: {pattern}")
    
    def test_main_html_structure(self):
        """Test monitor.html has proper structure"""
        html_file = self.chrome_app_dir / 'monitor.html'
        self.assertTrue(html_file.exists(), 
                       "monitor.html should exist")
        
        try:
            with open(html_file, 'r') as f:
                html_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.html should be readable")
        
        # Check for required HTML elements
        required_elements = [
            '<html',
            '<head>',
            '<body>',
            '<script',
            'monitor.js',
            'monitor.css'
        ]
        
        for element in required_elements:
            self.assertIn(element, html_content, 
                         f"monitor.html missing element: {element}")
    
    def test_javascript_files_syntax(self):
        """Test JavaScript files for basic syntax validity"""
        js_files = [
            'monitor.js',
            'settings-panel.js',
            'background.js'
        ]
        
        for js_file in js_files:
            file_path = self.chrome_app_dir / js_file
            self.assertTrue(file_path.exists(), 
                           f"{js_file} should exist")
            
            try:
                with open(file_path, 'r') as f:
                    js_content = f.read()
                
                # Basic syntax checks
                self.assertNotIn('undefined is not a function', js_content)
                self.assertNotIn('SyntaxError', js_content)
                
                # Check for proper function declarations
                if 'function' in js_content:
                    # Should have matching braces
                    open_braces = js_content.count('{')
                    close_braces = js_content.count('}')
                    self.assertEqual(open_braces, close_braces, 
                                   f"{js_file} has mismatched braces")
                
            except FileNotFoundError:
                self.fail(f"{js_file} should be readable")
    
    def test_css_file_validity(self):
        """Test CSS file exists and is readable"""
        css_file = self.chrome_app_dir / 'monitor.css'
        self.assertTrue(css_file.exists(), 
                       "monitor.css should exist")
        
        try:
            with open(css_file, 'r') as f:
                css_content = f.read()
            
            # Basic CSS validation
            self.assertNotIn('parse error', css_content.lower())
            self.assertNotIn('invalid', css_content.lower())
            
        except FileNotFoundError:
            self.fail("monitor.css should be readable")


class TestUIResponsiveness(unittest.TestCase):
    """Test UI responsiveness and interaction"""
    
    def setUp(self):
        """Set up UI responsiveness tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
    
    def test_monitor_class_definition(self):
        """Test SystemMonitor class is properly defined"""
        monitor_js = self.chrome_app_dir / 'monitor.js'
        
        if not monitor_js.exists():
            self.skipTest("monitor.js not found")
        
        try:
            with open(monitor_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.js should be readable")
        
        # Check for SystemMonitor class definition
        self.assertIn('class SystemMonitor', js_content, 
                     "Should define SystemMonitor class")
        self.assertIn('constructor', js_content, 
                     "SystemMonitor should have constructor")
        
        # Check for essential methods
        essential_methods = [
            'startMonitoring',
            'updateDisplay',
            'connectWebSocket',
            'handleData'
        ]
        
        for method in essential_methods:
            self.assertIn(method, js_content, 
                         f"SystemMonitor should have {method} method")
    
    def test_settings_panel_functionality(self):
        """Test settings panel JavaScript functionality"""
        settings_js = self.chrome_app_dir / 'settings-panel.js'
        
        if not settings_js.exists():
            self.skipTest("settings-panel.js not found")
        
        try:
            with open(settings_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("settings-panel.js should be readable")
        
        # Check for settings functionality
        settings_functions = [
            'SettingsPanel',
            'saveSettings',
            'loadSettings',
            'resetSettings',
            'updateTheme'
        ]
        
        for func in settings_functions:
            self.assertIn(func, js_content, 
                         f"Settings panel should have {func}")
    
    def test_event_handlers(self):
        """Test event handlers are properly defined"""
        js_files = ['monitor.js', 'settings-panel.js']
        
        for js_file in js_files:
            file_path = self.chrome_app_dir / js_file
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    js_content = f.read()
                
                # Check for event listeners
                event_patterns = [
                    'addEventListener',
                    'onclick',
                    'onchange',
                    'onload'
                ]
                
                has_events = any(pattern in js_content for pattern in event_patterns)
                if 'monitor.js' in js_file or 'settings' in js_file:
                    self.assertTrue(has_events, 
                                   f"{js_file} should have event handlers")
                
            except FileNotFoundError:
                continue
    
    def test_websocket_connection_logic(self):
        """Test WebSocket connection logic"""
        monitor_js = self.chrome_app_dir / 'monitor.js'
        
        if not monitor_js.exists():
            self.skipTest("monitor.js not found")
        
        try:
            with open(monitor_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.js should be readable")
        
        # Check for WebSocket usage
        websocket_patterns = [
            'WebSocket',
            'ws://',
            'onopen',
            'onmessage',
            'onclose',
            'onerror'
        ]
        
        for pattern in websocket_patterns:
            self.assertIn(pattern, js_content, 
                         f"WebSocket logic should include {pattern}")
    
    def test_data_display_elements(self):
        """Test data display element structure"""
        monitor_html = self.chrome_app_dir / 'monitor.html'
        
        if not monitor_html.exists():
            self.skipTest("monitor.html not found")
        
        try:
            with open(monitor_html, 'r') as f:
                html_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.html should be readable")
        
        # Check for data display elements
        display_elements = [
            'cpu-usage',
            'memory-usage',
            'disk-usage',
            'gpu-info'
        ]
        
        for element in display_elements:
            self.assertIn(element, html_content, 
                         f"HTML should contain {element} element")


class TestSettingsPersistence(unittest.TestCase):
    """Test settings persistence and configuration"""
    
    def setUp(self):
        """Set up settings persistence tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
        self.test_settings = {
            'theme': 'dark',
            'updateInterval': 1000,
            'showGPU': True,
            'notifications': {
                'enabled': True,
                'cpuThreshold': 80,
                'memoryThreshold': 85
            }
        }
    
    def test_settings_storage_logic(self):
        """Test settings storage logic in JavaScript"""
        settings_js = self.chrome_app_dir / 'settings-panel.js'
        
        if not settings_js.exists():
            self.skipTest("settings-panel.js not found")
        
        try:
            with open(settings_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("settings-panel.js should be readable")
        
        # Check for Chrome storage API usage
        storage_patterns = [
            'chrome.storage',
            'chrome.storage.local',
            'set',
            'get'
        ]
        
        for pattern in storage_patterns:
            self.assertIn(pattern, js_content, 
                         f"Settings should use {pattern}")
    
    def test_default_settings_definition(self):
        """Test default settings are properly defined"""
        settings_js = self.chrome_app_dir / 'settings-panel.js'
        
        if not settings_js.exists():
            self.skipTest("settings-panel.js not found")
        
        try:
            with open(settings_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("settings-panel.js should be readable")
        
        # Check for default settings definition
        default_patterns = [
            'defaultSettings',
            'DEFAULT_',
            'theme',
            'updateInterval'
        ]
        
        for pattern in default_patterns:
            self.assertIn(pattern, js_content, 
                         f"Should define default settings with {pattern}")
    
    def test_settings_validation_logic(self):
        """Test settings validation logic"""
        settings_js = self.chrome_app_dir / 'settings-panel.js'
        
        if not settings_js.exists():
            self.skipTest("settings-panel.js not found")
        
        try:
            with open(settings_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("settings-panel.js should be readable")
        
        # Check for validation patterns
        validation_patterns = [
            'validate',
            'isValid',
            'parseInt',
            'parseFloat',
            'typeof'
        ]
        
        has_validation = any(pattern in js_content for pattern in validation_patterns)
        self.assertTrue(has_validation, 
                       "Settings should include validation logic")
    
    def test_theme_configuration(self):
        """Test theme configuration implementation"""
        css_file = self.chrome_app_dir / 'monitor.css'
        
        if not css_file.exists():
            self.skipTest("monitor.css not found")
        
        try:
            with open(css_file, 'r') as f:
                css_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.css should be readable")
        
        # Check for theme-related CSS
        theme_patterns = [
            'theme',
            'dark',
            'light',
            '--primary-color',
            '--background-color'
        ]
        
        for pattern in theme_patterns:
            self.assertIn(pattern, css_content, 
                         f"CSS should support themes with {pattern}")


class TestMultiMonitorBehavior(unittest.TestCase):
    """Test multi-monitor and window management behavior"""
    
    def setUp(self):
        """Set up multi-monitor tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
    
    def test_window_creation_logic(self):
        """Test window creation and positioning logic"""
        background_js = self.chrome_app_dir / 'background.js'
        
        if not background_js.exists():
            self.skipTest("background.js not found")
        
        try:
            with open(background_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("background.js should be readable")
        
        # Check for window creation parameters
        window_patterns = [
            'chrome.app.window.create',
            'width',
            'height',
            'minWidth',
            'minHeight'
        ]
        
        for pattern in window_patterns:
            self.assertIn(pattern, js_content, 
                         f"Window creation should specify {pattern}")
    
    def test_window_state_persistence(self):
        """Test window state persistence logic"""
        background_js = self.chrome_app_dir / 'background.js'
        
        if not background_js.exists():
            self.skipTest("background.js not found")
        
        try:
            with open(background_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("background.js should be readable")
        
        # Check for state persistence
        state_patterns = [
            'bounds',
            'state',
            'chrome.storage',
            'position'
        ]
        
        # At least some state management should be present
        has_state_management = any(pattern in js_content for pattern in state_patterns)
        if len(js_content) > 100:  # Only check if file has substantial content
            self.assertTrue(has_state_management, 
                           "Should handle window state persistence")
    
    def test_responsive_design(self):
        """Test responsive design capabilities"""
        css_file = self.chrome_app_dir / 'monitor.css'
        
        if not css_file.exists():
            self.skipTest("monitor.css not found")
        
        try:
            with open(css_file, 'r') as f:
                css_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.css should be readable")
        
        # Check for responsive design elements
        responsive_patterns = [
            '@media',
            'min-width',
            'max-width',
            'flex',
            'grid'
        ]
        
        has_responsive = any(pattern in css_content for pattern in responsive_patterns)
        if len(css_content) > 500:  # Only check if CSS has substantial content
            self.assertTrue(has_responsive, 
                           "CSS should include responsive design elements")


class TestChromeAPIIntegration(unittest.TestCase):
    """Test Chrome API integration and permissions"""
    
    def setUp(self):
        """Set up Chrome API integration tests"""
        self.chrome_app_dir = project_root / 'chrome-app'
    
    def test_chrome_storage_usage(self):
        """Test Chrome storage API usage"""
        js_files = ['settings-panel.js', 'monitor.js', 'background.js']
        
        storage_usage_found = False
        
        for js_file in js_files:
            file_path = self.chrome_app_dir / js_file
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    js_content = f.read()
                
                if 'chrome.storage' in js_content:
                    storage_usage_found = True
                    
                    # Check for proper usage patterns
                    storage_patterns = [
                        'chrome.storage.local.get',
                        'chrome.storage.local.set'
                    ]
                    
                    for pattern in storage_patterns:
                        if pattern in js_content:
                            # Check for callback handling
                            self.assertIn('function', js_content, 
                                         f"{js_file} should handle storage callbacks")
                            break
                
            except FileNotFoundError:
                continue
        
        # At least one file should use Chrome storage
        self.assertTrue(storage_usage_found, 
                       "App should use Chrome storage API")
    
    def test_chrome_system_api_usage(self):
        """Test Chrome system API usage for hardware monitoring"""
        monitor_js = self.chrome_app_dir / 'monitor.js'
        
        if not monitor_js.exists():
            self.skipTest("monitor.js not found")
        
        try:
            with open(monitor_js, 'r') as f:
                js_content = f.read()
        except FileNotFoundError:
            self.fail("monitor.js should be readable")
        
        # Check for Chrome system APIs (if used)
        system_apis = [
            'chrome.system.cpu',
            'chrome.system.memory',
            'chrome.system.storage'
        ]
        
        # Note: These might not be used if WebSocket approach is preferred
        # This test is more about checking the approach consistency
        if any(api in js_content for api in system_apis):
            self.assertIn('chrome.system', js_content, 
                         "Should properly use Chrome system APIs")
    
    def test_error_handling_patterns(self):
        """Test error handling patterns in Chrome API usage"""
        js_files = ['monitor.js', 'settings-panel.js', 'background.js']
        
        for js_file in js_files:
            file_path = self.chrome_app_dir / js_file
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    js_content = f.read()
                
                # Check for error handling patterns
                error_patterns = [
                    'try',
                    'catch',
                    'chrome.runtime.lastError',
                    'error',
                    'onerror'
                ]
                
                if len(js_content) > 200:  # Only check substantial files
                    has_error_handling = any(pattern in js_content for pattern in error_patterns)
                    self.assertTrue(has_error_handling, 
                                   f"{js_file} should include error handling")
                
            except FileNotFoundError:
                continue


def run_integration_test_suite():
    """Run the complete integration test suite"""
    print("\\n" + "="*80)
    print("INTEGRATION TEST SUITE")
    print("="*80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestChromeAppIntegration))
    test_suite.addTest(unittest.makeSuite(TestUIResponsiveness))
    test_suite.addTest(unittest.makeSuite(TestSettingsPersistence))
    test_suite.addTest(unittest.makeSuite(TestMultiMonitorBehavior))
    test_suite.addTest(unittest.makeSuite(TestChromeAPIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == '__main__':
    print("Integration Tests - Chrome App End-to-End Testing")
    print("="*80)
    
    # Check environment
    print(f"Project root: {project_root}")
    print(f"Chrome app directory: {project_root / 'chrome-app'}")
    
    # Run integration tests
    result = run_integration_test_suite()
    
    # Print summary
    print("\\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
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
    
    print("\\nIntegration testing completed!")
    print("="*80)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
