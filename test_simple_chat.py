"""
简单测试 - 不使用 json_object
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

print("=" * 60)
print("简单聊天测试（不使用 json_object）")
print("=" * 60)

# 简单的提示，要求返回 JSON
system_prompt = """你是一位专业的跑步教练。请以 JSON 格式返回，包含三个字段：
- immediate_advice: 即时评估和建议
- training_plan: 训练计划  
- strategy: 训练策略

请确保返回有效的 JSON 格式。"""

user_message = "请分析：距离 17.7 公里，平均心率 156 bpm，目标配速 5:00 min/km。提供训练建议。"

print("\n调用 API（不使用 json_object 格式）...")
try:
    completion = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=1500,  # 减少 token 数量
        timeout=60.0
    )
    
    print(f"✓ API 调用成功!")
    print(f"Usage: {completion.usage}")
    
    if len(completion.choices) > 0:
        response_text = completion.choices[0].message.content
        print(f"\n响应长度: {len(response_text)} 字符")
        print(f"Finish reason: {completion.choices[0].finish_reason}")
        
        if response_text:
            print(f"\n完整响应:")
            print("-" * 60)
            print(response_text)
            print("-" * 60)
            
            # 尝试提取 JSON
            try:
                # 尝试找到 JSON 部分
                if '{' in response_text and '}' in response_text:
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_str = response_text[start:end]
                    response_dict = json.loads(json_str)
                    print("\n✓ 成功提取并解析 JSON!")
                    for key in ['immediate_advice', 'training_plan', 'strategy']:
                        value = response_dict.get(key, '')
                        print(f"\n{key}:")
                        print(f"  长度: {len(value)} 字符")
                        if value:
                            print(f"  预览: {value[:200]}...")
            except json.JSONDecodeError as e:
                print(f"\n✗ JSON 解析失败: {e}")
                print("尝试手动提取 JSON...")
        else:
            print("\n✗ 响应为空!")
            
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
