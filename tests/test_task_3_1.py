"""
Test for Task 3.1: API Endpoints Implementation

This test verifies that the new resource monitoring API endpoints are working correctly
and provide the expected functionality for hardware monitoring configuration.
"""

import sys
import asyncio
import json
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import aiohttp

class APIEndpointTester:
    """Test class for Task 3.1 API endpoints"""
    
    def __init__(self, base_url="http://localhost:8888"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_gpu_info_endpoint(self):
        """Test GET /resources/monitor/GPU endpoint"""
        print("\n🎮 Testing GPU Information Endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/resources/monitor/GPU") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        print(f"✅ GPU Info Retrieved Successfully")
                        print(f"   GPU Count: {data.get('gpu_count', 0)}")
                        print(f"   Device Type: {data.get('device_type', 'unknown')}")
                        print(f"   CUDA Available: {data.get('capabilities', {}).get('cuda_available', False)}")
                        
                        gpus = data.get('gpus', [])
                        for i, gpu in enumerate(gpus):
                            print(f"   GPU {i}: {gpu.get('name', 'Unknown')} - {gpu.get('gpu_utilization', 'N/A')}% util")
                        
                        return True
                    else:
                        print(f"❌ GPU Info Failed: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ GPU Info Failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ GPU Info Test Failed: {e}")
            return False
    
    async def test_hdd_info_endpoint(self):
        """Test GET /resources/monitor/HDD endpoint"""
        print("\n💾 Testing HDD Information Endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/resources/monitor/HDD") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        print(f"✅ HDD Info Retrieved Successfully")
                        available_drives = data.get('available_drives', [])
                        print(f"   Available Drives: {len(available_drives)} ({', '.join(available_drives)})")
                        
                        drives = data.get('drives', [])
                        for drive in drives[:3]:  # Show first 3 drives
                            name = drive.get('path', 'Unknown')
                            used_percent = drive.get('used_percent', 0)
                            total_gb = drive.get('total_bytes', 0) // (1024**3)
                            print(f"   {name}: {used_percent:.1f}% used ({total_gb}GB total)")
                        
                        total_summary = data.get('total_summary', {})
                        if total_summary:
                            total_used = total_summary.get('used_percent', 0)
                            print(f"   Total Usage: {total_used:.1f}%")
                        
                        return True
                    else:
                        print(f"❌ HDD Info Failed: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ HDD Info Failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ HDD Info Test Failed: {e}")
            return False
    
    async def test_monitor_settings_update(self):
        """Test PATCH /resources/monitor endpoint"""
        print("\n⚙️ Testing Monitor Settings Update...")
        
        try:
            # Test updating monitoring settings
            settings_update = {
                "enable_cpu": True,
                "enable_ram": True,
                "enable_disk": True,
                "enable_gpu": True,
                "update_interval": 3.0,
                "save": False  # Don't save to avoid changing config file
            }
            
            async with self.session.patch(
                f"{self.base_url}/resources/monitor",
                json=settings_update,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        print(f"✅ Monitor Settings Updated Successfully")
                        updated = data.get('updated_settings', {})
                        print(f"   Updated: {list(updated.keys())}")
                        print(f"   New Update Interval: {updated.get('update_interval', 'unchanged')}")
                        return True
                    else:
                        print(f"❌ Settings Update Failed: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Settings Update Failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Monitor Settings Test Failed: {e}")
            return False
    
    async def test_gpu_settings_update(self):
        """Test PATCH /resources/monitor/GPU/{index} endpoint"""
        print("\n🔧 Testing GPU Settings Update...")
        
        try:
            # Test updating GPU 0 settings
            gpu_settings = {
                "enable_monitoring": True,
                "enable_vram": True,
                "enable_temperature": True,
                "save": False
            }
            
            async with self.session.patch(
                f"{self.base_url}/resources/monitor/GPU/0",
                json=gpu_settings,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success'):
                        print(f"✅ GPU Settings Updated Successfully")
                        print(f"   GPU Index: {data.get('gpu_index', 'unknown')}")
                        updated = data.get('updated_settings', {})
                        print(f"   Updated: {list(updated.keys())}")
                        if data.get('note'):
                            print(f"   Note: {data.get('note')}")
                        return True
                    else:
                        print(f"❌ GPU Settings Update Failed: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ GPU Settings Update Failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ GPU Settings Test Failed: {e}")
            return False
    
    async def test_invalid_requests(self):
        """Test error handling for invalid requests"""
        print("\n🚨 Testing Error Handling...")
        
        tests_passed = 0
        total_tests = 3
        
        # Test invalid GPU index
        try:
            async with self.session.patch(
                f"{self.base_url}/resources/monitor/GPU/999",
                json={"enable_monitoring": True}
            ) as response:
                if response.status == 404:
                    print(f"✅ Invalid GPU index correctly rejected (404)")
                    tests_passed += 1
                else:
                    print(f"❌ Invalid GPU index test failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Invalid GPU index test error: {e}")
        
        # Test invalid JSON
        try:
            async with self.session.patch(
                f"{self.base_url}/resources/monitor",
                data="invalid json",
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 400:
                    print(f"✅ Invalid JSON correctly rejected (400)")
                    tests_passed += 1
                else:
                    print(f"❌ Invalid JSON test failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Invalid JSON test error: {e}")
        
        # Test invalid GPU index format
        try:
            async with self.session.patch(
                f"{self.base_url}/resources/monitor/GPU/abc",
                json={"enable_monitoring": True}
            ) as response:
                if response.status == 400:
                    print(f"✅ Invalid GPU index format correctly rejected (400)")
                    tests_passed += 1
                else:
                    print(f"❌ Invalid GPU index format test failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Invalid GPU index format test error: {e}")
        
        return tests_passed == total_tests

async def wait_for_server(base_url="http://localhost:8888", timeout=30):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/api/status") as response:
                    if response.status == 200:
                        print("✅ Server is ready")
                        return True
        except:
            pass
        
        await asyncio.sleep(1)
    
    print("❌ Server not ready within timeout")
    return False

async def main():
    """Run all Task 3.1 API endpoint tests"""
    print("=" * 60)
    print("🧪 TASK 3.1 TESTING: API Endpoints Implementation")
    print("=" * 60)
    
    # Wait for server to be ready
    if not await wait_for_server():
        print("❌ Cannot test - server not available")
        print("   Please start the server with: python main.py")
        return False
    
    # Run tests
    async with APIEndpointTester() as tester:
        tests = [
            tester.test_gpu_info_endpoint,
            tester.test_hdd_info_endpoint,
            tester.test_monitor_settings_update,
            tester.test_gpu_settings_update,
            tester.test_invalid_requests
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if await test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TASK 3.1 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Task 3.1 API endpoints completed successfully!")
        print("✅ All resource monitoring endpoints are functional")
        print("✅ Error handling working correctly")
        print("✅ JSON request/response handling operational")
        return True
    else:
        print("⚠️ Some tests failed - check server logs")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
