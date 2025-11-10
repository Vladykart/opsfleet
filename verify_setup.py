import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.11+)")
        return False


def check_file_exists(filepath, description):
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def check_env_variable(var_name):
    value = os.getenv(var_name)
    if value and value != f"your-{var_name.lower().replace('_', '-')}":
        print(f"✅ {var_name} is set")
        return True
    else:
        print(f"⚠️  {var_name} not configured")
        return False


def check_docker():
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    print("❌ Docker not found")
    return False


def check_weaviate():
    try:
        import requests
        response = requests.get("http://localhost:8080/v1/meta", timeout=2)
        if response.status_code == 200:
            print("✅ Weaviate is running")
            return True
    except Exception:
        pass
    print("⚠️  Weaviate not running (run: docker-compose up -d)")
    return False


def check_npm():
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    print("⚠️  npm not found (needed for Context7 MCP)")
    return False


def check_context7_mcp():
    try:
        result = subprocess.run(
            ["npx", "@upstash/context7-mcp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or "context7" in result.stderr.lower():
            print("✅ Context7 MCP installed")
            return True
    except Exception:
        pass
    print("⚠️  Context7 MCP not installed (run: npm install -g @upstash/context7-mcp)")
    return False


def main():
    print("\n" + "="*60)
    print("🔍 LangGraph Data Analysis Agent - Setup Verification")
    print("="*60 + "\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    checks = []
    
    print("📦 System Requirements:")
    checks.append(check_python_version())
    checks.append(check_docker())
    checks.append(check_npm())
    
    print("\n📁 Required Files:")
    checks.append(check_file_exists(".env", ".env file"))
    checks.append(check_file_exists("requirements.txt", "requirements.txt"))
    checks.append(check_file_exists("config/mcp_config.json", "MCP config"))
    checks.append(check_file_exists("config/agent_config.json", "Agent config"))
    checks.append(check_file_exists("docker-compose.yml", "Docker Compose"))
    
    print("\n🔑 Environment Variables:")
    checks.append(check_env_variable("GOOGLE_API_KEY"))
    checks.append(check_env_variable("CONTEXT7_API_KEY"))
    checks.append(check_env_variable("GCP_PROJECT_ID"))
    
    print("\n🛠️ MCP Servers:")
    checks.append(check_file_exists("toolbox", "BigQuery MCP (toolbox)"))
    checks.append(check_context7_mcp())
    
    print("\n🐳 Services:")
    checks.append(check_weaviate())
    
    print("\n" + "="*60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("\n🚀 Ready to run: python build_multi_agent_system.py")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n📋 Review the items above and fix any issues.")
        print("📖 See QUICKSTART.md or docs/guides/setup-guide.md for help")
    
    print("="*60 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
