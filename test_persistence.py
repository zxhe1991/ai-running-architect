"""
测试数据持久化功能
"""
import os
import json
import pickle
import pandas as pd

print("=" * 60)
print("数据持久化功能测试")
print("=" * 60)

# 1. 测试用户配置加载
print("\n1. 测试用户配置加载:")
if os.path.exists("user_config.json"):
    with open("user_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"   ✓ 配置文件存在")
    print(f"   - 用户资料: {config.get('user_profile', {})}")
    print(f"   - 目标设置: {config.get('goal', {})}")
    print(f"   - 配速单位: {config.get('pace_unit', 'N/A')}")
    print(f"   - 语言: {config.get('language', 'N/A')}")
else:
    print("   ⚠ 配置文件不存在（首次使用时会自动创建）")

# 2. 测试历史数据加载
print("\n2. 测试历史数据加载:")
if os.path.exists("garmin_data.pkl"):
    with open("garmin_data.pkl", 'rb') as f:
        df = pickle.load(f)
    print(f"   ✓ 历史数据文件存在")
    print(f"   - 已索引跑步记录数: {len(df)}")
    print(f"   - 数据列: {', '.join(list(df.columns)[:5])}...")
else:
    print("   ⚠ 历史数据文件不存在")

# 3. 测试索引文件
print("\n3. 测试索引文件:")
if os.path.exists("garmin.index"):
    file_size = os.path.getsize("garmin.index")
    print(f"   ✓ 索引文件存在")
    print(f"   - 文件大小: {file_size:,} 字节")
else:
    print("   ⚠ 索引文件不存在")

# 4. 总结
print("\n" + "=" * 60)
print("测试总结:")
print("=" * 60)
if os.path.exists("garmin.index") and os.path.exists("garmin_data.pkl"):
    print("✓ 历史数据已就绪，应用可以正常使用历史搜索功能")
else:
    print("⚠ 历史数据未构建，需要上传 CSV 文件并构建索引")

if os.path.exists("user_config.json"):
    print("✓ 用户配置已保存，应用重启后会自动加载")
else:
    print("ℹ 用户配置将在首次使用时自动创建和保存")

print("=" * 60)
