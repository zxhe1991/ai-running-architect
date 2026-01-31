"""
测试历史数据搜索功能
"""
import os
import pickle
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from csv_analyzer import analyze_csv

load_dotenv()

print("=" * 60)
print("测试历史数据搜索功能")
print("=" * 60)

# 1. 检查文件
print("\n1. 检查文件:")
if os.path.exists("garmin.index"):
    index = faiss.read_index("garmin.index")
    print(f"   ✓ garmin.index 存在，包含 {index.ntotal} 条记录")
else:
    print(f"   ✗ garmin.index 不存在")
    exit(1)

if os.path.exists("garmin_data.pkl"):
    df = pickle.load(open("garmin_data.pkl", 'rb'))
    print(f"   ✓ garmin_data.pkl 存在，包含 {len(df)} 行")
else:
    print(f"   ✗ garmin_data.pkl 不存在")
    exit(1)

# 2. 分析今日跑步数据
print("\n2. 分析今日跑步数据:")
if os.path.exists("Running_Today.csv"):
    today_analysis = analyze_csv("Running_Today.csv")
    basic_stats = today_analysis.get('basic_stats', {})
    distance = basic_stats.get('total_distance_km', 0)
    pace = basic_stats.get('avg_pace') or basic_stats.get('avg_pace_min_km', 'N/A')
    print(f"   ✓ 今日跑步:")
    print(f"     - 距离: {distance} km")
    print(f"     - 配速: {pace}")
else:
    print(f"   ⚠ Running_Today.csv 不存在，使用示例数据")
    distance = 17.7
    pace = "5:30"

# 3. 构建查询
print("\n3. 构建搜索查询:")
query = f"距离: {distance} 公里, 配速: {pace} 每公里"
print(f"   查询: {query}")

# 4. 执行搜索
print("\n4. 执行搜索:")
try:
    openai_client = OpenAI(
        api_key=os.getenv("SUPER_MIND_API_KEY"),
        base_url=os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")
    )
    
    # 生成查询向量
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
    print(f"   ✓ 查询向量生成成功，维度: {query_embedding.shape}")
    
    # 搜索
    distances, indices = index.search(query_embedding, k=3)
    print(f"   ✓ 搜索完成")
    print(f"     找到 {len(indices[0])} 条相似记录")
    
    # 5. 显示结果
    print("\n5. 搜索结果:")
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
    
    print("\n" + "=" * 60)
    print("搜索功能正常！")
    print("=" * 60)
    print("\n历史数据索引的用途:")
    print("1. 找到历史上相似距离和配速的跑步")
    print("2. 将这些相似跑步作为上下文提供给 AI 教练")
    print("3. 帮助 AI 生成更个性化的训练建议")
    print("4. 在界面上显示'历史对比'部分，让用户了解自己的进步")
    
except Exception as e:
    print(f"\n✗ 搜索失败: {e}")
    import traceback
    traceback.print_exc()
