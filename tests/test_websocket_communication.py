#!/usr/bin/env python3
"""
WebSocket Communication Tests - Task 7.1
Real-time Data Transmission Testing

This module provides comprehensive tests for WebSocket communication
between the backend monitor and Chrome app frontend.
"""

import unittest
import asyncio
import websockets
import json
import time
import threading
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back_end import monitor

class TestWebSocketCommunication(unittest.TestCase):
    """Test cases for WebSocket communication functionality"""
    
    def setUp(self):
        """Set up WebSocket test fixtures"""
        self.monitor = monitor.SystemMonitor()
        self.test_port = 8765
        self.test_host = 'localhost'
        self.server = None
        self.client = None
    
    def tearDown(self):
        """Clean up after tests"""
        if self.server:
            self.server.close()
        if self.client:
            asyncio.get_event_loop().run_until_complete(self.client.close())
    
    def test_monitor_initialization(self):
        """Test SystemMonitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertTrue(hasattr(self.monitor, 'start_server'))
        self.assertTrue(hasattr(self.monitor, 'broadcast_data'))
        self.assertTrue(hasattr(self.monitor, 'get_system_data'))
    
    def test_system_data_format(self):
        """Test system data JSON format and structure"""
        system_data = self.monitor.get_system_data()
        
        self.assertIsInstance(system_data, dict)
        
        # Required top-level keys
        required_keys = ['timestamp', 'cpu', 'memory', 'disks', 'gpu']
        for key in required_keys:
            self.assertIn(key, system_data, f"Missing required key: {key}")
        
        # Validate timestamp
        self.assertIsInstance(system_data['timestamp'], (int, float))
        self.assertGreater(system_data['timestamp'], 0)
        
        # Validate CPU data
        cpu_data = system_data['cpu']
        self.assertIsInstance(cpu_data, dict)
        self.assertIn('percent', cpu_data)
        self.assertIn('count', cpu_data)
        self.assertIn('frequency', cpu_data)
        
        # Validate memory data
        memory_data = system_data['memory']
        self.assertIsInstance(memory_data, dict)
        self.assertIn('total', memory_data)
        self.assertIn('used', memory_data)
        self.assertIn('available', memory_data)
        self.assertIn('percent', memory_data)
        
        # Validate disk data
        disk_data = system_data['disks']
        self.assertIsInstance(disk_data, dict)
        
        # Validate GPU data
        gpu_data = system_data['gpu']
        self.assertIsInstance(gpu_data, list)
    
    def test_json_serialization(self):
        """Test JSON serialization of system data"""
        system_data = self.monitor.get_system_data()
        
        try:
            json_string = json.dumps(system_data)
            self.assertIsInstance(json_string, str)
            
            # Test deserialization
            parsed_data = json.loads(json_string)
            self.assertEqual(system_data, parsed_data)
            
        except (TypeError, ValueError) as e:
            self.fail(f"System data is not JSON serializable: {e}")
    
    @patch('websockets.serve')
    async def test_websocket_server_startup(self, mock_serve):
        """Test WebSocket server startup"""
        mock_server = AsyncMock()
        mock_serve.return_value = mock_server
        
        # Test server startup
        await self.monitor.start_server(self.test_host, self.test_port)
        
        # Verify serve was called with correct parameters
        mock_serve.assert_called_once()
        args, kwargs = mock_serve.call_args
        self.assertEqual(kwargs.get('host') or args[1], self.test_host)
        self.assertEqual(kwargs.get('port') or args[2], self.test_port)
    
    async def test_websocket_message_handling(self):
        """Test WebSocket message handling"""
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.recv = AsyncMock(return_value='{"type": "get_data"}')
        mock_websocket.send = AsyncMock()
        
        # Test message handling
        with patch.object(self.monitor, 'get_system_data') as mock_get_data:
            mock_get_data.return_value = {'test': 'data'}
            
            await self.monitor.handle_client(mock_websocket, "/")
            
            # Verify data was sent
            mock_websocket.send.assert_called()
            sent_data = mock_websocket.send.call_args[0][0]
            self.assertIsInstance(sent_data, str)
            
            # Verify it's valid JSON
            parsed_data = json.loads(sent_data)
            self.assertIn('test', parsed_data)
    
    def test_broadcast_data_format(self):
        """Test broadcast data format"""
        broadcast_data = self.monitor.prepare_broadcast_data()
        
        self.assertIsInstance(broadcast_data, str)
        
        # Should be valid JSON
        try:
            parsed_data = json.loads(broadcast_data)
            self.assertIsInstance(parsed_data, dict)
            self.assertIn('type', parsed_data)
            self.assertEqual(parsed_data['type'], 'system_update')
            self.assertIn('data', parsed_data)
        except (ValueError, TypeError) as e:
            self.fail(f"Broadcast data is not valid JSON: {e}")
    
    def test_client_connection_tracking(self):
        """Test client connection tracking"""
        # Test adding clients
        mock_client1 = Mock()
        mock_client2 = Mock()
        
        self.monitor.add_client(mock_client1)
        self.monitor.add_client(mock_client2)
        
        self.assertIn(mock_client1, self.monitor.connected_clients)
        self.assertIn(mock_client2, self.monitor.connected_clients)
        self.assertEqual(len(self.monitor.connected_clients), 2)
        
        # Test removing clients
        self.monitor.remove_client(mock_client1)
        
        self.assertNotIn(mock_client1, self.monitor.connected_clients)
        self.assertIn(mock_client2, self.monitor.connected_clients)
        self.assertEqual(len(self.monitor.connected_clients), 1)
    
    async def test_broadcast_to_multiple_clients(self):
        """Test broadcasting to multiple clients"""
        # Mock multiple clients
        mock_client1 = AsyncMock()
        mock_client2 = AsyncMock()
        mock_client3 = AsyncMock()
        
        self.monitor.add_client(mock_client1)
        self.monitor.add_client(mock_client2)
        self.monitor.add_client(mock_client3)
        
        # Test broadcast
        test_data = {"test": "broadcast"}
        await self.monitor.broadcast_to_clients(test_data)
        
        # Verify all clients received the data
        mock_client1.send.assert_called_once()
        mock_client2.send.assert_called_once()
        mock_client3.send.assert_called_once()
        
        # Verify sent data
        for client in [mock_client1, mock_client2, mock_client3]:
            sent_data = client.send.call_args[0][0]
            self.assertIsInstance(sent_data, str)
            parsed_data = json.loads(sent_data)
            self.assertEqual(parsed_data, test_data)
    
    async def test_client_disconnection_handling(self):
        """Test handling of client disconnections"""
        mock_client = AsyncMock()
        mock_client.send.side_effect = websockets.exceptions.ConnectionClosed(None, None)
        
        self.monitor.add_client(mock_client)
        
        # Test broadcast with disconnected client
        test_data = {"test": "disconnect"}
        await self.monitor.broadcast_to_clients(test_data)
        
        # Client should be automatically removed
        self.assertNotIn(mock_client, self.monitor.connected_clients)


class TestRealTimeDataTransmission(unittest.TestCase):
    """Test real-time data transmission characteristics"""
    
    def setUp(self):
        """Set up real-time transmission tests"""
        self.monitor = monitor.SystemMonitor()
    
    def test_data_update_frequency(self):
        """Test data update frequency and timing"""
        timestamps = []
        
        # Collect timestamps over multiple updates
        for _ in range(5):
            data = self.monitor.get_system_data()
            timestamps.append(data['timestamp'])
            time.sleep(0.1)
        
        # Calculate intervals
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        # Intervals should be consistent (within reasonable tolerance)
        avg_interval = sum(intervals) / len(intervals)
        for interval in intervals:
            self.assertAlmostEqual(interval, avg_interval, delta=0.05,
                                 msg="Data update intervals should be consistent")
    
    def test_data_freshness(self):
        """Test data freshness and timestamp accuracy"""
        before_time = time.time()
        data = self.monitor.get_system_data()
        after_time = time.time()
        
        data_timestamp = data['timestamp']
        
        # Timestamp should be between before and after time
        self.assertGreaterEqual(data_timestamp, before_time)
        self.assertLessEqual(data_timestamp, after_time)
        
        # Data should be fresh (within 1 second)
        freshness = after_time - data_timestamp
        self.assertLess(freshness, 1.0, "Data should be fresh")
    
    def test_data_consistency_over_time(self):
        """Test data consistency over multiple updates"""
        readings = []
        
        # Collect multiple readings
        for _ in range(3):
            data = self.monitor.get_system_data()
            readings.append(data)
            time.sleep(0.5)
        
        # System info should remain consistent
        for i in range(1, len(readings)):
            # CPU count should not change
            self.assertEqual(readings[i]['cpu']['count'], readings[0]['cpu']['count'])
            
            # Memory total should not change
            self.assertEqual(readings[i]['memory']['total'], readings[0]['memory']['total'])
            
            # Disk devices should remain the same
            self.assertEqual(set(readings[i]['disks'].keys()), set(readings[0]['disks'].keys()))
    
    def test_bandwidth_efficiency(self):
        """Test data transmission bandwidth efficiency"""
        data = self.monitor.get_system_data()
        json_data = json.dumps(data)
        
        # Check data size
        data_size = len(json_data.encode('utf-8'))
        
        # Data should be reasonably sized (less than 10KB for typical systems)
        self.assertLess(data_size, 10240, "Data payload should be bandwidth efficient")
        
        # Ensure all necessary data is included despite size constraints
        self.assertIn('cpu', data)
        self.assertIn('memory', data)
        self.assertIn('disks', data)
        self.assertIn('gpu', data)


class TestMessageProtocol(unittest.TestCase):
    """Test WebSocket message protocol and commands"""
    
    def setUp(self):
        """Set up message protocol tests"""
        self.monitor = monitor.SystemMonitor()
    
    def test_get_data_command(self):
        """Test 'get_data' command handling"""
        message = {"type": "get_data"}
        response = self.monitor.handle_message(message)
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response['type'], 'system_data')
        self.assertIn('data', response)
        
        # Validate data structure
        data = response['data']
        required_keys = ['timestamp', 'cpu', 'memory', 'disks', 'gpu']
        for key in required_keys:
            self.assertIn(key, data)
    
    def test_subscribe_command(self):
        """Test 'subscribe' command for real-time updates"""
        message = {"type": "subscribe", "interval": 1000}  # 1 second
        response = self.monitor.handle_message(message)
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response['type'], 'subscription_confirmed')
        self.assertIn('interval', response)
        self.assertEqual(response['interval'], 1000)
    
    def test_unsubscribe_command(self):
        """Test 'unsubscribe' command"""
        # First subscribe
        subscribe_msg = {"type": "subscribe", "interval": 1000}
        self.monitor.handle_message(subscribe_msg)
        
        # Then unsubscribe
        unsubscribe_msg = {"type": "unsubscribe"}
        response = self.monitor.handle_message(unsubscribe_msg)
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response['type'], 'subscription_cancelled')
    
    def test_config_command(self):
        """Test configuration command handling"""
        config_message = {
            "type": "config",
            "settings": {
                "update_interval": 500,
                "include_gpu": True,
                "disk_filter": ["C:", "D:"]
            }
        }
        
        response = self.monitor.handle_message(config_message)
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response['type'], 'config_updated')
        self.assertIn('settings', response)
    
    def test_invalid_message_handling(self):
        """Test handling of invalid messages"""
        invalid_messages = [
            {},  # Empty message
            {"type": "unknown_command"},  # Unknown command
            {"invalid": "structure"},  # Missing type
            "not_a_dict",  # Not a dictionary
        ]
        
        for invalid_msg in invalid_messages:
            response = self.monitor.handle_message(invalid_msg)
            
            self.assertIsInstance(response, dict)
            self.assertEqual(response['type'], 'error')
            self.assertIn('message', response)
    
    def test_message_validation(self):
        """Test message validation and sanitization"""
        # Test message with extra fields
        message = {
            "type": "get_data",
            "extra_field": "should_be_ignored",
            "timestamp": time.time()
        }
        
        response = self.monitor.handle_message(message)
        
        # Should handle gracefully and return valid response
        self.assertIsInstance(response, dict)
        self.assertEqual(response['type'], 'system_data')


class TestErrorHandlingAndResilience(unittest.TestCase):
    """Test error handling and system resilience"""
    
    def setUp(self):
        """Set up error handling tests"""
        self.monitor = monitor.SystemMonitor()
    
    async def test_websocket_connection_errors(self):
        """Test WebSocket connection error handling"""
        # Mock a connection that fails
        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = websockets.exceptions.ConnectionClosed(None, None)
        
        # Should handle disconnection gracefully
        try:
            await self.monitor.handle_client(mock_websocket, "/")
        except websockets.exceptions.ConnectionClosed:
            pass  # Expected
        
        # Client should be removed from connected clients
        self.assertNotIn(mock_websocket, self.monitor.connected_clients)
    
    def test_data_collection_errors(self):
        """Test handling of data collection errors"""
        with patch.object(self.monitor.hardware_monitor, 'get_cpu_info', 
                         side_effect=Exception("CPU monitoring failed")):
            
            # Should return partial data or handle error gracefully
            try:
                data = self.monitor.get_system_data()
                self.assertIsInstance(data, dict)
                self.assertIn('timestamp', data)
                # May have error indicators or default values
            except Exception as e:
                self.fail(f"Should handle data collection errors gracefully: {e}")
    
    def test_json_serialization_errors(self):
        """Test handling of JSON serialization errors"""
        # Create data with non-serializable objects
        with patch.object(self.monitor, 'get_system_data', 
                         return_value={'invalid': object()}):
            
            try:
                json_data = self.monitor.prepare_broadcast_data()
                # Should either serialize successfully or handle error
                self.assertIsInstance(json_data, str)
            except Exception as e:
                self.fail(f"Should handle JSON serialization errors: {e}")
    
    def test_memory_leak_prevention(self):
        """Test prevention of memory leaks in long-running operations"""
        initial_clients = len(self.monitor.connected_clients)
        
        # Simulate multiple client connections and disconnections
        for i in range(100):
            mock_client = Mock()
            self.monitor.add_client(mock_client)
            self.monitor.remove_client(mock_client)
        
        # Client list should return to original size
        final_clients = len(self.monitor.connected_clients)
        self.assertEqual(final_clients, initial_clients)


def run_websocket_integration_test():
    """Run a full integration test with actual WebSocket server"""
    print("\\n" + "="*60)
    print("WEBSOCKET INTEGRATION TEST")
    print("="*60)
    
    async def integration_test():
        monitor_instance = monitor.SystemMonitor()
        
        # Start server
        server = await websockets.serve(
            monitor_instance.handle_client,
            "localhost",
            8765
        )
        
        print("WebSocket server started on localhost:8765")
        
        try:
            # Connect client
            async with websockets.connect("ws://localhost:8765") as websocket:
                print("Client connected successfully")
                
                # Test get_data command
                await websocket.send(json.dumps({"type": "get_data"}))
                response = await websocket.recv()
                data = json.loads(response)
                
                print(f"Received data type: {data.get('type')}")
                print(f"Data keys: {list(data.get('data', {}).keys())}")
                
                # Test subscribe command
                await websocket.send(json.dumps({"type": "subscribe", "interval": 1000}))
                response = await websocket.recv()
                subscription = json.loads(response)
                
                print(f"Subscription response: {subscription.get('type')}")
                
                print("Integration test completed successfully!")
                
        except Exception as e:
            print(f"Integration test failed: {e}")
        finally:
            server.close()
            await server.wait_closed()
    
    # Run the integration test
    try:
        asyncio.get_event_loop().run_until_complete(integration_test())
    except Exception as e:
        print(f"Integration test error: {e}")


if __name__ == '__main__':
    # Run unit tests
    print("WebSocket Communication Tests")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestWebSocketCommunication))
    test_suite.addTest(unittest.makeSuite(TestRealTimeDataTransmission))
    test_suite.addTest(unittest.makeSuite(TestMessageProtocol))
    test_suite.addTest(unittest.makeSuite(TestErrorHandlingAndResilience))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run integration test
    run_websocket_integration_test()
    
    # Print summary
    print("\\n" + "="*60)
    print("WEBSOCKET TEST SUMMARY")
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
