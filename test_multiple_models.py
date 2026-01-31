"""
测试多个模型和不同的 API 配置
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
print("测试多个模型和配置")
print("=" * 60)

# 测试配置列表
test_configs = [
    {
        "name": "gpt-5 (标准配置)",
        "model": "gpt-5",
        "use_json_object": False,
        "max_tokens": 1500
    },
    {
        "name": "gpt-5 (json_object 格式)",
        "model": "gpt-5",
        "use_json_object": True,
        "max_tokens": 1500
    },
    {
        "name": "gpt-4 (如果可用)",
        "model": "gpt-4",
        "use_json_object": False,
        "max_tokens": 1500
    },
    {
        "name": "gpt-3.5-turbo (如果可用)",
        "model": "gpt-3.5-turbo",
        "use_json_object": False,
        "max_tokens": 1500
    },
    {
        "name": "claude-3-opus (如果可用)",
        "model": "claude-3-opus",
        "use_json_object": False,
        "max_tokens": 1500
    },
    {
        "name": "claude-3-sonnet (如果可用)",
        "model": "claude-3-sonnet",
        "use_json_object": False,
        "max_tokens": 1500
    },
]

system_prompt = """你是一位专业的跑步教练。请以 JSON 格式返回，包含三个字段：
- immediate_advice: 即时评估和建议
- training_plan: 训练计划  
- strategy: 训练策略

请确保返回有效的 JSON 格式。"""

user_message = "请分析：距离 17.7 公里，平均心率 156 bpm，目标配速 5:00 min/km。提供训练建议。"

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)

results = []

for config in test_configs:
    print(f"\n{'='*60}")
    print(f"测试: {config['name']}")
    print(f"{'='*60}")
    
    try:
        params = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": config["max_tokens"],
            "timeout": 30.0
        }
        
        if config["use_json_object"]:
            params["response_format"] = {"type": "json_object"}
        
        completion = openai_client.chat.completions.create(**params)
        
        response_text = completion.choices[0].message.content if completion.choices[0].message.content else ""
        usage = completion.usage
        
        result = {
            "config": config["name"],
            "success": True,
            "response_length": len(response_text),
            "has_content": len(response_text) > 0,
            "tokens_used": usage.completion_tokens if usage else 0,
            "finish_reason": completion.choices[0].finish_reason,
            "preview": response_text[:200] if response_text else "(空响应)"
        }
        
        print(f"✓ API 调用成功")
        print(f"  响应长度: {len(response_text)} 字符")
        print(f"  Token 使用: {usage.completion_tokens if usage else 'N/A'}")
        print(f"  完成原因: {completion.choices[0].finish_reason}")
        
        if response_text:
            print(f"  响应预览: {response_text[:200]}...")
            # 尝试解析 JSON
            try:
                if '{' in response_text:
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_str = response_text[start:end]
                    json.loads(json_str)
                    result["json_valid"] = True
                    print(f"  ✓ JSON 有效")
                else:
                    result["json_valid"] = False
                    print(f"  ✗ 未找到 JSON")
            except:
                result["json_valid"] = False
                print(f"  ✗ JSON 无效")
        else:
            print(f"  ⚠ 响应为空!")
            result["json_valid"] = False
        
        results.append(result)
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        results.append({
            "config": config["name"],
            "success": False,
            "error": str(e)
        })

# 总结
print(f"\n{'='*60}")
print("测试总结")
print(f"{'='*60}")

for result in results:
    if result.get("success"):
        status = "✓" if result.get("has_content") else "✗"
        print(f"{status} {result['config']}: {result['response_length']} 字符, {result['tokens_used']} tokens")
    else:
        print(f"✗ {result['config']}: {result.get('error', 'Unknown error')}")

# 找出最佳配置
best_config = None
for result in results:
    if result.get("success") and result.get("has_content") and result.get("json_valid"):
        best_config = result
        break

if best_config:
    print(f"\n✓ 找到可用配置: {best_config['config']}")
else:
    print(f"\n✗ 没有找到完全可用的配置")
    print("建议:")
    print("1. 检查 API 端点是否正确")
    print("2. 尝试直接使用 HTTP 请求")
    print("3. 联系 API 提供商")

print(f"\n{'='*60}")
