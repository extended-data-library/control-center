import os
import json
import subprocess
from typing import List

ORG = "extended-data-library"

def run_command(cmd: List[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def main():
    print(f"📊 Ecosystem Health Check for {ORG}")
    print("=" * 40)
    
    with open("repo-config.json", "r") as f:
        repos = json.load(f)["repositories"]
    
    for repo in repos:
        name = repo["name"]
        print(f"\n🔍 {name}:")
        
        # Check CI Status
        runs = run_command(["gh", "run", "list", "--repo", f"{ORG}/{name}", "--limit", "1", "--json", "conclusion"])
        try:
            conclusion = json.loads(runs)[0]["conclusion"]
            ci_status = "✅ PASS" if conclusion == "success" else f"❌ {conclusion.upper()}"
        except:
            ci_status = "⚪ NO RUNS"
        print(f"  CI Status: {ci_status}")
        
        # Check Open PRs
        prs = run_command(["gh", "pr", "list", "--repo", f"{ORG}/{name}", "--json", "number"])
        pr_count = len(json.loads(prs))
        print(f"  Open PRs:  {pr_count}")
        
        # Check if always-sync files exist
        has_agents = "✅" if "AGENTS.md" in run_command(["gh", "api", f"repos/{ORG}/{name}/contents/"]) else "❌"
        print(f"  Managed:   {has_agents}")

if __name__ == "__main__":
    main()
