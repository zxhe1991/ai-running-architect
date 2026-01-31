"""
快速测试脚本 - 验证应用关键功能
"""
import os
import json
import pickle

print("=" * 60)
print("AI Running Architect - 快速测试")
print("=" * 60)

# 1. 检查文件
print("\n1. 检查文件:")
files_to_check = [
    ("app.py", "主应用文件"),
    ("csv_analyzer.py", "CSV 分析器"),
    ("build_index.py", "索引构建脚本"),
    ("Running_Today.csv", "今日跑步数据（可选）"),
    ("Garmin_Runing.csv", "历史跑步数据（可选）"),
    ("garmin.index", "历史数据索引（可选）"),
    ("garmin_data.pkl", "历史数据文件（可选）"),
    (".env", "环境变量配置")
]

for filename, desc in files_to_check:
    exists = os.path.exists(filename)
    status = "✓" if exists else "✗"
    print(f"  {status} {desc}: {filename}")

# 2. 检查环境变量
print("\n2. 检查环境变量:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "SUPER_MIND_API_KEY",
        "SUPER_MIND_BASE_URL"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ✗ {var}: 未设置")
except Exception as e:
    print(f"  ✗ 加载环境变量失败: {e}")

# 3. 检查用户配置
print("\n3. 检查用户配置:")
if os.path.exists("user_config.json"):
    try:
        with open("user_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"  ✓ 用户配置已保存")
        print(f"    - 语言: {config.get('language', 'N/A')}")
        print(f"    - 配速单位: {config.get('pace_unit', 'N/A')}")
        print(f"    - 年龄: {config.get('user_profile', {}).get('age', 'N/A')}")
    except Exception as e:
        print(f"  ✗ 读取配置失败: {e}")
else:
    print("  ℹ 用户配置文件不存在（首次使用时会自动创建）")

# 4. 检查历史数据
print("\n4. 检查历史数据:")
if os.path.exists("garmin.index") and os.path.exists("garmin_data.pkl"):
    try:
        import faiss
        index = faiss.read_index("garmin.index")
        print(f"  ✓ 索引文件存在，包含 {index.ntotal} 条记录")
        
        # 尝试加载 pickle 文件（测试兼容性）
        try:
            import pandas as pd
            with open("garmin_data.pkl", 'rb') as f:
                df = pickle.load(f)
            print(f"  ✓ 数据文件可正常加载，包含 {len(df)} 行")
        except Exception as e:
            print(f"  ⚠ 数据文件加载失败（可能是 StringDtype 问题）: {e}")
            print(f"    建议：重新构建索引")
    except Exception as e:
        print(f"  ✗ 检查索引失败: {e}")
else:
    print("  ℹ 历史数据索引不存在（需要上传 CSV 并构建索引）")

# 5. 检查导入
print("\n5. 检查模块导入:")
modules = [
    ("streamlit", "Streamlit"),
    ("pandas", "Pandas"),
    ("numpy", "NumPy"),
    ("faiss", "FAISS"),
    ("openai", "OpenAI"),
    ("csv_analyzer", "CSV 分析器（本地）")
]

for module_name, desc in modules:
    try:
        __import__(module_name)
        print(f"  ✓ {desc}: {module_name}")
    except ImportError:
        print(f"  ✗ {desc}: {module_name} (未安装)")

# 6. 测试 CSV 分析器
print("\n6. 测试 CSV 分析器:")
if os.path.exists("Running_Today.csv"):
    try:
        from csv_analyzer import analyze_csv
        result = analyze_csv("Running_Today.csv")
        print(f"  ✓ CSV 分析成功")
        print(f"    - 距离: {result.get('basic_stats', {}).get('total_distance_km', 'N/A')} km")
        print(f"    - 平均心率: {result.get('basic_stats', {}).get('avg_heart_rate', 'N/A')} bpm")
    except Exception as e:
        print(f"  ✗ CSV 分析失败: {e}")
else:
    print("  ℹ Running_Today.csv 不存在（需要上传）")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n下一步:")
print("1. 确保 Streamlit 应用正在运行 (http://localhost:8501)")
print("2. 在浏览器中打开应用")
print("3. 按照 TEST_CHECKLIST.md 中的步骤进行测试")
print("=" * 60)
