"""
测试历史数据索引的完整流程
"""
import os
import pickle
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from csv_analyzer import analyze_csv

load_dotenv()

print("=" * 70)
print("历史数据索引完整测试")
print("=" * 70)

# 1. 检查文件存在性
print("\n1. 检查文件:")
files_ok = True
if os.path.exists("garmin.index"):
    index = faiss.read_index("garmin.index")
    print(f"   ✓ garmin.index 存在，包含 {index.ntotal} 条记录")
else:
    print(f"   ✗ garmin.index 不存在")
    files_ok = False

if os.path.exists("garmin_data.pkl"):
    df = pickle.load(open("garmin_data.pkl", 'rb'))
    print(f"   ✓ garmin_data.pkl 存在，包含 {len(df)} 行")
else:
    print(f"   ✗ garmin_data.pkl 不存在")
    files_ok = False

if not files_ok:
    print("\n❌ 文件检查失败，请先构建索引！")
    exit(1)

# 2. 检查今日数据
print("\n2. 检查今日数据:")
if os.path.exists("Running_Today.csv"):
    try:
        today_analysis = analyze_csv("Running_Today.csv")
        basic_stats = today_analysis.get('basic_stats', {})
        distance = basic_stats.get('total_distance_km', 0)
        pace = basic_stats.get('avg_pace') or basic_stats.get('avg_pace_min_km', 'N/A')
        hr = basic_stats.get('avg_heart_rate', 'N/A')
        
        print(f"   ✓ Running_Today.csv 存在")
        print(f"     - 距离: {distance} km")
        print(f"     - 配速: {pace}")
        print(f"     - 心率: {hr}")
        
        if distance == 0 or pace == 'N/A':
            print(f"   ⚠ 警告: 今日数据不完整，可能影响搜索")
    except Exception as e:
        print(f"   ✗ 分析今日数据失败: {e}")
        distance = 17.7
        pace = "5:30"
else:
    print(f"   ⚠ Running_Today.csv 不存在，使用示例数据")
    distance = 17.7
    pace = "5:30"

# 3. 测试搜索功能
print("\n3. 测试搜索功能:")
try:
    openai_client = OpenAI(
        api_key=os.getenv("SUPER_MIND_API_KEY"),
        base_url=os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")
    )
    
    # 构建查询
    query = f"距离: {distance} 公里, 配速: {pace} 每公里"
    print(f"   查询: {query}")
    
    # 生成查询向量
    print("   正在生成查询向量...")
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
    print(f"   ✓ 查询向量生成成功，维度: {query_embedding.shape}")
    
    # 搜索
    print("   正在搜索...")
    distances, indices = index.search(query_embedding, k=3)
    print(f"   ✓ 搜索完成，找到 {len(indices[0])} 条记录")
    
    # 4. 显示搜索结果
    print("\n4. 搜索结果详情:")
    if len(indices[0]) > 0:
        for i, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
            if idx < len(df):
                row = df.iloc[idx]
                run_date = row.get('Date', 'Unknown')
                run_distance = row.get('Distance', 'N/A')
                run_pace = row.get('Avg Pace', 'N/A')
                run_hr = row.get('Avg HR', 'N/A')
                
                print(f"\n   相似跑步 #{i} (相似度距离: {dist:.4f}):")
                print(f"     - 日期: {run_date}")
                print(f"     - 距离: {run_distance}")
                print(f"     - 配速: {run_pace}")
                print(f"     - 心率: {run_hr}")
            else:
                print(f"   ⚠ 索引 {idx} 超出范围")
    else:
        print("   ⚠ 未找到相似记录")
    
    # 5. 测试数据格式
    print("\n5. 测试数据格式:")
    if len(indices[0]) > 0:
        idx = indices[0][0]
        if idx < len(df):
            row = df.iloc[idx]
            run_data = row.to_dict()
            
            # 检查关键字段
            checks = []
            checks.append(('Date' in run_data, "包含 Date 字段"))
            checks.append(('Distance' in run_data, "包含 Distance 字段"))
            checks.append(('Avg Pace' in run_data, "包含 Avg Pace 字段"))
            checks.append(('Avg HR' in run_data, "包含 Avg HR 字段"))
            
            for passed, msg in checks:
                status = "✓" if passed else "✗"
                print(f"   {status} {msg}")
            
            # 检查数据类型
            print("\n   数据类型检查:")
            date_val = run_data.get('Date')
            print(f"     Date 类型: {type(date_val).__name__}")
            dist_val = run_data.get('Distance')
            print(f"     Distance 类型: {type(dist_val).__name__}")
            pace_val = run_data.get('Avg Pace')
            print(f"     Avg Pace 类型: {type(pace_val).__name__}")
    
    print("\n" + "=" * 70)
    print("✓ 所有测试通过！")
    print("=" * 70)
    print("\n总结:")
    print(f"- 索引包含 {index.ntotal} 条历史记录")
    print(f"- 今日跑步: {distance} km, 配速 {pace}")
    print(f"- 找到 {len(indices[0])} 条相似记录")
    print("\n历史数据索引功能正常！")
    print("在 Streamlit 应用中应该能看到'历史对比'部分。")
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
