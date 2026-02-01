"""
修复 Git 推送冲突
"""
import subprocess
import os

def fix_git_push():
    """拉取远程更改并推送"""
    print("=" * 60)
    print("修复 Git 推送冲突")
    print("=" * 60)
    
    # 检查 Git 是否可用
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git 未安装或不可用")
            return False
    except FileNotFoundError:
        print("❌ Git 未安装")
        return False
    
    # 检查是否在 Git 仓库中
    if not os.path.exists(".git"):
        print("⚠️  当前目录不是 Git 仓库")
        return False
    
    # 1. 先拉取远程更改
    print("\n1. 拉取远程更改...")
    print("   执行: git pull origin main --allow-unrelated-histories")
    result = subprocess.run(["git", "pull", "origin", "main", "--allow-unrelated-histories"], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"   ⚠️  拉取时可能有冲突: {result.stderr}")
        print("\n   如果出现合并冲突，需要手动解决：")
        print("   1. 检查冲突文件")
        print("   2. 解决冲突")
        print("   3. git add <冲突文件>")
        print("   4. git commit -m 'Merge remote changes'")
        print("   5. git push origin main")
        return False
    else:
        print("   ✅ 远程更改已拉取")
        if result.stdout:
            print(f"   输出: {result.stdout[:200]}")
    
    # 2. 检查状态
    print("\n2. 检查当前状态...")
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    print(result.stdout)
    
    # 3. 如果有未提交的更改，先添加
    print("\n3. 检查是否有未提交的更改...")
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    if result.stdout.strip():
        print("   发现未提交的更改，正在添加...")
        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Update: Remove default historical data display"], 
                      capture_output=True)
        print("   ✅ 更改已提交")
    
    # 4. 推送
    print("\n4. 推送到 GitHub...")
    result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 推送失败: {result.stderr}")
        return False
    else:
        print("   ✅ 代码已成功推送到 GitHub")
        return True

if __name__ == "__main__":
    success = fix_git_push()
    if success:
        print("\n" + "=" * 60)
        print("✅ 代码已成功推送！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 等待部署平台自动检测到新提交（通常 1-2 分钟）")
        print("2. 或手动触发部署: python deploy.py")
    else:
        print("\n" + "=" * 60)
        print("⚠️  需要手动处理")
        print("=" * 60)
