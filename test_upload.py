"""
测试上传端点
"""
import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def test_upload_csv():
    """测试上传 CSV 文件"""
    url = f"{BASE_URL}/upload_running_csv"
    
    csv_file = "Running_Today.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"测试上传 CSV 文件")
    print(f"{'='*60}")
    print(f"文件: {csv_file}")
    print(f"URL: {url}")
    print(f"{'-'*60}")
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n成功!")
            print(f"消息: {result.get('message')}")
            print(f"文件名: {result.get('filename')}")
            print(f"保存为: {result.get('saved_as')}")
            
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"\n分析结果:")
                print(f"  总距离: {analysis.get('basic_stats', {}).get('total_distance_km')} km")
                print(f"  平均心率: {analysis.get('basic_stats', {}).get('avg_heart_rate')} bpm")
        else:
            print(f"\n错误响应:")
            try:
                error_data = response.json()
                print(f"错误详情: {error_data}")
            except:
                print(f"响应文本: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到服务器 {BASE_URL}")
        print("请确保 FastAPI 服务器正在运行！")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


def test_upload_tcx():
    """测试上传 TCX 文件"""
    url = f"{BASE_URL}/upload_tcx"
    
    tcx_file = "Runing_Today.tcx"
    
    if not os.path.exists(tcx_file):
        print(f"\n{tcx_file} 不存在，跳过 TCX 测试")
        return
    
    print(f"\n{'='*60}")
    print(f"测试上传 TCX 文件")
    print(f"{'='*60}")
    print(f"文件: {tcx_file}")
    print(f"URL: {url}")
    print(f"{'-'*60}")
    
    try:
        with open(tcx_file, 'rb') as f:
            files = {'file': (tcx_file, f, 'application/xml')}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n成功!")
            print(f"消息: {result.get('message')}")
        else:
            print(f"\n错误响应:")
            try:
                error_data = response.json()
                print(f"错误详情: {error_data}")
            except:
                print(f"响应文本: {response.text}")
                
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("上传端点测试")
    print("="*60)
    
    test_upload_csv()
    test_upload_tcx()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
