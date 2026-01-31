"""
测试 Chat API 端点
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat(user_message: str):
    """测试 Chat API"""
    url = f"{BASE_URL}/chat"
    
    request_body = {
        "user_message": user_message
    }
    
    print(f"\n{'='*60}")
    print(f"测试 Chat API")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"请求体: {json.dumps(request_body, indent=2, ensure_ascii=False)}")
    print(f"{'-'*60}")
    
    try:
        response = requests.post(url, json=request_body, timeout=60)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            json_data = response.json()
            print(f"响应: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            print(f"\nAI 回复: {json_data.get('response', 'N/A')}")
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 错误: 无法连接到服务器 {BASE_URL}")
        print("请确保 FastAPI 服务器正在运行！")
        print("运行命令: py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    print("Chat API 测试程序")
    print("=" * 60)
    
    # 测试消息
    test_messages = [
        "Hello, what is Python?",
        "Tell me a short joke.",
    ]
    
    for msg in test_messages:
        test_chat(msg)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
