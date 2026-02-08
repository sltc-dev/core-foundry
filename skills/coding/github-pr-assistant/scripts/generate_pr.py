#!/usr/bin/env python3
import subprocess
import urllib.parse
import sys
import re

def run_command(command):
    try:
        result = subprocess.run(
            command,
            cwd=None,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{' '.join(command)}': {e.stderr}", file=sys.stderr)
        return None

def get_current_branch():
    return run_command(["git", "branch", "--show-current"])

def get_remote_url():
    return run_command(["git", "remote", "get-url", "origin"])

def parse_remote_url(url):
    # Handles ssh: git@github.com:owner/repo.git
    # Handles https: https://github.com/owner/repo.git
    if not url:
        return None, None
    
    if url.startswith("git@"):
        match = re.search(r":(.+)/(.+)\.git$", url)
    else:
        match = re.search(r"github\.com/(.+)/(.+)\.git$", url)
        
    if match:
        return match.group(1), match.group(2)
    
    # Try without .git suffix
    if url.startswith("https://"):
         match = re.search(r"github\.com/(.+)/(.+)$", url)
         if match:
             return match.group(1), match.group(2)

    return None, None

def get_default_branch():
    # Try main, then master
    branches = run_command(["git", "branch", "-r"])
    if not branches:
        return "main" # Fallback
    
    if "origin/main" in branches:
        return "main"
    elif "origin/master" in branches:
        return "master"
    return "main"

def get_commits(base_branch, current_branch):
    # Get all commits between base and current
    log_output = run_command(["git", "log", f"origin/{base_branch}..{current_branch}", "--pretty=format:%s%n%b%n---COMMIT_DELIMITER---"])
    if not log_output:
        return []
    
    commits = log_output.split("---COMMIT_DELIMITER---")
    return [c.strip() for c in commits if c.strip()]

import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate GitHub PR URL")
    parser.add_argument("--title", help="PR Title")
    parser.add_argument("--body", help="PR Description/Body")
    args = parser.parse_args()

    current_branch = get_current_branch()
    if not current_branch:
        print("Could not determine current branch. Are you in a git repository?", file=sys.stderr)
        sys.exit(1)

    remote_url = get_remote_url()
    owner, repo = parse_remote_url(remote_url)
    
    if not owner or not repo:
        print(f"Could not parse owner/repo from remote URL: {remote_url}", file=sys.stderr)
        sys.exit(1)

    base_branch = get_default_branch()
    
    # Default to commit history if no arguments provided
    commits = get_commits(base_branch, current_branch)
    
    title = args.title
    body = args.body
    
    if not title and commits:
        # Use the first commit as title
        first_commit_lines = commits[0].split('\n')
        title = first_commit_lines[0]
        
    if not body and commits:
        # Use all commits for body, formatted as a list
        body = "## Summary\n\n"
        body += "<!-- Automatically generated from commit history -->\n"
        for commit in commits:
            lines = commit.split('\n')
            body += f"- {lines[0]}\n"
            
        body += "\n## Changes\n"
        body += "\n## Testing\n"
        body += "- [ ] Tested locally\n"

    # Encode for URL
    params = {
        "expand": "1"
    }
    if title:
        params["title"] = title
    if body:
        params["body"] = body
        
    query_string = urllib.parse.urlencode(params)
    
    pr_url = f"https://github.com/{owner}/{repo}/compare/{base_branch}...{current_branch}?{query_string}"
    
    print(f"Generated PR URL:\n{pr_url}")

if __name__ == "__main__":
    main()
