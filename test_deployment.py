"""
测试部署的应用是否正常工作
"""
import requests
import time

def test_deployment():
    """测试部署的应用"""
    url = "https://ai-running-architect.ai-builders.space/"
    
    print("=" * 60)
    print("测试部署的应用")
    print("=" * 60)
    print(f"\n🌐 测试 URL: {url}")
    
    # 测试根路径
    print("\n1. 测试根路径...")
    try:
        response = requests.get(url, timeout=30, allow_redirects=True)
        print(f"   Status Code: {response.status_code}")
        print(f"   URL (最终): {response.url}")
        print(f"   Response Length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            print("   ✅ 应用响应正常")
            
            # 检查是否是 Streamlit 应用
            if "streamlit" in response.text.lower() or "AI Running Architect" in response.text:
                print("   ✅ 检测到 Streamlit 应用")
            
            # 显示响应头
            print(f"\n   响应头:")
            for key, value in response.headers.items():
                if key.lower() in ['content-type', 'server', 'x-frame-options']:
                    print(f"     {key}: {value}")
            
            # 显示响应内容的前几行
            print(f"\n   响应内容预览（前 500 字符）:")
            print(f"   {response.text[:500]}")
            
        elif response.status_code == 404:
            print("   ❌ 404 - 页面未找到")
            print("   可能原因：应用路径配置错误")
        elif response.status_code == 502:
            print("   ❌ 502 - Bad Gateway")
            print("   可能原因：应用正在启动或崩溃")
        elif response.status_code == 503:
            print("   ❌ 503 - Service Unavailable")
            print("   可能原因：应用暂时不可用")
        else:
            print(f"   ⚠️  意外的状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时（30秒）")
        print("   可能原因：应用启动时间较长或网络问题")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 连接错误: {e}")
        print("   可能原因：")
        print("   - DNS 解析失败")
        print("   - 服务器不可达")
        print("   - 应用未启动")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试健康检查端点（如果有）
    print("\n2. 测试健康检查...")
    health_urls = [
        url + "health",
        url + "_stcore/health",
        url + "api/health"
    ]
    
    for health_url in health_urls:
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {health_url} - 健康检查通过")
                break
        except:
            pass
    
    # 检查部署状态
    print("\n3. 检查部署状态...")
    try:
        from deploy import check_deployment_status
        status_data = check_deployment_status('ai-running-architect')
        if status_data:
            print(f"   状态: {status_data.get('status', 'unknown')}")
            print(f"   URL: {status_data.get('public_url', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️  无法检查部署状态: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_deployment()
