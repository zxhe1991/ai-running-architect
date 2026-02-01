"""
检查部署状态
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://space.ai-builders.com/backend"
API_KEY = os.getenv("SUPER_MIND_API_KEY") or os.getenv("AI_BUILDER_TOKEN")
SERVICE_NAME = "ai-running-architect"

def check_status():
    url = f"{BASE_URL}/v1/deployments/{SERVICE_NAME}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n[部署状态] {SERVICE_NAME}")
            print(f"  状态: {data.get('status', 'unknown')}")
            print(f"  公共URL: {data.get('public_url', 'Not available yet')}")
            print(f"  最后部署时间: {data.get('last_deployed_at', 'Never')}")
            
            # 尝试访问公共URL
            public_url = data.get('public_url')
            if public_url:
                print(f"\n[测试访问] {public_url}")
                try:
                    test_response = requests.get(public_url, timeout=5)
                    if test_response.status_code == 200:
                        print(f"  [OK] 应用可以访问！状态码: {test_response.status_code}")
                    else:
                        print(f"  [WARNING] 应用返回状态码: {test_response.status_code}")
                except Exception as e:
                    print(f"  [INFO] 应用可能还在部署中: {e}")
            
            return data
        else:
            print(f"[ERROR] 检查状态失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 连接错误: {e}")
        return None

if __name__ == "__main__":
    check_status()
