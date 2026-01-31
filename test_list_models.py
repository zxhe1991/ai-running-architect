"""
列出可用的模型
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

print("=" * 60)
print("列出可用模型")
print("=" * 60)

# 尝试不同的端点来列出模型
endpoints_to_try = [
    f"{SUPER_MIND_BASE_URL}/models",
    f"{SUPER_MIND_BASE_URL}/v1/models",
    f"https://space.ai-builders.com/backend/models",
]

headers = {
    "Authorization": f"Bearer {SUPER_MIND_API_KEY}",
    "Content-Type": "application/json"
}

for endpoint in endpoints_to_try:
    print(f"\n尝试端点: {endpoint}")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(endpoint, headers=headers)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                if "data" in data:
                    models = data["data"]
                    print(f"\n  可用模型:")
                    for model in models:
                        print(f"    - {model.get('id', model)}")
            else:
                print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"  错误: {e}")

print(f"\n{'='*60}")
