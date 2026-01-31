"""
测试 Agentic Loop 功能
验证 /chat 端点是否能正确处理工具调用和循环
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_agentic_chat(user_message: str):
    """测试带工具调用的聊天"""
    url = f"{BASE_URL}/chat"
    
    request_body = {
        "user_message": user_message
    }
    
    print(f"\n{'='*60}")
    print(f"测试 Agentic Chat")
    print(f"{'='*60}")
    print(f"用户消息: {user_message}")
    print(f"{'-'*60}")
    
    try:
        response = requests.post(url, json=request_body, timeout=120)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            json_data = response.json()
            print(f"\n响应:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            print(f"\nAI 回复:")
            print(json_data.get('response', 'N/A'))
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 无法连接到服务器 {BASE_URL}")
        print("请确保 FastAPI 服务器正在运行！")
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Agentic Loop 测试程序")
    print("="*60)
    
    # 测试需要搜索的问题
    test_messages = [
        "Who won the Super Bowl in 2024?",
        "What is the latest news about Python programming?",
        "Tell me about FastAPI framework",
    ]
    
    for msg in test_messages:
        test_agentic_chat(msg)
        print("\n" + "="*60 + "\n")
    
    print("测试完成！")
