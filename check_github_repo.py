"""
检查 GitHub 仓库状态，帮助诊断部署问题
"""
import requests
import json

def check_github_repo(username, repo_name):
    """检查 GitHub 仓库状态"""
    print("=" * 60)
    print("GitHub 仓库状态检查")
    print("=" * 60)
    
    # GitHub API URL
    api_url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    print(f"\n📦 检查仓库: {username}/{repo_name}")
    print(f"   API URL: {api_url}")
    print(f"   网页 URL: https://github.com/{username}/{repo_name}")
    
    try:
        # 发送请求（不需要认证，因为检查公开仓库）
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ 仓库存在！")
            print(f"   名称: {data.get('full_name', 'N/A')}")
            print(f"   描述: {data.get('description', 'N/A')}")
            print(f"   可见性: {'🔓 公开 (Public)' if not data.get('private', True) else '🔒 私有 (Private)'}")
            print(f"   默认分支: {data.get('default_branch', 'N/A')}")
            print(f"   星标数: {data.get('stargazers_count', 0)}")
            print(f"   最后更新: {data.get('updated_at', 'N/A')}")
            
            # 检查是否为公开仓库
            if data.get('private', True):
                print(f"\n⚠️  警告: 仓库是私有的！")
                print(f"   部署系统需要公开仓库。")
                print(f"   请将仓库改为公开：")
                print(f"   1. 访问: https://github.com/{username}/{repo_name}/settings")
                print(f"   2. 滚动到底部 'Danger Zone'")
                print(f"   3. 点击 'Change visibility' → 'Make public'")
            else:
                print(f"\n✅ 仓库是公开的，符合部署要求")
            
            # 检查默认分支
            default_branch = data.get('default_branch', '')
            if default_branch != 'main':
                print(f"\n⚠️  警告: 默认分支是 '{default_branch}'，不是 'main'")
                print(f"   请更新 deploy-config.json 中的 'branch' 为 '{default_branch}'")
            else:
                print(f"\n✅ 默认分支是 'main'，符合配置")
            
            # 检查分支
            branches_url = f"https://api.github.com/repos/{username}/{repo_name}/branches"
            branches_response = requests.get(branches_url, timeout=10)
            if branches_response.status_code == 200:
                branches = branches_response.json()
                branch_names = [b['name'] for b in branches]
                print(f"\n📋 可用分支: {', '.join(branch_names)}")
                
                if 'main' not in branch_names:
                    print(f"\n⚠️  警告: 没有找到 'main' 分支！")
                    if branch_names:
                        print(f"   可用分支: {', '.join(branch_names)}")
                        print(f"   请更新 deploy-config.json 中的 'branch'")
            
            # 检查提交
            commits = []
            commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
            commits_response = requests.get(commits_url, params={'per_page': 1}, timeout=10)
            if commits_response.status_code == 200:
                commits = commits_response.json()
                if commits:
                    latest_commit = commits[0]
                    print(f"\n✅ 有提交记录")
                    print(f"   最新提交: {latest_commit.get('sha', 'N/A')[:7]}")
                    print(f"   提交信息: {latest_commit.get('commit', {}).get('message', 'N/A')[:50]}")
                else:
                    print(f"\n⚠️  警告: 仓库中没有提交记录！")
                    print(f"   请确保代码已提交并推送到 GitHub")
            else:
                print(f"\n⚠️  警告: 无法检查提交记录（HTTP {commits_response.status_code}）")
            
            # 总结
            print(f"\n" + "=" * 60)
            print("检查总结")
            print("=" * 60)
            
            issues = []
            if data.get('private', True):
                issues.append("❌ 仓库是私有的（需要改为公开）")
            else:
                print("✅ 仓库是公开的")
            
            if default_branch != 'main':
                issues.append(f"⚠️  默认分支是 '{default_branch}'（需要更新配置）")
            else:
                print("✅ 默认分支是 'main'")
            
            if not commits:
                issues.append("❌ 仓库中没有提交记录")
            else:
                print("✅ 有提交记录")
            
            if issues:
                print(f"\n需要修复的问题：")
                for issue in issues:
                    print(f"   {issue}")
                print(f"\n修复后，可以重新尝试部署。")
            else:
                print(f"\n✅ 所有检查通过！仓库配置正确，可以部署。")
            
            return True
            
        elif response.status_code == 404:
            print(f"\n❌ 错误: 仓库不存在或无法访问")
            print(f"   可能的原因：")
            print(f"   1. 仓库不存在")
            print(f"   2. 仓库名称拼写错误")
            print(f"   3. 用户名不正确")
            print(f"\n请检查：")
            print(f"   - 仓库 URL: https://github.com/{username}/{repo_name}")
            print(f"   - 如果仓库不存在，请创建它")
            return False
            
        else:
            print(f"\n❌ 错误: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络错误: {e}")
        print(f"   请检查网络连接")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        return False


if __name__ == "__main__":
    # 从 deploy-config.json 读取配置
    try:
        with open("deploy-config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        repo_url = config.get("repo_url", "")
        
        # 解析 GitHub URL
        if "github.com" in repo_url:
            # 提取用户名和仓库名
            # 格式: https://github.com/username/repo.git
            parts = repo_url.replace(".git", "").split("/")
            if len(parts) >= 2:
                username = parts[-2]
                repo_name = parts[-1]
                
                check_github_repo(username, repo_name)
            else:
                print("❌ 无法解析仓库 URL")
                print(f"   URL: {repo_url}")
        else:
            print("❌ 不是 GitHub 仓库 URL")
            print(f"   URL: {repo_url}")
            
    except FileNotFoundError:
        print("❌ deploy-config.json 文件不存在")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")
