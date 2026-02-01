"""
更新部署配置，添加 SUPER_MIND_API_KEY
"""
import json
import os
from dotenv import load_dotenv

def update_deploy_config():
    """更新部署配置"""
    print("=" * 60)
    print("更新部署配置")
    print("=" * 60)
    
    # 加载 .env 文件
    load_dotenv()
    
    # 读取 API key
    api_key = os.getenv("SUPER_MIND_API_KEY")
    
    if not api_key:
        print("\n❌ 错误: 在 .env 文件中找不到 SUPER_MIND_API_KEY")
        print("\n请确保 .env 文件包含：")
        print("SUPER_MIND_API_KEY=your_api_key_here")
        return False
    
    print(f"\n✅ 找到 API Key: {api_key[:20]}...")
    
    # 读取现有配置
    config_file = "deploy-config.json"
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"\n❌ 错误: {config_file} 文件不存在")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ 错误: JSON 解析失败: {e}")
        return False
    
    # 更新 env_vars
    if "env_vars" not in config:
        config["env_vars"] = {}
    
    config["env_vars"]["SUPER_MIND_API_KEY"] = api_key
    
    # 确保 SUPER_MIND_BASE_URL 也存在
    if "SUPER_MIND_BASE_URL" not in config["env_vars"]:
        config["env_vars"]["SUPER_MIND_BASE_URL"] = "https://space.ai-builders.com/backend/v1"
    
    # 保存配置
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 已更新 {config_file}")
        print(f"\n当前配置：")
        print(f"  服务名称: {config.get('service_name', 'N/A')}")
        print(f"  仓库 URL: {config.get('repo_url', 'N/A')}")
        print(f"  分支: {config.get('branch', 'N/A')}")
        print(f"  环境变量: {list(config.get('env_vars', {}).keys())}")
        
        print(f"\n⚠️  注意: {config_file} 在 .gitignore 中，不会被提交到 GitHub")
        print(f"   这是安全的，因为包含敏感信息")
        
        return True
    except Exception as e:
        print(f"\n❌ 错误: 保存配置失败: {e}")
        return False

if __name__ == "__main__":
    success = update_deploy_config()
    if success:
        print("\n" + "=" * 60)
        print("✅ 配置更新完成！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 重新部署: python deploy.py")
        print("2. 等待部署完成（5-10 分钟）")
        print("3. 测试应用")
    else:
        print("\n" + "=" * 60)
        print("❌ 配置更新失败")
        print("=" * 60)
