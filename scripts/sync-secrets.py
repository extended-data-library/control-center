import os
import json
import subprocess
import sys
from typing import List, Dict

ORG = "extended-data-library"

# Secrets to propagate
REQUIRED_SECRETS = [
    "CURSOR_API_KEY",
    "GOOGLE_JULES_API_KEY",
    "CI_GITHUB_TOKEN",
    "CODECOV_TOKEN"
]

def run_command(cmd: List[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def get_repos():
    with open("repo-config.json", "r") as f:
        return json.load(f)["repositories"]

def sync_secrets(repo_name: str):
    print(f"🔐 Syncing secrets for {repo_name}...")
    for secret in REQUIRED_SECRETS:
        val = os.environ.get(secret)
        if not val:
            print(f"  ⚠️ Secret {secret} not found in environment, skipping.")
            continue
        
        try:
            # Check if secret exists
            # gh secret set doesn't have an easy "check" but we can just set it idempotently
            run_command(["gh", "secret", "set", secret, "--body", val, "--repo", f"{ORG}/{repo_name}"])
            print(f"  ✅ {secret} set.")
        except Exception as e:
            print(f"  ❌ Failed to set {secret}: {str(e)}")

def main():
    if not os.environ.get("GH_TOKEN"):
        print("GH_TOKEN environment variable is required.")
        sys.exit(1)

    repos = get_repos()
    for repo in repos:
        sync_secrets(repo["name"])

if __name__ == "__main__":
    main()
