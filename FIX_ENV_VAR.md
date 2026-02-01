# 修复环境变量问题

## 🚨 问题

部署时出现错误：
```
ValueError: SUPER_MIND_API_KEY environment variable not set!
```

## ✅ 已实施的修复

### 1. 更新 `build_index.py` 和 `app.py`

代码现在会尝试两个环境变量：
1. `SUPER_MIND_API_KEY`（本地开发）
2. `AI_BUILDER_TOKEN`（部署平台自动注入）

### 2. 更新部署配置

需要在 `deploy-config.json` 中添加 `SUPER_MIND_API_KEY`。

## 📋 需要执行的操作

### 选项 1: 添加 API Key 到部署配置（推荐）

编辑 `deploy-config.json`，添加 `SUPER_MIND_API_KEY`：

```json
{
  "repo_url": "https://github.com/zxhe1991/ai-running-architect.git",
  "service_name": "ai-running-architect",
  "branch": "main",
  "port": 8501,
  "env_vars": {
    "SUPER_MIND_API_KEY": "your_api_key_here",
    "SUPER_MIND_BASE_URL": "https://space.ai-builders.com/backend/v1"
  }
}
```

**重要：** 将 `your_api_key_here` 替换为实际的 API key。

### 选项 2: 使用平台自动注入的 Token

如果部署平台自动注入 `AI_BUILDER_TOKEN`，代码已经支持使用它。

## 🚀 部署步骤

1. **更新 `deploy-config.json`**（添加 API key）
2. **提交代码更改**：
   ```bash
   git add build_index.py app.py deploy-config.json
   git commit -m "Fix environment variable handling for deployment"
   git push origin main
   ```
3. **重新部署**：
   ```bash
   python deploy.py
   ```

## ⚠️ 安全提示

- **不要**将包含真实 API key 的 `deploy-config.json` 提交到 GitHub
- 使用 `.gitignore` 排除 `deploy-config.json`（如果包含敏感信息）
- 或者使用部署平台的环境变量配置界面

## 📝 注意事项

- `.env` 文件在部署环境中不会被使用
- 环境变量必须通过 `deploy-config.json` 的 `env_vars` 设置
- 或者依赖部署平台自动注入的环境变量
