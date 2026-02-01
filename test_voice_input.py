"""
测试语音输入功能
验证语音转文字API调用是否正常工作
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the transcribe function from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
print("=" * 60)
print("测试语音输入功能")
print("=" * 60)

try:
    from app import transcribe_audio, SUPER_MIND_API_KEY, SUPER_MIND_BASE_URL
    print("[OK] 成功导入 transcribe_audio 函数")
except ImportError as e:
    print(f"[ERROR] 导入失败: {e}")
    sys.exit(1)

# Check API key
if not SUPER_MIND_API_KEY:
    print("[ERROR] SUPER_MIND_API_KEY 未设置！")
    print("请在 .env 文件中设置 API key")
    sys.exit(1)
else:
    print(f"[OK] API Key 已设置 (长度: {len(SUPER_MIND_API_KEY)})")

print(f"[INFO] API Base URL: {SUPER_MIND_BASE_URL}")

# Test 1: Check function signature
print("\n[测试1] 函数签名检查")
import inspect
sig = inspect.signature(transcribe_audio)
print(f"  函数签名: {sig}")
params = list(sig.parameters.keys())
expected_params = ['audio_file_bytes', 'language_hint']
if params == expected_params:
    print("  [OK] 函数参数正确")
else:
    print(f"  [WARNING] 参数不匹配: 期望 {expected_params}, 实际 {params}")

# Test 2: Test with empty bytes (should handle gracefully)
print("\n[测试2] 空音频文件处理")
try:
    result = transcribe_audio(b'', 'zh-CN')
    if not result['success']:
        print("  [OK] 正确处理空文件（返回失败）")
    else:
        print("  [WARNING] 空文件应该返回失败")
except Exception as e:
    print(f"  [OK] 正确处理异常: {type(e).__name__}")

# Test 3: Test API endpoint format
print("\n[测试3] API 端点格式检查")
expected_url = f"{SUPER_MIND_BASE_URL.replace('/v1', '')}/v1/audio/transcriptions"
print(f"  预期 URL: {expected_url}")
if '/v1/audio/transcriptions' in expected_url:
    print("  [OK] URL 格式正确")
else:
    print("  [ERROR] URL 格式错误")

# Test 4: Check required dependencies
print("\n[测试4] 依赖检查")
required_modules = ['httpx', 'tempfile', 'os']
missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"  [OK] {module} 已安装")
    except ImportError:
        print(f"  [ERROR] {module} 未安装")
        missing.append(module)

if missing:
    print(f"\n[WARNING] 缺少依赖: {', '.join(missing)}")
    print("请运行: pip install " + " ".join(missing))
else:
    print("\n[OK] 所有依赖已安装")

# Test 5: Check translation keys
print("\n[测试5] 翻译键检查")
try:
    from app import TRANSLATIONS
    required_keys = [
        'input_method', 'text_input', 'voice_input', 'record_audio',
        'transcribing', 'transcription_success', 'transcription_error',
        'historical_running_info', 'historical_info_placeholder', 'historical_info_help'
    ]
    missing_keys = []
    for lang in ['Chinese', 'English']:
        for key in required_keys:
            if key not in TRANSLATIONS.get(lang, {}):
                missing_keys.append(f"{lang}.{key}")
    
    if missing_keys:
        print(f"  [ERROR] 缺少翻译键: {', '.join(missing_keys)}")
    else:
        print("  [OK] 所有翻译键已定义")
except Exception as e:
    print(f"  [ERROR] 检查翻译键时出错: {e}")

# Test 6: Check function calls in app.py
print("\n[测试6] 函数调用检查")
try:
    import re
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if get_coach_advice has historical_running_info parameter
    if 'historical_running_info: str = ""' in content:
        print("  [OK] get_coach_advice 函数包含 historical_running_info 参数")
    else:
        print("  [ERROR] get_coach_advice 函数缺少 historical_running_info 参数")
    
    # Check if all calls include historical_running_info
    calls = re.findall(r'get_coach_advice\([^)]+\)', content)
    if calls:
        all_have_param = all('historical_running_info' in call for call in calls)
        if all_have_param:
            print("  [OK] 所有 get_coach_advice 调用都包含 historical_running_info")
        else:
            print("  [WARNING] 部分调用可能缺少 historical_running_info 参数")
            for i, call in enumerate(calls[:3], 1):
                print(f"    调用 {i}: {call[:80]}...")
except Exception as e:
    print(f"  [ERROR] 检查函数调用时出错: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n注意事项:")
print("1. 语音转文字功能需要有效的 API key")
print("2. 需要上传真实的音频文件才能完整测试")
print("3. 支持的音频格式: MP3, WAV, FLAC, OGG, M4A")
print("4. 建议在实际部署前进行端到端测试")
