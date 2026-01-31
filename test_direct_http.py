"""
直接使用 HTTP 请求测试 API（绕过 OpenAI SDK）
"""
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

print("=" * 60)
print("直接 HTTP 请求测试")
print("=" * 60)

url = f"{SUPER_MIND_BASE_URL}/chat/completions"

headers = {
    "Authorization": f"Bearer {SUPER_MIND_API_KEY}",
    "Content-Type": "application/json"
}

system_prompt = """你是一位专业的跑步教练。请以 JSON 格式返回，包含三个字段：
- immediate_advice: 即时评估和建议
- training_plan: 训练计划  
- strategy: 训练策略

请确保返回有效的 JSON 格式。"""

user_message = "请分析：距离 17.7 公里，平均心率 156 bpm，目标配速 5:00 min/km。提供训练建议。"

# 测试多个模型
models_to_test = [
    "gpt-5",
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku"
]

for model in models_to_test:
    print(f"\n{'='*60}")
    print(f"测试模型: {model}")
    print(f"{'='*60}")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"响应键: {list(data.keys())}")
                
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
                    
                    print(f"Content 类型: {type(content)}")
                    print(f"Content 长度: {len(content) if content else 0}")
                    print(f"Finish reason: {choice.get('finish_reason')}")
                    
                    if "usage" in data:
                        usage = data["usage"]
                        print(f"Token 使用: {usage.get('completion_tokens', 0)}")
                    
                    if content:
                        print(f"\n响应内容:")
                        print("-" * 60)
                        print(content[:500])
                        print("-" * 60)
                        
                        # 尝试解析 JSON
                        try:
                            if '{' in content:
                                start = content.find('{')
                                end = content.rfind('}') + 1
                                json_str = content[start:end]
                                parsed = json.loads(json_str)
                                print(f"\n✓ JSON 解析成功!")
                                print(f"  字段: {list(parsed.keys())}")
                        except Exception as e:
                            print(f"\n✗ JSON 解析失败: {e}")
                    else:
                        print(f"\n⚠ Content 为空!")
                        print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                else:
                    print(f"\n✗ 响应中没有 choices")
                    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            else:
                print(f"\n✗ HTTP 错误: {response.status_code}")
                print(f"响应: {response.text[:500]}")
                
    except httpx.TimeoutException:
        print(f"\n✗ 请求超时")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print("测试完成")
print(f"{'='*60}")
