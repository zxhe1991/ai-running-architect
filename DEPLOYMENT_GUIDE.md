# 部署指南 - AI Running Architect

本指南将帮助您将 AI Running Architect 应用部署到 `ai-builders.space` 平台。

## 📋 前置要求

1. **GitHub 公开仓库** - 您的代码必须在一个公开的 GitHub 仓库中
2. **API Key** - 您需要 `SUPER_MIND_API_KEY`（已在 `.env` 文件中配置）
3. **所有代码已提交** - 确保所有更改都已提交并推送到 GitHub

## 🚀 部署步骤

### 步骤 1: 准备 GitHub 仓库

1. 在 GitHub 上创建一个新的公开仓库（如果还没有）
2. 将您的代码推送到仓库：
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Running Architect"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

### 步骤 2: 更新部署配置

编辑 `deploy-config.json` 文件，填入您的信息：

```json
{
  "repo_url": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME",
  "service_name": "ai-running-architect",
  "branch": "main",
  "port": 8501,
  "env_vars": {
    "SUPER_MIND_API_KEY": "your_api_key_here",
    "SUPER_MIND_BASE_URL": "https://space.ai-builders.com/backend/v1"
  }
}
```

**重要提示：**
- `service_name` 必须是唯一的，将作为您的子域名：`https://ai-running-architect.ai-builders.space`
- `service_name` 只能包含小写字母、数字和连字符（3-32 个字符）
- 确保 `SUPER_MIND_API_KEY` 在 `env_vars` 中（虽然平台也会自动注入 `AI_BUILDER_TOKEN`）

### 步骤 3: 确保代码已推送

**重要：** 部署系统直接从 GitHub 拉取代码。在部署之前，确保：

1. 所有文件都已提交：
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   ```

2. 所有更改都已推送到 GitHub：
   ```bash
   git push
   ```

### 步骤 4: 运行部署脚本

```bash
python deploy.py
```

部署脚本会：
- 读取 `deploy-config.json` 配置
- 调用部署 API
- 显示部署状态和日志

### 步骤 5: 等待部署完成

- 部署通常需要 **5-10 分钟**
- 您可以通过以下方式检查状态：
  ```bash
  python deploy.py --status ai-running-architect
  ```

## 📝 部署后

部署成功后，您将获得：
- **公共 URL**: `https://ai-running-architect.ai-builders.space`
- 应用将自动运行，无需手动启动

## 🔍 检查部署状态

### 使用脚本检查：
```bash
python deploy.py --status ai-running-architect
```

### 使用 API 检查：
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://space.ai-builders.com/backend/v1/deployments/ai-running-architect
```

## 🐛 故障排除

### 部署失败？

1. **检查构建日志**：
   - 部署响应中包含 `streaming_logs`，查看是否有错误
   - 使用 API 获取完整日志：
     ```bash
     GET /v1/deployments/{service_name}/logs?log_type=build
     ```

2. **常见问题**：
   - ❌ Dockerfile 不存在或格式错误
   - ❌ 端口配置错误（应该使用 PORT 环境变量）
   - ❌ 依赖安装失败（检查 requirements.txt）
   - ❌ GitHub 仓库是私有的（必须是公开的）

3. **检查 Dockerfile**：
   - 确保使用 shell 形式：`CMD sh -c "streamlit run app.py --server.port=${PORT:-8501}"`
   - 确保暴露了正确的端口

## 📚 更多信息

- 部署 API 文档：https://www.ai-builders.com/resources/students-backend/openapi.json
- 平台限制：
  - 免费托管 12 个月
  - 每个用户最多 2 个服务（默认）
  - 256 MB RAM 限制

## 💡 提示

- 部署后，您的应用会自动使用 `AI_BUILDER_TOKEN` 环境变量（平台自动注入）
- 如果需要其他环境变量，在 `deploy-config.json` 的 `env_vars` 中添加
- 不要将敏感信息提交到 Git（使用 `.gitignore`）
