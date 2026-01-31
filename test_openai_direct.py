"""
直接测试 OpenAI API 调用
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

print("=" * 60)
print("直接测试 OpenAI API")
print("=" * 60)
print(f"Base URL: {SUPER_MIND_BASE_URL}")
print(f"API Key: {SUPER_MIND_API_KEY[:20]}..." if SUPER_MIND_API_KEY else "NOT SET")
print("=" * 60)

if not SUPER_MIND_API_KEY:
    print("ERROR: SUPER_MIND_API_KEY not set!")
    exit(1)

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

# 简单的测试提示
system_prompt = """你是一位专业的跑步教练。请以 JSON 格式返回三个字段：
1. immediate_advice: 即时评估和建议
2. training_plan: 训练计划
3. strategy: 训练策略

全部使用中文。"""

user_message = "请分析我的跑步数据：距离 17.7 公里，平均心率 156 bpm，目标配速 5:00 min/km，目标日期 3 个月后。请提供训练建议。"

print("\n调用 API...")
print(f"Model: gpt-5")
print(f"Max tokens: 2000")
print(f"Response format: json_object")
print("-" * 60)

# 测试1: 不使用 json_object 格式
print("\n测试1: 不使用 json_object 格式...")
try:
    completion1 = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=2000,
        timeout=60.0
    )
    
    print("✓ 测试1 成功!")
    if len(completion1.choices) > 0:
        response1 = completion1.choices[0].message.content
        print(f"响应长度: {len(response1)} 字符")
        print(f"响应预览: {response1[:500]}")
except Exception as e:
    print(f"✗ 测试1 失败: {e}")

# 测试2: 使用 json_object 格式
print("\n测试2: 使用 json_object 格式...")
try:
    completion = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=2000,
        response_format={"type": "json_object"},
        timeout=60.0
    )
    
    print("✓ API 调用成功!")
    print(f"\nCompletion 对象类型: {type(completion)}")
    print(f"Completion 对象属性: {dir(completion)}")
    print(f"Choices count: {len(completion.choices)}")
    
    # 打印完整的 completion 对象
    print(f"\nCompletion 对象:")
    print(f"  - id: {completion.id}")
    print(f"  - object: {completion.object}")
    print(f"  - created: {completion.created}")
    print(f"  - model: {completion.model}")
    print(f"  - usage: {completion.usage}")
    
    if len(completion.choices) > 0:
        choice = completion.choices[0]
        print(f"\nChoice 对象:")
        print(f"  - index: {choice.index}")
        print(f"  - finish_reason: {choice.finish_reason}")
        print(f"  - message role: {choice.message.role}")
        print(f"  - message content type: {type(choice.message.content)}")
        print(f"  - message content: '{choice.message.content}'")
        print(f"  - message content length: {len(choice.message.content) if choice.message.content else 0}")
        print(f"  - message 所有属性: {dir(choice.message)}")
        
        # 尝试获取完整响应
        try:
            print(f"\n尝试获取完整响应...")
            # 检查是否有其他字段
            if hasattr(choice.message, 'tool_calls'):
                print(f"  - tool_calls: {choice.message.tool_calls}")
            if hasattr(choice.message, 'function_call'):
                print(f"  - function_call: {choice.message.function_call}")
            
            # 尝试序列化整个消息
            import json
            msg_dict = choice.message.model_dump()
            print(f"\n消息对象完整内容:")
            print(json.dumps(msg_dict, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"  获取完整响应时出错: {e}")
        
        response_text = choice.message.content
        print(f"\n响应长度: {len(response_text) if response_text else 0} 字符")
        print(f"\n原始响应:")
        print("-" * 60)
        if response_text:
            print(response_text[:1000])
        else:
            print("(空响应)")
        print("-" * 60)
        
        # 尝试解析 JSON
        try:
            response_dict = json.loads(response_text)
            print("\n✓ JSON 解析成功!")
            print(f"\n解析后的字段:")
            for key in ['immediate_advice', 'training_plan', 'strategy']:
                value = response_dict.get(key, '')
                print(f"  - {key}: {len(value)} 字符")
                if value:
                    print(f"    预览: {value[:100]}...")
        except json.JSONDecodeError as e:
            print(f"\n✗ JSON 解析失败: {e}")
            print(f"响应文本: {response_text[:500]}")
    else:
        print("✗ 没有返回 choices")
        print(f"Completion object: {completion}")
        
except Exception as e:
    print(f"\n✗ API 调用失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
