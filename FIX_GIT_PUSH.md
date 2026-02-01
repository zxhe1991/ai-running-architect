# 修复 Git 推送冲突

## 🚨 问题

推送时出现错误：
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs
Updates were rejected because the remote contains work that you do not have locally.
```

## ✅ 解决方案

远程仓库有本地没有的更改，需要先拉取并合并。

### 步骤 1: 拉取远程更改

```bash
git pull origin main --allow-unrelated-histories
```

**说明：**
- `--allow-unrelated-histories` 允许合并不相关的历史记录
- 这会将远程更改合并到本地

### 步骤 2: 解决可能的冲突（如果有）

如果拉取后出现冲突：

1. **查看冲突文件**：
   ```bash
   git status
   ```

2. **打开冲突文件**，查找 `<<<<<<<`, `=======`, `>>>>>>>` 标记

3. **手动解决冲突**：
   - 保留需要的代码
   - 删除冲突标记

4. **标记冲突已解决**：
   ```bash
   git add <冲突文件>
   git commit -m "Merge remote changes"
   ```

### 步骤 3: 推送更改

```bash
git push origin main
```

## 🔄 完整命令序列

如果一切顺利，执行以下命令：

```bash
# 1. 拉取远程更改
git pull origin main --allow-unrelated-histories

# 2. 如果有未提交的更改，先提交
git add app.py
git commit -m "Remove default historical data display, use user-defined data only"

# 3. 推送
git push origin main
```

## ⚠️ 如果仍有问题

### 选项 A: 强制推送（不推荐，除非确定）

```bash
git push origin main --force
```

**警告：** 这会覆盖远程更改，可能导致数据丢失。

### 选项 B: 重新设置远程

```bash
# 查看远程配置
git remote -v

# 如果需要，重新添加远程
git remote remove origin
git remote add origin https://github.com/zxhe1991/ai-running-architect.git
```

## 📝 常见情况

### 情况 1: 远程有新的提交

- **原因**：其他人推送了代码，或通过 Web 界面修改了文件
- **解决**：使用 `git pull` 拉取并合并

### 情况 2: 本地和远程都有更改

- **原因**：本地和远程都修改了同一文件
- **解决**：拉取后解决冲突，然后推送

### 情况 3: 历史记录不相关

- **原因**：本地和远程仓库历史记录不同
- **解决**：使用 `--allow-unrelated-histories` 参数

## ✅ 验证

推送成功后，应该看到：
```
To https://github.com/zxhe1991/ai-running-architect.git
   xxxxxxx..xxxxxxx  main -> main
```

## 🚀 推送后

推送成功后：

1. **等待部署平台检测**（通常 1-2 分钟）
2. **或手动触发部署**：
   ```bash
   python deploy.py
   ```
3. **等待部署完成**（5-10 分钟）
