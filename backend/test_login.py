import requests

url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "username": "city.infra@contractor.com",
    "password": "Contractor123"
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

try:
    response = requests.post(url, data=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
