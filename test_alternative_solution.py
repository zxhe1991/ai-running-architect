"""
替代解决方案：使用不同的方法获取响应
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import httpx

load_dotenv()

SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

print("=" * 60)
print("替代解决方案测试")
print("=" * 60)

system_prompt = """你是一位专业的跑步教练。请以 JSON 格式返回，包含三个字段：
- immediate_advice: 即时评估和建议
- training_plan: 训练计划  
- strategy: 训练策略

请确保返回有效的 JSON 格式。"""

user_message = "请分析：距离 17.7 公里，平均心率 156 bpm，目标配速 5:00 min/km。提供训练建议。"

# 解决方案1: 使用更短的提示和更少的 tokens
print("\n解决方案1: 减少 max_tokens")
try:
    openai_client = OpenAI(
        api_key=SUPER_MIND_API_KEY,
        base_url=SUPER_MIND_BASE_URL
    )
    
    completion = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=500,  # 大幅减少
        timeout=30.0
    )
    
    response = completion.choices[0].message.content
    print(f"  响应长度: {len(response) if response else 0}")
    if response:
        print(f"  ✓ 成功! 响应: {response[:200]}")
    else:
        print(f"  ✗ 仍然为空")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 解决方案2: 不使用 system prompt
print("\n解决方案2: 不使用 system prompt")
try:
    completion = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": f"{system_prompt}\n\n{user_message}"}
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=30.0
    )
    
    response = completion.choices[0].message.content
    print(f"  响应长度: {len(response) if response else 0}")
    if response:
        print(f"  ✓ 成功! 响应: {response[:200]}")
    else:
        print(f"  ✗ 仍然为空")
except Exception as e:
    print(f"  ✗ 失败: {e}")

# 解决方案3: 使用原始 HTTP 请求并检查完整响应
print("\n解决方案3: 原始 HTTP 请求（检查完整响应）")
try:
    url = f"{SUPER_MIND_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {SUPER_MIND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应键: {list(data.keys())}")
            
            # 检查所有可能的字段
            if "choices" in data:
                choice = data["choices"][0]
                print(f"  Choice 键: {list(choice.keys())}")
                print(f"  Message 键: {list(choice.get('message', {}).keys())}")
                
                # 尝试所有可能的字段
                message = choice.get("message", {})
                for key in message.keys():
                    value = message[key]
                    if value:
                        print(f"  ✓ 找到非空字段 '{key}': {str(value)[:100]}")
            
            # 打印完整响应（用于调试）
            print(f"\n  完整响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        else:
            print(f"  ✗ HTTP 错误: {response.status_code}")
            print(f"  响应: {response.text[:500]}")
            
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# 解决方案4: 尝试不同的 base URL
print("\n解决方案4: 尝试不同的 base URL")
alternative_urls = [
    "https://space.ai-builders.com/backend/v1",
    "https://space.ai-builders.com/api/v1",
    "https://api.space.ai-builders.com/v1",
]

for alt_url in alternative_urls:
    print(f"\n  测试: {alt_url}")
    try:
        test_client = OpenAI(
            api_key=SUPER_MIND_API_KEY,
            base_url=alt_url
        )
        
        completion = test_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "user", "content": "Hello, respond with 'test'"}
            ],
            max_tokens=10,
            timeout=10.0
        )
        
        response = completion.choices[0].message.content
        if response:
            print(f"    ✓ 成功! URL 可用，响应: {response}")
            break
        else:
            print(f"    ✗ 响应为空")
    except Exception as e:
        print(f"    ✗ 失败: {str(e)[:100]}")

print(f"\n{'='*60}")
print("测试完成")
print(f"{'='*60}")
