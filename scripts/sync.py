import os
import json
import subprocess
import pathlib
import base64
import sys
from typing import List, Dict, Optional

# Configuration
CONFIG_FILE = "repo-config.json"
ALWAYS_SYNC_DIR = "repository-files/always-sync"
INITIAL_ONLY_DIR = "repository-files/initial-only"
DOCS_DIR = "repository-files/docs"
ORG = "extended-data-library"

def log(msg: str):
    print(f"  {msg}")

def run_command(cmd: List[str], input_str: str = None) -> str:
    try:
        result = subprocess.run(
            cmd,
            input=input_str,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr}")
        raise

def get_repos() -> List[Dict]:
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file {CONFIG_FILE} not found.")
        return []
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    return config.get("repositories", [])

def get_remote_file_sha(repo: str, path: str) -> Optional[str]:
    try:
        res = run_command(["gh", "api", f"repos/{ORG}/{repo}/contents/{path}"])
        return json.loads(res).get("sha")
    except Exception:
        return None

def update_file(repo: str, path: str, content: str, message: str):
    sha = get_remote_file_sha(repo, path)
    
    # Check if content is actually different to save API calls
    if sha:
        try:
            remote_content_res = run_command(["gh", "api", f"repos/{ORG}/{repo}/contents/{path}"])
            remote_content_b64 = json.loads(remote_content_res).get("content", "").replace("\n", "")
            remote_content = base64.b64decode(remote_content_b64).decode('utf-8')
            if remote_content == content:
                # No change needed
                return
        except Exception:
            pass

    log(f"Updating {path}...")
    
    # Try using vendor-connectors if it's in the environment
    try:
        subprocess.run([
            "vendor-connectors", "call", "github", "update_repository_file",
            "--repository", f"{ORG}/{repo}",
            "--file_path", path,
            "--file_data", content,
            "--msg", message
        ], check=True, capture_output=True)
        log(f"✅ {path} (via vendor-connectors)")
    except Exception:
        # Fallback to gh api
        encoded = base64.b64encode(content.encode()).decode()
        cmd = [
            "gh", "api", "--method", "PUT", f"repos/{ORG}/{repo}/contents/{path}",
            "-f", f"message={message}",
            "-f", f"content={encoded}"
        ]
        if sha:
            cmd.extend(["-f", f"sha={sha}"])
        
        try:
            run_command(cmd)
            log(f"✅ {path} (via gh api)")
        except Exception as e:
            log(f"❌ Failed to update {path}: {str(e)}")

def delete_file(repo: str, path: str, message: str):
    sha = get_remote_file_sha(repo, path)
    if not sha:
        return

    log(f"Deleting {path} (no longer in always-sync)...")
    try:
        run_command([
            "gh", "api", "--method", "DELETE", f"repos/{ORG}/{repo}/contents/{path}",
            "-f", f"message={message}",
            "-f", f"sha={sha}"
        ])
        log(f"✅ Deleted {path}")
    except Exception as e:
        log(f"❌ Failed to delete {path}: {str(e)}")

def get_all_remote_files(repo: str, path: str = "") -> List[str]:
    files = []
    try:
        res = run_command(["gh", "api", f"repos/{ORG}/{repo}/contents/{path}"])
        items = json.loads(res)
        if not isinstance(items, list):
            return []
        for item in items:
            if item["type"] == "dir":
                files.extend(get_all_remote_files(repo, item["path"]))
            else:
                files.append(item["path"])
    except Exception:
        pass
    return files

def main():
    repos = get_repos()
    if not repos:
        print("No repositories found to sync.")
        return

    # Track files for deletion sync (only for .github/ and .cursor/ which we "own")
    managed_prefixes = [".github/", ".cursor/", "AGENTS.md", "CLAUDE.md"]
    
    always_sync_files = {}
    for root, _, files in os.walk(ALWAYS_SYNC_DIR):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, ALWAYS_SYNC_DIR)
            always_sync_files[rel_path] = src_path

    for repo_config in repos:
        repo_name = repo_config["name"]
        repo_type = repo_config["type"]
        print(f"\n📦 Syncing {ORG}/{repo_name} ({repo_type})")
        
        # 1. Always Sync
        for rel_path, src_path in always_sync_files.items():
            with open(src_path, "r") as f:
                content = f.read()
            update_file(repo_name, rel_path, content, f"chore: sync {rel_path} from control-center")

        # 2. Deletion Sync (Careful!)
        # Only delete files in managed directories that are NOT in always_sync_files
        remote_files = get_all_remote_files(repo_name)
        for remote_path in remote_files:
            if any(remote_path.startswith(p) for p in managed_prefixes):
                if remote_path not in always_sync_files:
                    # Special case: don't delete files that might be in initial-only or docs
                    # This is a bit simplistic but works for now
                    delete_file(repo_name, remote_path, f"chore: remove legacy file {remote_path}")

        # 3. Initial Only
        for root, _, files in os.walk(INITIAL_ONLY_DIR):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, INITIAL_ONLY_DIR)
                
                if not get_remote_file_sha(repo_name, rel_path):
                    with open(src_path, "r") as f:
                        content = f.read().replace("{{ REPO_NAME }}", repo_name)
                    update_file(repo_name, rel_path, content, f"chore: initial setup for {rel_path}")

        # 4. Specialized Sync for Docs Repo
        if repo_type == "docs":
            for root, _, files in os.walk(DOCS_DIR):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, DOCS_DIR)
                    with open(src_path, "r") as f:
                        content = f.read()
                    update_file(repo_name, rel_path, content, f"chore: sync specialized docs file {rel_path}")

    print("\n✨ Sync complete.")

if __name__ == "__main__":
    main()
