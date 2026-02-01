"""
简单的测试服务器 - 用于诊断问题
"""
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="简单测试",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 简单测试服务器")
st.success("✅ 服务器运行正常！")

st.markdown("---")
st.header("系统信息")

try:
    from app import SUPER_MIND_API_KEY, SUPER_MIND_BASE_URL
    st.success(f"✅ API Key 已配置 (长度: {len(SUPER_MIND_API_KEY)})")
    st.info(f"📍 Base URL: {SUPER_MIND_BASE_URL}")
except Exception as e:
    st.error(f"❌ 导入错误: {e}")

st.markdown("---")
st.header("功能测试")

if st.button("测试导入 transcribe_audio"):
    try:
        from app import transcribe_audio
        st.success("✅ transcribe_audio 函数导入成功")
    except Exception as e:
        st.error(f"❌ 导入失败: {e}")

st.markdown("---")
st.info("如果看到这个页面，说明 Streamlit 服务器运行正常！")
