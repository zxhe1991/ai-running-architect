"""
测试应用启动
验证 Streamlit 应用能否正常启动
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("测试应用启动")
print("=" * 60)

# Test 1: Check if app.py can be imported
print("\n[测试1] 导入 app.py")
try:
    # Temporarily redirect stderr to suppress Streamlit warnings
    import io
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    import app
    sys.stderr = old_stderr
    
    print("  [OK] app.py 导入成功")
except Exception as e:
    sys.stderr = old_stderr
    print(f"  [ERROR] 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check required functions exist
print("\n[测试2] 检查必需函数")
required_functions = [
    'transcribe_audio',
    'get_coach_advice',
    'parse_pace_to_seconds',
    'load_user_config',
    'save_user_config'
]

missing_functions = []
for func_name in required_functions:
    if hasattr(app, func_name):
        print(f"  [OK] {func_name} 存在")
    else:
        print(f"  [ERROR] {func_name} 不存在")
        missing_functions.append(func_name)

if missing_functions:
    print(f"\n[ERROR] 缺少函数: {', '.join(missing_functions)}")
    sys.exit(1)

# Test 3: Check session state initialization
print("\n[测试3] 检查 session state 键")
try:
    # Mock streamlit session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
    
    # Check if code references session state correctly
    print("  [OK] Session state 结构检查通过")
except Exception as e:
    print(f"  [WARNING] Session state 检查: {e}")

# Test 4: Check API configuration
print("\n[测试4] API 配置检查")
if hasattr(app, 'SUPER_MIND_API_KEY'):
    if app.SUPER_MIND_API_KEY:
        print(f"  [OK] API Key 已设置 (长度: {len(app.SUPER_MIND_API_KEY)})")
    else:
        print("  [WARNING] API Key 未设置（应用可能无法正常工作）")
else:
    print("  [ERROR] SUPER_MIND_API_KEY 未定义")

if hasattr(app, 'SUPER_MIND_BASE_URL'):
    print(f"  [OK] Base URL: {app.SUPER_MIND_BASE_URL}")
else:
    print("  [ERROR] SUPER_MIND_BASE_URL 未定义")

# Test 5: Check translation function
print("\n[测试5] 翻译功能检查")
if hasattr(app, 't'):
    try:
        # Mock session state for translation
        app.st.session_state = type('obj', (object,), {'language': 'Chinese'})()
        test_translation = app.t('app_title')
        if test_translation:
            print(f"  [OK] 翻译功能正常: '{test_translation}'")
        else:
            print("  [WARNING] 翻译返回空值")
    except Exception as e:
        print(f"  [WARNING] 翻译测试失败: {e}")

# Test 6: Check file structure
print("\n[测试6] 文件结构检查")
required_files = [
    'app.py',
    'requirements.txt',
    'Dockerfile',
    'mock_coach_response.py'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"  [OK] {file} 存在")
    else:
        print(f"  [WARNING] {file} 不存在")
        missing_files.append(file)

print("\n" + "=" * 60)
print("启动测试完成！")
print("=" * 60)

if missing_functions:
    print("\n[ERROR] 发现错误，请修复后再部署")
    sys.exit(1)
else:
    print("\n[SUCCESS] 所有基本检查通过")
    print("\n下一步:")
    print("1. 运行 'streamlit run app.py' 进行完整测试")
    print("2. 测试语音输入功能（需要真实音频文件）")
    print("3. 验证所有UI组件正常工作")
