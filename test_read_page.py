"""
测试 read_page 工具和组合工具调用
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_read_page_tool():
    """测试需要 web_search 和 read_page 的组合查询"""
    url = f"{BASE_URL}/chat"
    
    # 测试查询：搜索 Python 最新版本，然后读取官方 changelog
    test_query = "Search for the latest release of Python, then read the official changelog page to tell me the new features."
    
    request_body = {
        "user_message": test_query
    }
    
    print(f"\n{'='*60}")
    print(f"测试组合工具调用")
    print(f"{'='*60}")
    print(f"查询: {test_query}")
    print(f"{'-'*60}")
    
    try:
        response = requests.post(url, json=request_body, timeout=180)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            json_data = response.json()
            print(f"\n响应:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            print(f"\n{'='*60}")
            print(f"AI 回复:")
            print(f"{'='*60}")
            print(json_data.get('response', 'N/A'))
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 无法连接到服务器 {BASE_URL}")
        print("请确保 FastAPI 服务器正在运行！")
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")


def test_direct_read_page():
    """直接测试 read_page 函数"""
    print(f"\n{'='*60}")
    print(f"直接测试 read_page 函数")
    print(f"{'='*60}")
    
    try:
        from main import read_page
        
        # 测试读取一个简单的页面
        test_url = "https://www.python.org/downloads/"
        print(f"测试 URL: {test_url}")
        
        result = read_page(test_url)
        
        if result["success"]:
            print(f"\n[OK] 页面读取成功")
            print(f"内容长度: {len(result['content'])} 字符")
            print(f"\n内容预览 (前 500 字符):")
            print(result['content'][:500])
        else:
            print(f"\n[FAIL] 页面读取失败: {result.get('error')}")
            
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")


if __name__ == "__main__":
    print("="*60)
    print("read_page 工具测试程序")
    print("="*60)
    
    # 先测试直接函数调用
    test_direct_read_page()
    
    # 再测试组合工具调用
    test_read_page_tool()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
