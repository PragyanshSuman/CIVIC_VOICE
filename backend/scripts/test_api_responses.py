import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api():
    print(f"--- API Test ({time.ctime()}) ---")
    
    # login
    login_data = {
        "username": "admin@civic.com",
        "password": "Admin123"
    }
    
    try:
        print(f"Logging in as admin at {BASE_URL}/auth/login ...")
        resp = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=5)
        print(f"Login Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
            
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Login successful. Token obtained.")
        
        # Test Stats
        print(f"Fetching stats...")
        resp = requests.get(f"{BASE_URL}/problems/stats", headers=headers, timeout=5)
        print(f"Stats Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Stats: {json.dumps(resp.json(), indent=2)}")
        else:
            print(f"Stats Error: {resp.text}")
            
        # Test Work Orders
        print(f"Fetching work orders...")
        resp = requests.get(f"{BASE_URL}/work-orders/", headers=headers, timeout=5)
        print(f"Work Orders Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Work Orders: {len(resp.json())} found")
        else:
            print(f"Work Orders Error: {resp.text}")
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
    except Exception as e:
        print(f"Request failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_api()
