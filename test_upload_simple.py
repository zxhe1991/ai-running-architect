"""
简单测试上传功能
"""
import requests
import os

BASE_URL = "http://127.0.0.1:8000"
csv_file = "Running_Today.csv"

if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found")
    exit(1)

print(f"Testing upload of {csv_file}...")

try:
    with open(csv_file, 'rb') as f:
        files = {'file': (os.path.basename(csv_file), f, 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/upload_running_csv",
            files=files,
            timeout=30
        )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nSuccess!")
        print(f"Message: {result.get('message')}")
        if 'analysis' in result:
            print("Analysis completed successfully")
    else:
        print(f"\nError Response:")
        print(response.text)
        try:
            error_json = response.json()
            print(f"Error JSON: {error_json}")
        except:
            pass
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
