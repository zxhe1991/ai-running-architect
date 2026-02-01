"""
检查 WebSocket 连接状态
"""
import requests
import json

def check_websocket_support():
    """检查 WebSocket 支持"""
    base_url = "https://ai-running-architect.ai-builders.space"
    
    print("=" * 60)
    print("WebSocket 连接检查")
    print("=" * 60)
    
    # 检查主页面
    print("\n1. 检查主页面...")
    try:
        response = requests.get(base_url + "/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 主页面可访问")
            
            # 检查是否包含 Streamlit 相关脚本
            if "_stcore" in response.text:
                print("   ✅ 检测到 Streamlit 核心脚本")
            else:
                print("   ⚠️  未检测到 Streamlit 核心脚本")
        else:
            print(f"   ❌ 主页面不可访问")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 检查健康检查端点
    print("\n2. 检查健康检查端点...")
    health_endpoints = [
        "/health",
        "/_stcore/health",
        "/_stcore/stream"
    ]
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(base_url + endpoint, timeout=5)
            print(f"   {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   {endpoint}: ❌ {type(e).__name__}")
    
    # 检查 WebSocket 端点（HTTP 请求会失败，但可以检查响应）
    print("\n3. 检查 WebSocket 端点...")
    ws_endpoint = "/_stcore/stream"
    try:
        # WebSocket 端点通常返回 400 或 426（Upgrade Required）
        response = requests.get(base_url + ws_endpoint, timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code in [400, 426]:
            print("   ✅ WebSocket 端点存在（返回预期状态码）")
        else:
            print(f"   ⚠️  意外的状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  {type(e).__name__}: {str(e)[:100]}")
    
    # 检查部署状态
    print("\n4. 检查部署状态...")
    try:
        from deploy import check_deployment_status
        status_data = check_deployment_status('ai-running-architect')
        if status_data:
            print(f"   状态: {status_data.get('status', 'unknown')}")
            print(f"   最后部署: {status_data.get('last_deployed_at', 'N/A')}")
            
            # 检查是否有最近的部署
            if status_data.get('last_deployed_at'):
                print(f"   ✅ 有部署记录")
    except Exception as e:
        print(f"   ⚠️  无法检查: {e}")
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
    print("\n💡 提示：")
    print("- WebSocket 连接需要在浏览器中测试")
    print("- 如果仍有 WebSocket 错误，可能需要等待部署完成")
    print("- 清除浏览器缓存后重试")

if __name__ == "__main__":
    check_websocket_support()
