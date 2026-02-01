"""
语音输入功能测试界面
用于测试语音转文字功能
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from app.py
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import transcribe_audio, SUPER_MIND_API_KEY, SUPER_MIND_BASE_URL

st.set_page_config(
    page_title="语音输入测试",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 语音输入功能测试界面")
st.markdown("---")

# Check API configuration
if not SUPER_MIND_API_KEY:
    st.error("❌ API Key 未设置！请在 .env 文件中设置 SUPER_MIND_API_KEY")
    st.stop()

st.success(f"✅ API Key 已配置 (长度: {len(SUPER_MIND_API_KEY)})")
st.info(f"📍 API Base URL: {SUPER_MIND_BASE_URL}")

st.markdown("---")

# Test Section 1: Audio Transcription
st.header("1️⃣ 语音转文字测试")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("上传音频文件")
    st.markdown("""
    **支持的格式：**
    - MP3
    - WAV
    - FLAC
    - OGG
    - M4A
    """)
    
    audio_file = st.file_uploader(
        "选择音频文件",
        type=['mp3', 'wav', 'flac', 'ogg', 'm4a'],
        help="上传一个音频文件进行测试"
    )
    
    language_option = st.selectbox(
        "语言提示（可选）",
        ["自动检测", "中文 (zh-CN)", "英文 (en-US)"],
        help="提供语言提示可以提高识别准确率"
    )
    
    if language_option == "中文 (zh-CN)":
        lang_hint = "zh-CN"
    elif language_option == "英文 (en-US)":
        lang_hint = "en-US"
    else:
        lang_hint = None

with col2:
    st.subheader("转换结果")
    
    if audio_file is not None:
        # Display audio player
        st.audio(audio_file, format=f"audio/{audio_file.name.split('.')[-1]}")
        
        file_size = len(audio_file.read())
        audio_file.seek(0)  # Reset file pointer
        
        st.info(f"📁 文件大小: {file_size / 1024:.2f} KB")
        st.info(f"📝 文件名: {audio_file.name}")
        
        if st.button("🔄 开始转换", type="primary", use_container_width=True):
            with st.spinner("⏳ 正在转换中，请稍候..."):
                audio_bytes = audio_file.read()
                result = transcribe_audio(audio_bytes, lang_hint)
                
                if result['success']:
                    st.success("✅ 转换成功！")
                    
                    # Display transcription
                    st.text_area(
                        "转换结果",
                        value=result['text'],
                        height=200,
                        key='transcription_result'
                    )
                    
                    # Display metadata
                    with st.expander("📊 详细信息"):
                        st.json({
                            "检测到的语言": result.get('detected_language', 'N/A'),
                            "置信度": result.get('confidence', 'N/A'),
                            "文本长度": len(result['text']),
                            "字符数": len(result['text'])
                        })
                    
                    # Store in session state
                    st.session_state.last_transcription = result['text']
                else:
                    st.error(f"❌ 转换失败: {result.get('error', 'Unknown error')}")
    else:
        st.info("👆 请先上传音频文件")

st.markdown("---")

# Test Section 2: Historical Running Info Input
st.header("2️⃣ 历史跑步信息输入测试")

input_method_historical = st.radio(
    "选择输入方式",
    ["文字输入", "语音输入"],
    horizontal=True,
    key='historical_input_method'
)

if input_method_historical == "文字输入":
    historical_text = st.text_area(
        "历史跑步信息",
        placeholder="例如：3个月前开始跑步，刚开始很累，跑5分钟就气喘吁吁，现在可以跑30分钟了...",
        height=100,
        key='historical_text_input'
    )
    
    if historical_text:
        st.success("✅ 文字输入已保存")
        st.session_state.historical_running_info = historical_text
else:
    st.info("💡 请上传音频文件（支持 MP3, WAV, FLAC 等格式）")
    audio_historical = st.file_uploader(
        "上传历史信息音频",
        type=['mp3', 'wav', 'flac', 'ogg', 'm4a'],
        key='historical_audio_uploader'
    )
    
    if audio_historical is not None:
        st.audio(audio_historical, format=f"audio/{audio_historical.name.split('.')[-1]}")
        
        if st.button("🔄 转换历史信息", key='transcribe_historical'):
            with st.spinner("⏳ 正在转换..."):
                audio_bytes = audio_historical.read()
                lang_hint_hist = 'zh-CN' if language_option == "中文 (zh-CN)" else 'en-US'
                result = transcribe_audio(audio_bytes, lang_hint_hist)
                
                if result['success']:
                    st.success("✅ 转换成功！")
                    historical_text = st.text_area(
                        "转换结果",
                        value=result['text'],
                        height=100,
                        key='historical_transcribed'
                    )
                    st.session_state.historical_running_info = result['text']
                else:
                    st.error(f"❌ 转换失败: {result.get('error', 'Unknown error')}")

st.markdown("---")

# Test Section 3: Subjective Feeling Input
st.header("3️⃣ 主观感受输入测试")

input_method_subjective = st.radio(
    "选择输入方式",
    ["文字输入", "语音输入"],
    horizontal=True,
    key='subjective_input_method'
)

if input_method_subjective == "文字输入":
    subjective_text = st.text_area(
        "主观感受",
        placeholder="例如：腿部感觉沉重，感觉很强壮，最后2公里很吃力...",
        height=100,
        key='subjective_text_input'
    )
    
    if subjective_text:
        st.success("✅ 文字输入已保存")
        st.session_state.subjective_feeling = subjective_text
else:
    st.info("💡 请上传音频文件（支持 MP3, WAV, FLAC 等格式）")
    audio_subjective = st.file_uploader(
        "上传主观感受音频",
        type=['mp3', 'wav', 'flac', 'ogg', 'm4a'],
        key='subjective_audio_uploader'
    )
    
    if audio_subjective is not None:
        st.audio(audio_subjective, format=f"audio/{audio_subjective.name.split('.')[-1]}")
        
        if st.button("🔄 转换主观感受", key='transcribe_subjective'):
            with st.spinner("⏳ 正在转换..."):
                audio_bytes = audio_subjective.read()
                lang_hint_subj = 'zh-CN' if language_option == "中文 (zh-CN)" else 'en-US'
                result = transcribe_audio(audio_bytes, lang_hint_subj)
                
                if result['success']:
                    st.success("✅ 转换成功！")
                    subjective_text = st.text_area(
                        "转换结果",
                        value=result['text'],
                        height=100,
                        key='subjective_transcribed'
                    )
                    st.session_state.subjective_feeling = result['text']
                else:
                    st.error(f"❌ 转换失败: {result.get('error', 'Unknown error')}")

st.markdown("---")

# Test Section 4: Summary
st.header("4️⃣ 测试总结")

if st.button("📊 查看所有输入内容", use_container_width=True):
    summary_data = {}
    
    if 'last_transcription' in st.session_state:
        summary_data['最新转换结果'] = st.session_state.last_transcription
    
    if 'historical_running_info' in st.session_state:
        summary_data['历史跑步信息'] = st.session_state.historical_running_info
    
    if 'subjective_feeling' in st.session_state:
        summary_data['主观感受'] = st.session_state.subjective_feeling
    
    if summary_data:
        st.json(summary_data)
        
        # Show how it would be used in coach advice
        st.markdown("### 💡 这些信息将如何被使用：")
        st.info("""
        这些输入的信息将被整合到 AI 教练的建议中：
        
        1. **历史跑步信息** - 帮助教练了解您的跑步背景和进步情况
        2. **主观感受** - 帮助教练评估您的当前状态和训练效果
        
        这些信息将与您的：
        - 用户资料（年龄、性别）
        - 训练目标（目标配速、目标距离、目标日期）
        - 今日跑步数据（如果有）
        - 历史跑步数据（如果有）
        
        一起用于生成个性化的训练建议和计划。
        """)
    else:
        st.warning("⚠️ 还没有输入任何内容，请先完成上面的测试")

st.markdown("---")

# Instructions
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 测试步骤：
    
    1. **语音转文字测试**
       - 上传一个音频文件（建议 1-2 分钟）
       - 选择语言提示（可选）
       - 点击"开始转换"
       - 查看转换结果
    
    2. **历史跑步信息测试**
       - 选择"文字输入"或"语音输入"
       - 如果选择语音，上传音频文件并转换
       - 查看转换后的文字
    
    3. **主观感受测试**
       - 选择"文字输入"或"语音输入"
       - 如果选择语音，上传音频文件并转换
       - 查看转换后的文字
    
    4. **查看总结**
       - 点击"查看所有输入内容"
       - 了解这些信息如何被使用
    
    ### 提示：
    - 音频文件建议清晰、无背景噪音
    - 支持中文和英文语音识别
    - 转换可能需要几秒钟时间
    - 如果转换失败，请检查 API key 是否正确配置
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>测试界面 - AI Running Architect</p>
    <p>使用 space.ai-builders.com 语音转文字 API</p>
</div>
""", unsafe_allow_html=True)
