"""
部署 WebSocket 修复
"""
import subprocess
import os

def deploy_fix():
    """提交并推送 WebSocket 修复"""
    print("=" * 60)
    print("部署 WebSocket 修复")
    print("=" * 60)
    
    # 检查 Git 是否可用
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git 未安装或不可用")
            print("请手动执行以下命令：")
            print("1. git add .streamlit/config.toml Dockerfile")
            print("2. git commit -m 'Fix WebSocket connection for Streamlit'")
            print("3. git push origin main")
            return False
    except FileNotFoundError:
        print("❌ Git 未安装")
        print("请先安装 Git，然后手动执行命令")
        return False
    
    # 检查是否在 Git 仓库中
    if not os.path.exists(".git"):
        print("⚠️  当前目录不是 Git 仓库")
        print("请先初始化 Git 仓库")
        return False
    
    # 添加文件
    print("\n1. 添加文件...")
    result = subprocess.run(["git", "add", ".streamlit/config.toml", "Dockerfile"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 添加文件失败: {result.stderr}")
        return False
    print("   ✅ 文件已添加")
    
    # 提交
    print("\n2. 提交更改...")
    result = subprocess.run(["git", "commit", "-m", "Fix WebSocket connection for Streamlit deployment"], capture_output=True, text=True)
    if result.returncode != 0:
        if "nothing to commit" in result.stdout.lower():
            print("   ⚠️  没有更改需要提交（可能已经提交）")
        else:
            print(f"❌ 提交失败: {result.stderr}")
            return False
    else:
        print("   ✅ 更改已提交")
    
    # 推送
    print("\n3. 推送到 GitHub...")
    result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 推送失败: {result.stderr}")
        print("\n可能的原因：")
        print("- 需要认证（用户名/密码或 token）")
        print("- 网络连接问题")
        print("\n请手动执行: git push origin main")
        return False
    print("   ✅ 代码已推送到 GitHub")
    
    print("\n" + "=" * 60)
    print("✅ WebSocket 修复已部署！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 等待部署平台自动检测到新提交（通常 1-2 分钟）")
    print("2. 或手动触发部署: python deploy.py")
    print("3. 等待 5-10 分钟让部署完成")
    print("4. 清除浏览器缓存并重新访问应用")
    
    return True

if __name__ == "__main__":
    deploy_fix()
