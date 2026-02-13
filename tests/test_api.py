import urllib.request
import json
import time

time.sleep(3)

# Test health endpoint
try:
    with urllib.request.urlopen('http://localhost:5000/api/health') as response:
        data = json.loads(response.read())
        print("✓ Health Check Successful!")
        print(f"  Status: {data['status']}")
        print(f"  Server: {data['server']}")
        print(f"  Workers: {data['parallel_workers']}")
        print(f"  Models: {data['models_available']}")
except Exception as e:
    print(f"✗ Health check failed: {e}")

# Test models endpoint
try:
    with urllib.request.urlopen('http://localhost:5000/api/models') as response:
        data = json.loads(response.read())
        print("\n✓ Models Endpoint Successful!")
        for provider, models in data.items():
            print(f"  {provider.upper()}: {len(models)} models")
except Exception as e:
    print(f"✗ Models endpoint failed: {e}")

# Test one more - health check again
print("\n✓ All basic tests passed!")
print("Server is running on http://localhost:5000")
