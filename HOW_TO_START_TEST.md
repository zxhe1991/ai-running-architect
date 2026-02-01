# 🚀 如何启动测试界面

## 方法 1: 使用命令行（推荐）

### Windows PowerShell:
```powershell
cd "C:\Users\zxhe1\OneDrive\Desktop\Cursor Demo"
python -m streamlit run test_voice_interface.py --server.port 8502
```

### 或者使用批处理文件:
双击运行 `start_test_interface.bat`

## 方法 2: 如果主应用正在运行

如果主应用（app.py）正在端口 8501 上运行，测试界面会使用端口 8502，不会冲突。

## 📋 启动步骤

1. **打开 PowerShell 或命令提示符**
2. **切换到项目目录**:
   ```powershell
   cd "C:\Users\zxhe1\OneDrive\Desktop\Cursor Demo"
   ```
3. **运行测试界面**:
   ```powershell
   python -m streamlit run test_voice_interface.py --server.port 8502
   ```
4. **等待服务器启动**（会看到类似这样的输出）:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8502
   ```
5. **浏览器会自动打开**，如果没有，手动访问: http://localhost:8502

## ⚠️ 如果遇到问题

### 问题 1: "python" 命令不存在
**解决**: 使用完整路径
```powershell
C:\Users\zxhe1\AppData\Local\Programs\Python\Python312\python.exe -m streamlit run test_voice_interface.py --server.port 8502
```

### 问题 2: 端口被占用
**解决**: 使用其他端口（如 8503, 8504）
```powershell
python -m streamlit run test_voice_interface.py --server.port 8503
```

### 问题 3: 模块导入错误
**解决**: 确保在项目根目录运行命令

## ✅ 成功启动的标志

看到以下信息说明启动成功：
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8502
Network URL: http://192.168.x.x:8502
```

## 🎯 测试界面功能

启动后，您将看到：
1. **语音转文字测试** - 上传音频文件测试转换
2. **历史跑步信息输入测试** - 测试文字/语音输入
3. **主观感受输入测试** - 测试文字/语音输入
4. **测试总结** - 查看所有输入内容

## 💡 提示

- 保持命令行窗口打开，关闭窗口会停止服务器
- 按 `Ctrl+C` 可以停止服务器
- 修改代码后，界面会自动重新加载
