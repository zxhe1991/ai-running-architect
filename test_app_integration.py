"""
测试应用中的历史数据搜索集成
模拟 Streamlit 应用中的搜索流程
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import search_similar_runs
from csv_analyzer import analyze_csv

print("=" * 70)
print("测试应用中的历史数据搜索集成")
print("=" * 70)

# 1. 检查今日数据
print("\n1. 分析今日跑步数据:")
if os.path.exists("Running_Today.csv"):
    try:
        today_analysis = analyze_csv("Running_Today.csv")
        basic_stats = today_analysis.get('basic_stats', {})
        distance = basic_stats.get('total_distance_km', 0)
        pace = basic_stats.get('avg_pace') or basic_stats.get('avg_pace_min_km', 'N/A')
        
        print(f"   ✓ 今日跑步:")
        print(f"     - 距离: {distance} km")
        print(f"     - 配速: {pace}")
        
        # 2. 构建查询（模拟应用中的逻辑）
        print("\n2. 构建搜索查询:")
        query = f"距离: {distance} 公里, 配速: {pace} 每公里"
        print(f"   查询: {query}")
        
        # 3. 执行搜索（使用应用中的函数）
        print("\n3. 执行搜索（使用应用函数）:")
        try:
            historical_runs = search_similar_runs(query, k=3)
            
            if historical_runs:
                print(f"   ✓ 找到 {len(historical_runs)} 条相似的历史跑步记录")
                
                # 4. 显示结果（模拟应用中的显示逻辑）
                print("\n4. 搜索结果（模拟应用显示）:")
                for i, run in enumerate(historical_runs, 1):
                    run_data = run.get('data', {})
                    
                    # 转换为字典（如果必要）
                    if hasattr(run_data, 'to_dict'):
                        run_data = run_data.to_dict()
                    
                    hist_date = run_data.get('Date', 'Unknown')
                    hist_distance = run_data.get('Distance', 0)
                    hist_pace = run_data.get('Avg Pace', 'N/A')
                    hist_hr = run_data.get('Avg HR', 'N/A')
                    
                    similarity_score = run.get('distance', 999)
                    
                    print(f"\n   相似跑步 #{i} (相似度: {similarity_score:.4f}):")
                    print(f"     - 日期: {hist_date}")
                    print(f"     - 距离: {hist_distance}")
                    print(f"     - 配速: {hist_pace}")
                    print(f"     - 心率: {hist_hr}")
                
                print("\n" + "=" * 70)
                print("✓ 集成测试通过！")
                print("=" * 70)
                print("\n在 Streamlit 应用中:")
                print("- 应该显示: '✓ 找到 X 条相似的历史跑步记录'")
                print("- 应该显示: '📚 历史对比' 部分")
                print("- 应该显示: 3条相似跑步记录的详细信息")
            else:
                print("   ℹ 未找到相似的历史跑步记录")
                print("   这可能是因为历史数据与今日跑步差异较大")
        except Exception as e:
            print(f"   ✗ 搜索失败: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"   ✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ✗ Running_Today.csv 不存在")
    print("   请先上传今日跑步数据")
