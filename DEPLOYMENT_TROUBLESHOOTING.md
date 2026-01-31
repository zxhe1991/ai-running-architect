# 部署故障排除指南

## 🚨 当前问题

**错误信息：**
```
Failed to get the SHA of the commit in github.com/zxhe1991/ai-running-architect/main
Status: Unhealthy
Provisioning has failed
```

## 🔍 问题诊断

这个错误表示部署系统无法从 GitHub 仓库获取代码。可能的原因：

### 1. GitHub 仓库不存在或不可访问
- 仓库 URL 可能不正确
- 仓库可能已被删除
- 网络连接问题

### 2. 仓库是私有的
- **部署系统需要公开仓库**
- 私有仓库无法被部署系统访问

### 3. 分支不存在
- `main` 分支可能不存在
- 分支名称可能不同（如 `master`）

### 4. 仓库中没有提交
- 仓库可能是空的
- 没有提交到 `main` 分支

### 5. 仓库 URL 格式错误
- URL 格式不正确
- 缺少 `.git` 后缀

## ✅ 解决方案

### 步骤 1: 验证 GitHub 仓库

1. **访问仓库 URL**：
   ```
   https://github.com/zxhe1991/ai-running-architect
   ```

2. **检查仓库状态**：
   - ✅ 仓库是否存在？
   - ✅ 仓库是否为**公开**（Public）？
   - ✅ 是否有 `main` 分支？
   - ✅ 是否有提交记录？

### 步骤 2: 确保仓库是公开的

如果仓库是私有的，需要改为公开：

1. 访问仓库设置：`Settings` → `General`
2. 滚动到底部找到 `Danger Zone`
3. 点击 `Change visibility` → `Make public`
4. 确认更改

### 步骤 3: 确保代码已推送到 GitHub

如果本地有代码但未推送到 GitHub：

1. **检查本地 Git 状态**：
   ```bash
   git status
   ```

2. **添加所有文件**：
   ```bash
   git add .
   ```

3. **提交更改**：
   ```bash
   git commit -m "Prepare for deployment"
   ```

4. **推送到 GitHub**：
   ```bash
   git push origin main
   ```

### 步骤 4: 验证分支名称

如果分支不是 `main`，需要：

1. **检查当前分支**：
   ```bash
   git branch
   ```

2. **如果分支是 `master`**：
   - 选项 A: 重命名为 `main`
     ```bash
     git branch -M main
     git push -u origin main
     ```
   - 选项 B: 更新 `deploy-config.json` 中的 `branch` 为 `master`

### 步骤 5: 创建 GitHub 仓库（如果不存在）

如果仓库不存在，需要创建：

1. **在 GitHub 上创建新仓库**：
   - 访问：https://github.com/new
   - 仓库名：`ai-running-architect`
   - 选择：**Public**（公开）
   - 不要初始化 README、.gitignore 或 license

2. **在本地初始化并推送**：
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Running Architect"
   git branch -M main
   git remote add origin https://github.com/zxhe1991/ai-running-architect.git
   git push -u origin main
   ```

### 步骤 6: 验证仓库 URL 格式

确保 `deploy-config.json` 中的 URL 格式正确：

```json
{
  "repo_url": "https://github.com/zxhe1991/ai-running-architect.git",
  "service_name": "ai-running-architect",
  "branch": "main",
  "port": 8501
}
```

**重要：**
- URL 必须以 `.git` 结尾
- 使用 `https://` 协议
- 用户名和仓库名正确

### 步骤 7: 重新部署

修复问题后，重新部署：

```bash
python deploy.py
```

## 🔧 快速检查清单

在重新部署前，请确认：

- [ ] GitHub 仓库存在：https://github.com/zxhe1991/ai-running-architect
- [ ] 仓库是**公开**的（Public）
- [ ] 仓库有 `main` 分支
- [ ] 仓库中有提交记录（至少有一个 commit）
- [ ] `deploy-config.json` 中的 `repo_url` 正确
- [ ] `deploy-config.json` 中的 `branch` 是 `main`
- [ ] 本地代码已推送到 GitHub

## 📝 常见问题

### Q: 如何检查仓库是否为公开？

A: 访问仓库 URL，如果看到 "Public" 标签，说明是公开的。如果是 "Private"，需要改为公开。

### Q: 如何检查分支是否存在？

A: 在 GitHub 仓库页面，点击分支下拉菜单，查看是否有 `main` 分支。

### Q: 如何检查是否有提交？

A: 在 GitHub 仓库页面，应该能看到文件列表。如果是空仓库，会显示 "No commits yet"。

### Q: 部署系统需要什么权限？

A: 部署系统只需要**读取**公开仓库的权限，不需要任何特殊权限或 token。

## 🆘 如果问题仍然存在

如果按照上述步骤操作后问题仍然存在：

1. **检查部署日志**：
   - 使用部署 API 获取详细日志
   - 查看是否有其他错误信息

2. **联系支持**：
   - 联系 `ai-builders.space` 支持团队
   - 提供错误信息和仓库 URL

3. **尝试替代方案**：
   - 检查是否有其他部署方式
   - 考虑使用其他部署平台

## 📚 相关文档

- [部署指南](DEPLOYMENT_GUIDE.md)
- [部署脚本](deploy.py)
- [部署配置](deploy-config.json)
