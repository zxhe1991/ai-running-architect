"""
测试客户端 - 调用教练建议 API
"""
import requests
import json
from csv_analyzer import analyze_csv

BASE_URL = "http://127.0.0.1:8001"

def test_coach_advice():
    """测试教练建议 API"""
    
    print("=" * 60)
    print("测试教练建议 API")
    print("=" * 60)
    
    # 1. 分析今日跑步数据
    print("\n1. 分析今日跑步数据...")
    try:
        today_analysis = analyze_csv("Running_Today.csv")
        print(f"   ✓ 分析成功")
        print(f"   - 距离: {today_analysis['basic_stats'].get('total_distance_km', 'N/A')} km")
        print(f"   - 平均心率: {today_analysis['basic_stats'].get('avg_heart_rate', 'N/A')} bpm")
        print(f"   - 平均配速: {today_analysis['basic_stats'].get('avg_pace_min_km', 'N/A')}")
    except Exception as e:
        print(f"   ✗ 分析失败: {e}")
        return
    
    # 2. 准备请求数据
    print("\n2. 准备请求数据...")
    request_data = {
        "user_profile": {
            "age": 33,
            "gender": "男性"
        },
        "goal": {
            "target_pace": "5:00",
            "target_date": "In 3 months",
            "weekly_hours": 5.0,
            "pace_unit": "km"
        },
        "today_analysis": today_analysis,
        "historical_runs": [],  # 暂时不包含历史数据
        "subjective_feeling": "感觉很好，最后几公里有点累",
        "language": "Chinese"
    }
    
    print(f"   ✓ 请求数据准备完成")
    print(f"   - 用户年龄: {request_data['user_profile']['age']}")
    print(f"   - 目标配速: {request_data['goal']['target_pace']}")
    print(f"   - 语言: {request_data['language']}")
    
    # 3. 调用 API
    print("\n3. 调用教练建议 API...")
    try:
        response = requests.post(
            f"{BASE_URL}/coach/advice",
            json=request_data,
            timeout=120
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n{'='*60}")
            print("API 响应:")
            print(f"{'='*60}")
            print(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                immediate_advice = result.get('immediate_advice', '')
                training_plan = result.get('training_plan', '')
                strategy = result.get('strategy', '')
                
                print(f"\n即时评估与下次训练 ({len(immediate_advice)} 字符):")
                print("-" * 60)
                print(immediate_advice[:500] + ("..." if len(immediate_advice) > 500 else ""))
                
                print(f"\n详细训练计划 ({len(training_plan)} 字符):")
                print("-" * 60)
                print(training_plan[:500] + ("..." if len(training_plan) > 500 else ""))
                
                print(f"\n训练策略与原理 ({len(strategy)} 字符):")
                print("-" * 60)
                print(strategy[:500] + ("..." if len(strategy) > 500 else ""))
                
                # 保存完整响应
                with open("coach_response.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n✓ 完整响应已保存到 coach_response.json")
            else:
                print(f"\n✗ API 返回错误:")
                print(result.get('error', 'Unknown error'))
                print(f"\n原始响应:")
                print(result.get('raw_response', 'N/A'))
        else:
            print(f"   ✗ 请求失败")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ✗ 无法连接到服务器 {BASE_URL}")
        print(f"   请确保测试 API 服务器正在运行:")
        print(f"   py test_coach_api.py")
    except Exception as e:
        print(f"   ✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coach_advice()
