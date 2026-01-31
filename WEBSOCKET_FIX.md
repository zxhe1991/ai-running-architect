# WebSocket 连接问题修复指南

## 🔍 问题诊断

**错误信息：**
```
WebSocket connection to 'wss://ai-running-architect.ai-builders.space/_stcore/stream' failed
```

**原因：**
Streamlit 应用在反向代理（nginx）后面运行时，需要特殊配置来支持 WebSocket 连接。

## ✅ 已实施的修复

### 1. 创建 Streamlit 配置文件

创建了 `.streamlit/config.toml` 文件，包含以下配置：

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = 8501
```

### 2. 更新 Dockerfile

更新了 CMD 指令，添加了 WebSocket 相关配置：

```dockerfile
CMD sh -c "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=true"
```

## 🚀 部署修复

### 步骤 1: 提交更改

```bash
git add .streamlit/config.toml Dockerfile
git commit -m "Fix WebSocket connection for Streamlit deployment"
```

### 步骤 2: 推送到 GitHub

```bash
git push origin main
```

### 步骤 3: 重新部署

部署平台会自动检测到新的提交并重新部署，或者手动触发：

```bash
python deploy.py
```

## 📋 验证修复

部署完成后：

1. **清除浏览器缓存**：`Ctrl + Shift + Delete`
2. **硬刷新页面**：`Ctrl + F5`
3. **检查浏览器控制台**：应该不再有 WebSocket 错误
4. **测试应用功能**：确保所有功能正常工作

## 🔧 如果问题仍然存在

如果修复后问题仍然存在，可能需要：

1. **检查部署平台配置**：
   - 确保反向代理（nginx）支持 WebSocket 升级
   - 检查是否有 WebSocket 相关的防火墙规则

2. **联系部署平台支持**：
   - 提供错误信息和配置详情
   - 询问 WebSocket 支持配置

3. **替代方案**：
   - 考虑使用其他部署方式
   - 或使用不同的应用框架

## 📚 相关资源

- [Streamlit 部署文档](https://docs.streamlit.io/knowledge-base/deploy/deploy-streamlit-app)
- [WebSocket 配置指南](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
