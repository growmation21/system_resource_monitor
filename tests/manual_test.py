"""
Manual API Test for Task 3.1

Simple direct test of the API endpoints without external dependencies
"""

import json
import urllib.request
import urllib.parse

def test_endpoint(url, method="GET", data=None):
    """Test an API endpoint"""
    print(f"\n🔍 Testing {method} {url}")
    
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Status: {response.status}")
            print(f"📄 Response: {json.dumps(result, indent=2)[:500]}...")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Manual API Test for Task 3.1")
    print("=" * 50)
    
    base_url = "http://localhost:8888"
    
    # Test GPU endpoint
    if test_endpoint(f"{base_url}/resources/monitor/GPU"):
        print("✅ GPU endpoint working")
    
    # Test HDD endpoint  
    if test_endpoint(f"{base_url}/resources/monitor/HDD"):
        print("✅ HDD endpoint working")
    
    # Test monitor settings update
    settings = {"enable_cpu": True, "update_interval": 3.0, "save": False}
    if test_endpoint(f"{base_url}/resources/monitor", "PATCH", settings):
        print("✅ Monitor settings update working")
    
    print("\n🎉 Manual tests completed!")

if __name__ == "__main__":
    main()
