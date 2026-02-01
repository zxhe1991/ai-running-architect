"""
Deployment script for AI Running Architect to ai-builders.space
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BASE_URL = "https://space.ai-builders.com/backend"
API_KEY = os.getenv("SUPER_MIND_API_KEY") or os.getenv("AI_BUILDER_TOKEN")

if not API_KEY:
    print("[ERROR] SUPER_MIND_API_KEY or AI_BUILDER_TOKEN not found in .env file!")
    print("Please add your API key to .env file:")
    print("SUPER_MIND_API_KEY=your_api_key_here")
    exit(1)


def load_deploy_config():
    """Load deployment configuration from deploy-config.json"""
    try:
        with open("deploy-config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("[ERROR] deploy-config.json not found!")
        print("Please create deploy-config.json with your deployment configuration.")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in deploy-config.json: {e}")
        return None


def deploy_service(config):
    """Deploy service to ai-builders.space"""
    url = f"{BASE_URL}/v1/deployments"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare deployment request
    deploy_request = {
        "repo_url": config["repo_url"],
        "service_name": config["service_name"],
        "branch": config["branch"],
        "port": config.get("port", 8501),
    }
    
    # Add environment variables if provided
    if "env_vars" in config and config["env_vars"]:
        deploy_request["env_vars"] = config["env_vars"]
    
    print(f"\n[Deploying] {config['service_name']}...")
    print(f"   Repository: {config['repo_url']}")
    print(f"   Branch: {config['branch']}")
    print(f"   Port: {deploy_request['port']}")
    
    try:
        response = requests.post(url, json=deploy_request, headers=headers, timeout=120)
        
        if response.status_code == 202:
            data = response.json()
            print(f"\n[SUCCESS] Deployment queued successfully!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Service Name: {data.get('service_name', 'unknown')}")
            
            if data.get('public_url'):
                print(f"   Public URL: {data.get('public_url')}")
            
            if data.get('streaming_logs'):
                print(f"\n[LOGS] Initial Build Logs:")
                print("-" * 60)
                logs = data.get('streaming_logs', '')
        if logs:
            try:
                print(logs)
            except UnicodeEncodeError:
                # Handle encoding issues on Windows
                print(logs.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))
                print("-" * 60)
            
            print(f"\n[STATUS] Deployment Status:")
            print(f"   Provisioning typically takes 5-10 minutes.")
            print(f"   Check status with: GET /v1/deployments/{config['service_name']}")
            print(f"\n[NEXT STEPS]")
            for action in data.get('suggested_actions', []):
                print(f"   - {action}")
            
            return True
        else:
            print(f"\n[ERROR] Deployment failed!")
            print(f"   Status Code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Error connecting to deployment API: {e}")
        return False


def check_deployment_status(service_name):
    """Check the status of a deployment"""
    url = f"{BASE_URL}/v1/deployments/{service_name}"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\n[STATUS] Deployment Status for {service_name}:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Public URL: {data.get('public_url', 'Not available yet')}")
            print(f"   Last Deployed: {data.get('last_deployed_at', 'Never')}")
            return data
        else:
            print(f"[ERROR] Error checking status: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("AI Running Architect - Deployment Script")
    print("=" * 60)
    
    # Load configuration
    config = load_deploy_config()
    if not config:
        exit(1)
    
    # Validate configuration
    if config.get("repo_url") == "YOUR_GITHUB_REPO_URL_HERE":
        print("\n[ERROR] Please update deploy-config.json with your GitHub repository URL!")
        print("   Edit deploy-config.json and set 'repo_url' to your public GitHub repository.")
        exit(1)
    
    # Deploy
    success = deploy_service(config)
    
    if success:
        print("\n" + "=" * 60)
        print("Deployment initiated! Use the following command to check status:")
        print(f"python deploy.py --status {config['service_name']}")
        print("=" * 60)
