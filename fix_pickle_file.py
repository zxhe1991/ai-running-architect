"""
修复 pickle 文件中的 StringDtype 兼容性问题
"""
import pandas as pd
import pickle
import os

print("=" * 60)
print("修复 pickle 文件兼容性")
print("=" * 60)

pickle_file = "garmin_data.pkl"
csv_file = "Garmin_Runing.csv"

if not os.path.exists(pickle_file):
    print(f"✗ {pickle_file} 不存在")
    exit(1)

print(f"\n1. 尝试加载 pickle 文件...")
try:
    with open(pickle_file, 'rb') as f:
        df = pickle.load(f)
    print(f"   ✓ 成功加载，包含 {len(df)} 行")
except Exception as e:
    print(f"   ✗ 加载失败: {e}")
    
    if 'StringDtype' in str(e):
        print(f"\n2. 检测到 StringDtype 错误，从 CSV 重新加载...")
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                print(f"   ✓ 从 CSV 加载成功，包含 {len(df)} 行")
            except Exception as csv_error:
                print(f"   ✗ CSV 加载失败: {csv_error}")
                exit(1)
        else:
            print(f"   ✗ {csv_file} 不存在，无法修复")
            exit(1)
    else:
        print(f"   ✗ 未知错误，无法修复")
        exit(1)

print(f"\n3. 检查并转换 StringDtype 列...")
converted_count = 0
for col in df.columns:
    dtype_str = str(df[col].dtype)
    if 'string' in dtype_str.lower() or 'StringDtype' in dtype_str:
        print(f"   转换列 '{col}': {dtype_str} -> object")
        df[col] = df[col].astype('object')
        converted_count += 1

if converted_count > 0:
    print(f"   ✓ 转换了 {converted_count} 个列")
else:
    print(f"   ℹ 没有需要转换的列")

print(f"\n4. 保存修复后的文件...")
try:
    # Backup original file
    if os.path.exists(pickle_file):
        backup_file = pickle_file + ".backup"
        import shutil
        shutil.copy2(pickle_file, backup_file)
        print(f"   ✓ 已备份原文件到 {backup_file}")
    
    # Save fixed file
    with open(pickle_file, 'wb') as f:
        pickle.dump(df, f)
    print(f"   ✓ 已保存修复后的文件")
    
    # Verify
    print(f"\n5. 验证修复...")
    with open(pickle_file, 'rb') as f:
        df_test = pickle.load(f)
    print(f"   ✓ 验证成功！文件可以正常加载")
    print(f"   - 行数: {len(df_test)}")
    print(f"   - 列数: {len(df_test.columns)}")
    
except Exception as e:
    print(f"   ✗ 保存失败: {e}")
    exit(1)

print(f"\n" + "=" * 60)
print("修复完成！")
print("=" * 60)
print(f"\n现在可以正常使用历史数据搜索功能了。")
