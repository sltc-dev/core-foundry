import argparse
import subprocess
import sys
import os
import re

def get_repo_root():
    """Returns the root directory of the current git repository."""
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT).decode('utf-8').strip()
        return root
    except subprocess.CalledProcessError:
        return None

def check_gh_installed():
    """Checks if gh CLI is installed."""
    try:
        subprocess.run(['gh', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def fetch_pr_diff(pr_id, output_path):
    """Fetches the PR diff using gh CLI."""
    print(f"Fetching diff for PR #{pr_id}...")
    try:
        # Check if pr_id is a URL, extract number if so
        match = re.search(r'/pull/(\d+)', pr_id)
        if match:
            pr_id = match.group(1)
        
        with open(output_path, 'w') as f:
            subprocess.run(['gh', 'pr', 'diff', pr_id], stdout=f, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error fetching PR diff: {e}")
        return False

def run_rule_manager(repo_root):
    """Runs the universal-code-reviewer rule manager."""
    print("\n--- Invoking Universal Code Reviewer Rule Manager ---")
    
    # Determine path to universal-code-reviewer based on current script location
    # This script is in .../skills/coding/auto-pr-reviewer/scripts/
    # We want .../skills/coding/universal-code-reviewer/scripts/rule_manager.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up two levels to 'skills/coding'
    coding_dir = os.path.abspath(os.path.join(current_dir, "../.."))
    
    rule_manager_path = os.path.join(coding_dir, "universal-code-reviewer/scripts/rule_manager.py")
    
    if not os.path.exists(rule_manager_path):
        # Fallback: try three levels up if 'coding' is not the parent of parent
        # This handles cases where structure might be skills/auto-pr-reviewer (if moved)
        # But for now, let's trust the current structure.
        print(f"Debug: coding_dir={coding_dir}")
        print(f"Error: Rule manager script not found at {rule_manager_path}")
        return False

    repo_name = os.path.basename(repo_root)
    
    cmd = [sys.executable, rule_manager_path, "ready", repo_name, repo_root]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        print("Error executing rule manager.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Auto PR Reviewer Workflow")
    parser.add_argument("pr_id", help="PR ID or URL")
    args = parser.parse_args()

    repo_root = get_repo_root()
    if not repo_root:
        print("Error: Not in a git repository.")
        sys.exit(1)

    if not check_gh_installed():
        print("Error: GitHub CLI (gh) is not installed or not in PATH.")
        sys.exit(1)

    diff_file = f"/tmp/pr_{os.path.basename(args.pr_id)}.diff"
    
    if fetch_pr_diff(args.pr_id, diff_file):
        print(f"\n✅ Diff saved to: {diff_file}")
        print(f"Action Required: Use 'view_file {diff_file}' to read the changes.")
    else:
        sys.exit(1)

    # Always run rule manager to provide context for the review
    if not run_rule_manager(repo_root):
        print("⚠️ Warning: Rule manager failed. Proceeding with default/generic review standards.")

if __name__ == "__main__":
    main()
