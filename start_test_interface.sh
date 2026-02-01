#!/bin/bash
echo "========================================"
echo "启动语音输入测试界面"
echo "========================================"
echo ""
echo "测试界面将在浏览器中自动打开"
echo "如果没有自动打开，请访问: http://localhost:8502"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================"
echo ""

python -m streamlit run test_voice_interface.py --server.port 8502
