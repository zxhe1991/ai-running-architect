"""
修复 .env 文件，添加 USE_MOCK_RESPONSE=true
"""
import os
import re

env_file = ".env"

# 读取现有内容
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
else:
    content = ""

# 移除旧的 USE_MOCK_RESPONSE 行（如果有）
content = re.sub(r'USE_MOCK_RESPONSE=.*\n?', '', content)
content = re.sub(r'# 使用模拟响应.*\n?', '', content)

# 确保文件以换行符结尾
content = content.rstrip() + '\n'

# 添加新的配置
if 'USE_MOCK_RESPONSE' not in content:
    content += '\n# 使用模拟响应（当 API 返回空响应时）\n'
    content += 'USE_MOCK_RESPONSE=true\n'

# 写入文件
with open(env_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ .env 文件已更新")
print("\n当前 USE_MOCK_RESPONSE 配置:")
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        if 'USE_MOCK_RESPONSE' in line:
            print(f"  {line.strip()}")

# 验证
from dotenv import load_dotenv
load_dotenv()
mock = os.getenv('USE_MOCK_RESPONSE', 'false')
print(f"\n✓ 验证: USE_MOCK_RESPONSE = {mock}")
print(f"  状态: {'已启用' if mock.lower() == 'true' else '未启用'}")
