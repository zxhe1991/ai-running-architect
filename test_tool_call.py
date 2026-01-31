"""
测试 LLM 工具调用格式
验证当问 "Who won the Super Bowl?" 时，LLM 能否输出有效的工具调用
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_tool_schema():
    """获取工具 schema"""
    print("\n" + "="*60)
    print("1. 获取工具 Schema")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] 工具 Schema 获取成功:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"✗ 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def test_tool_call_example():
    """测试工具调用示例"""
    print("\n" + "="*60)
    print("2. 测试工具调用格式示例")
    print("="*60)
    
    try:
        response = requests.post(f"{BASE_URL}/test_tool_call", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("[OK] 工具调用示例获取成功:")
            print("\n问题: 'Who won the Super Bowl?'")
            print("\n期望的 LLM 工具调用格式:")
            print(json.dumps(data["expected_tool_call"], indent=2, ensure_ascii=False))
            print("\n工具 Schema:")
            print(json.dumps(data["tool_schema"], indent=2, ensure_ascii=False))
            return data
        else:
            print(f"✗ 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        return None


def verify_tool_call_format(tool_call_example):
    """验证工具调用格式是否符合 OpenAI 标准"""
    print("\n" + "="*60)
    print("3. 验证工具调用格式")
    print("="*60)
    
    expected = tool_call_example["expected_tool_call"]
    
    checks = [
        ("包含 'role' 字段", "role" in expected),
        ("role 值为 'assistant'", expected.get("role") == "assistant"),
        ("包含 'tool_calls' 字段", "tool_calls" in expected),
        ("tool_calls 是列表", isinstance(expected.get("tool_calls"), list)),
        ("tool_calls 不为空", len(expected.get("tool_calls", [])) > 0),
    ]
    
    if expected.get("tool_calls"):
        tool_call = expected["tool_calls"][0]
        checks.extend([
            ("tool_call 包含 'id'", "id" in tool_call),
            ("tool_call 包含 'type'", "type" in tool_call),
            ("tool_call type 为 'function'", tool_call.get("type") == "function"),
            ("tool_call 包含 'function'", "function" in tool_call),
            ("function 包含 'name'", "name" in tool_call.get("function", {})),
            ("function name 为 'web_search'", tool_call.get("function", {}).get("name") == "web_search"),
            ("function 包含 'arguments'", "arguments" in tool_call.get("function", {})),
        ])
        
        # 验证 arguments 是有效的 JSON
        try:
            args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
            checks.append(("arguments 是有效的 JSON", True))
            checks.append(("arguments 包含 'query'", "query" in args))
        except:
            checks.append(("arguments 是有效的 JSON", False))
    
    all_passed = True
    for check_name, passed in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n[OK] 所有格式验证通过！工具调用格式符合 OpenAI 标准。")
    else:
        print("\n[FAIL] 部分验证失败，请检查工具调用格式。")
    
    return all_passed


if __name__ == "__main__":
    print("="*60)
    print("LLM 工具调用格式验证测试")
    print("="*60)
    
    # 1. 获取工具 schema
    tool_schema = test_tool_schema()
    
    # 2. 获取工具调用示例
    tool_call_example = test_tool_call_example()
    
    # 3. 验证格式
    if tool_call_example:
        verify_tool_call_format(tool_call_example)
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n说明:")
    print("- 当 LLM 被问 'Who won the Super Bowl?' 时")
    print("- 它应该输出包含 tool_calls 的响应")
    print("- tool_calls 中应包含对 web_search 函数的调用")
    print("- arguments 应包含查询字符串，如 'Super Bowl winner 2024'")
