import os
import json
import subprocess
import pathlib
from typing import List, Dict

# Configuration
CONFIG_FILE = "repo-config.json"
ALWAYS_SYNC_DIR = "repository-files/always-sync"
INITIAL_ONLY_DIR = "repository-files/initial-only"
DOCS_DIR = "repository-files/docs"
ORG = "extended-data-library"

def run_command(cmd: List[str], input_str: str = None) -> str:
    result = subprocess.run(
        cmd,
        input=input_str,
        text=True,
        capture_output=True,
        check=True
    )
    return result.stdout.strip()

def get_repos() -> List[Dict]:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    return config["repositories"]

def file_exists(repo: str, path: str) -> bool:
    try:
        run_command(["gh", "api", f"repos/{ORG}/{repo}/contents/{path}"])
        return True
    except subprocess.CalledProcessError:
        return False

def update_file(repo: str, path: str, content: str, message: str):
    print(f"  Updating {path}...")
    # Use vendor-connectors if available, otherwise fallback to gh api
    try:
        subprocess.run([
            "vendor-connectors", "call", "github", "update_repository_file",
            "--repository", f"{ORG}/{repo}",
            "--file_path", path,
            "--file_data", content,
            "--msg", message
        ], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to direct gh api call
        # We need the SHA if the file exists
        sha = ""
        try:
            res = run_command(["gh", "api", f"repos/{ORG}/{repo}/contents/{path}"])
            sha = json.loads(res).get("sha", "")
        except:
            pass
        
        import base64
        encoded = base64.b64encode(content.encode()).decode()
        
        cmd = [
            "gh", "api", "--method", "PUT", f"repos/{ORG}/{repo}/contents/{path}",
            "-f", f"message={message}",
            "-f", f"content={encoded}"
        ]
        if sha:
            cmd.extend(["-f", f"sha={sha}"])
        
        run_command(cmd)

def main():
    repos = get_repos()
    
    for repo_config in repos:
        repo_name = repo_config["name"]
        repo_type = repo_config["type"]
        print(f"📦 Syncing {ORG}/{repo_name} ({repo_type})")
        
        # 1. Always Sync
        for root, _, files in os.walk(ALWAYS_SYNC_DIR):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, ALWAYS_SYNC_DIR)
                
                with open(src_path, "r") as f:
                    content = f.read()
                
                update_file(repo_name, rel_path, content, f"chore: sync {rel_path} from control-center")

        # 2. Initial Only
        for root, _, files in os.walk(INITIAL_ONLY_DIR):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, INITIAL_ONLY_DIR)
                
                if not file_exists(repo_name, rel_path):
                    with open(src_path, "r") as f:
                        content = f.read().replace("{{ REPO_NAME }}", repo_name)
                    update_file(repo_name, rel_path, content, f"chore: initial setup for {rel_path}")

        # 3. Specialized Sync for Docs Repo
        if repo_type == "docs":
            for root, _, files in os.walk(DOCS_DIR):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, DOCS_DIR)
                    
                    with open(src_path, "r") as f:
                        content = f.read()
                    
                    update_file(repo_name, rel_path, content, f"chore: sync specialized docs file {rel_path}")

if __name__ == "__main__":
    main()
