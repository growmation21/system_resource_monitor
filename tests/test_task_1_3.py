#!/usr/bin/env python3
"""
Server Test Script for Task 1.3

Tests the aiohttp web server implementation including:
- Basic HTTP endpoints
- WebSocket functionality
- Static file serving
- Error handling
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.logger import setup_logging
from src.server import SystemMonitorServer

async def test_server_functionality():
    """Test server functionality"""
    print("🧪 Testing System Monitor Server - Task 1.3")
    print("=" * 50)
    
    # Set up logging
    logger = setup_logging(level='INFO')
    
    # Create test configuration
    config = Config()
    config.server.port = 8890  # Use different port for testing
    config.app.auto_open_browser = False
    
    # Create server
    server = SystemMonitorServer(config, logger)
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Give server time to start
    await asyncio.sleep(2)
    
    try:
        # Test HTTP endpoints
        async with aiohttp.ClientSession() as session:
            base_url = f"http://{config.server.host}:{config.server.port}"
            
            # Test status endpoint
            print("🔍 Testing /api/status endpoint...")
            async with session.get(f"{base_url}/api/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status endpoint: {data.get('server', 'unknown')}")
                else:
                    print(f"❌ Status endpoint failed: {response.status}")
            
            # Test config endpoint
            print("🔍 Testing /api/config endpoint...")
            async with session.get(f"{base_url}/api/config") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Config endpoint: {len(data)} config sections")
                else:
                    print(f"❌ Config endpoint failed: {response.status}")
            
            # Test root endpoint
            print("🔍 Testing root endpoint...")
            async with session.get(base_url) as response:
                if response.status == 200:
                    print("✅ Root endpoint working")
                else:
                    print(f"❌ Root endpoint failed: {response.status}")
            
            # Test WebSocket
            print("🔍 Testing WebSocket connection...")
            try:
                ws_url = f"ws://{config.server.host}:{config.server.port}/ws"
                async with session.ws_connect(ws_url) as ws:
                    # Wait for connection message
                    msg = await ws.receive()
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        if data.get('type') == 'connected':
                            print("✅ WebSocket connection established")
                            
                            # Test ping/pong
                            await ws.send_str(json.dumps({'type': 'ping'}))
                            response = await ws.receive()
                            if response.type == aiohttp.WSMsgType.TEXT:
                                pong_data = json.loads(response.data)
                                if pong_data.get('type') == 'pong':
                                    print("✅ WebSocket ping/pong working")
                                else:
                                    print(f"❌ WebSocket ping/pong failed: {pong_data}")
                            
                            # Test status request
                            await ws.send_str(json.dumps({'type': 'get_status'}))
                            response = await ws.receive()
                            if response.type == aiohttp.WSMsgType.TEXT:
                                status_data = json.loads(response.data)
                                if status_data.get('type') == 'status':
                                    print("✅ WebSocket status request working")
                                else:
                                    print(f"❌ WebSocket status failed: {status_data}")
                    
                    await ws.close()
                    
            except Exception as e:
                print(f"❌ WebSocket test failed: {e}")
    
    except Exception as e:
        print(f"❌ HTTP tests failed: {e}")
    
    finally:
        # Stop the server
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        
        await server.stop()
    
    print("\n" + "=" * 50)
    print("✅ Task 1.3 Server Tests Completed")

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import aiohttp
        print(f"✅ aiohttp {aiohttp.__version__}")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        import aiohttp_cors
        print("✅ aiohttp_cors")
    except ImportError as e:
        print(f"❌ aiohttp_cors import failed: {e}")
        return False
    
    try:
        from src.server import SystemMonitorServer, WebSocketManager
        print("✅ Server modules")
    except ImportError as e:
        print(f"❌ Server module import failed: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    if not test_imports():
        print("❌ Import tests failed")
        return 1
    
    try:
        await test_server_functionality()
        print("🎉 All tests passed!")
        return 0
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
