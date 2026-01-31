"""
快速测试应用的关键功能
"""
import os
import pickle
import pandas as pd
from dotenv import load_dotenv

print("=" * 60)
print("快速功能测试")
print("=" * 60)

# 1. 检查环境配置
print("\n1. 检查环境配置:")
load_dotenv()
mock_response = os.getenv("USE_MOCK_RESPONSE", "false")
print(f"   USE_MOCK_RESPONSE = {mock_response} ({'✓ 已启用' if mock_response.lower() == 'true' else '✗ 未启用'})")

# 2. 检查 pickle 文件
print("\n2. 检查 pickle 文件:")
try:
    df = pickle.load(open("garmin_data.pkl", 'rb'))
    print(f"   ✓ 文件可以正常加载")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}")
    
    # 检查数据类型
    string_cols = []
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        if 'string' in dtype_str.lower() or 'StringDtype' in dtype_str:
            string_cols.append(col)
    
    if string_cols:
        print(f"   ⚠ 仍有 StringDtype 列: {string_cols[:3]}")
    else:
        print(f"   ✓ 没有 StringDtype 列（已修复）")
except Exception as e:
    print(f"   ✗ 加载失败: {e}")

# 3. 检查模拟响应模块
print("\n3. 检查模拟响应模块:")
try:
    from mock_coach_response import get_mock_coach_advice
    result = get_mock_coach_advice(
        {'age': 33, 'gender': '男性'},
        {'target_pace': '5:00', 'target_date': 'In 3 months', 'weekly_hours': 5.0},
        {'basic_stats': {'total_distance_km': 17.7, 'avg_heart_rate': 156.6}},
        [],
        '感觉很好',
        'Chinese'
    )
    print(f"   ✓ 模拟响应模块正常")
    print(f"   - immediate_advice: {len(result['immediate_advice'])} 字符")
    print(f"   - training_plan: {len(result['training_plan'])} 字符")
    print(f"   - strategy: {len(result['strategy'])} 字符")
except Exception as e:
    print(f"   ✗ 模块错误: {e}")

# 4. 检查 CSV 分析器
print("\n4. 检查 CSV 分析器:")
if os.path.exists("Running_Today.csv"):
    try:
        from csv_analyzer import analyze_csv
        result = analyze_csv("Running_Today.csv")
        print(f"   ✓ CSV 分析器正常")
        print(f"   - 距离: {result['basic_stats'].get('total_distance_km', 'N/A')} km")
        print(f"   - 平均心率: {result['basic_stats'].get('avg_heart_rate', 'N/A')} bpm")
    except Exception as e:
        print(f"   ✗ CSV 分析失败: {e}")
else:
    print(f"   ℹ Running_Today.csv 不存在（需要上传）")

# 5. 检查应用导入
print("\n5. 检查应用导入:")
try:
    import app
    print(f"   ✓ app.py 可以正常导入")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n下一步:")
print("1. 在浏览器中打开 http://localhost:8501")
print("2. 按照 TESTING_STEPS.md 中的步骤进行测试")
print("3. 验证所有功能是否正常")
