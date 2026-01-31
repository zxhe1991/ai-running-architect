"""
测试流式响应
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

print("=" * 60)
print("测试流式响应")
print("=" * 60)

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

system_prompt = """你是一位专业的跑步教练。请以 JSON 格式返回，包含三个字段：
- immediate_advice: 即时评估和建议
- training_plan: 训练计划  
- strategy: 训练策略

请确保返回有效的 JSON 格式。"""

user_message = "请分析：距离 17.7 公里，平均心率 156 bpm，目标配速 5:00 min/km。提供训练建议。"

print("\n测试流式响应...")
try:
    stream = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=1000,
        stream=True
    )
    
    print("✓ 流式响应开始")
    
    full_response = ""
    chunk_count = 0
    
    for chunk in stream:
        chunk_count += 1
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                content = delta.content
                full_response += content
                print(content, end='', flush=True)
    
    print(f"\n\n✓ 流式响应完成")
    print(f"  总块数: {chunk_count}")
    print(f"  响应长度: {len(full_response)} 字符")
    
    if full_response:
        print(f"\n完整响应:")
        print("-" * 60)
        print(full_response)
        print("-" * 60)
        
        # 尝试解析 JSON
        try:
            if '{' in full_response:
                start = full_response.find('{')
                end = full_response.rfind('}') + 1
                json_str = full_response[start:end]
                parsed = json.loads(json_str)
                print(f"\n✓ JSON 解析成功!")
                for key in ['immediate_advice', 'training_plan', 'strategy']:
                    value = parsed.get(key, '')
                    print(f"  {key}: {len(value)} 字符")
        except Exception as e:
            print(f"\n✗ JSON 解析失败: {e}")
    else:
        print(f"\n⚠ 响应为空!")
        
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}")
