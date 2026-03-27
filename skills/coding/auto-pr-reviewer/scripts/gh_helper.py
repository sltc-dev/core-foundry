import subprocess
import sys
import os
import re
import json

def get_current_repo_nwo():
    """
    Returns the 'owner/repo' string for the current repository using gh.
    """
    try:
        # Use gh to get the repository info for the current directory
        # This respects gh's logic for determining the current repo
        result = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'nameWithOwner', '-q', '.nameWithOwner'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If gh fails (e.g. not a git repo, or not logged in), we can't enforce restrictions reliably based on repo identity.
        # But if we aren't in a repo, gh won't work for repo-context commands anyway unless -R is passed.
        # Our goal is to prevent -R to *other* repos.
        return None

def extract_target_repo(args):
    """
    Scans arguments for -R or --repo flag and returns the specified repository.
    Handles: -R value, -Rvalue, --repo value, --repo=value
    """
    target = None
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        if arg == '-R' or arg == '--repo':
            if i + 1 < len(args):
                target = args[i + 1]
                skip_next = True
            # if no next arg, let gh handle the error
        elif arg.startswith('-R'):
            target = arg[2:]
        elif arg.startswith('--repo='):
            target = arg.split('=', 1)[1]
            
        if target:
            return target
            
    return None

def run_gh_command(args, capture_output=True, text=True):
    """
    Executes a gh command securely within the current repository context.
    Returns subprocess.CompletedProcess.
    """
    # 1. Identify where we are
    current_repo = get_current_repo_nwo()
    
    # 2. Identify where the user wants to go
    target_repo = extract_target_repo(args)
    
    # 3. Policy Check
    if target_repo:
        if not current_repo:
             raise RuntimeError("Error: Could not determine current repository context (are you in a git repo?). \n"
                   "Operations with --repo/-R are blocked when context is unknown to prevent external repository modification.")

        if target_repo.lower() != current_repo.lower():
            raise RuntimeError(f"Error: Operation blocked. You are attempting to operate on '{target_repo}' but the current repository is '{current_repo}'.\n"
                  "This wrapper script restricts specific repository operations to the current repository only.")

    # 4. Execution
    try:
        return subprocess.run(['gh'] + args, capture_output=capture_output, text=text, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gh command failed: {' '.join(args)}\nDraft:\n{e.stderr}")

def get_pr_details(pr_id_or_url):
    """
    Fetches PR details (title, body, etc.)
    """
    cmd = ['pr', 'view', str(pr_id_or_url), '--json', 'number,title,body,url,author,baseRefName,headRefName']
    result = run_gh_command(cmd)
    return json.loads(result.stdout)

def get_pr_diff(pr_id_or_url, output_path):
    """
    Fetches PR diff and saves to a file.
    """
    cmd = ['pr', 'diff', str(pr_id_or_url)]
    result = run_gh_command(cmd)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    
    return output_path

def main():
    # Pass all arguments to the script directly to gh, but check for safety first
    args = sys.argv[1:]
    
    try:
        # We use subprocess.run to allow interaction (like input prompts) to flow through attached stdin/out
        # capture_output=False ensures stdout/stderr go to terminal
        # simple wrapper usage: just call run_gh_command with capture_output=False
        
        # However, run_gh_command uses check=True and raises RuntimeError.
        # We want to mimic the original behavior of passing through exit codes.
        
        # 1. Reuse existing logic for safety check
        current_repo = get_current_repo_nwo()
        target_repo = extract_target_repo(args)
        
        if target_repo:
            if not current_repo:
                 print("Error: Could not determine current repository context (are you in a git repo?). \n"
                       "Operations with --repo/-R are blocked when context is unknown to prevent external repository modification.", file=sys.stderr)
                 sys.exit(1)
    
            if target_repo.lower() != current_repo.lower():
                print(f"Error: Operation blocked. You are attempting to operate on '{target_repo}' but the current repository is '{current_repo}'.\n"
                      "This wrapper script restricts specific repository operations to the current repository only.", file=sys.stderr)
                sys.exit(1)

        subprocess.run(['gh'] + args, check=True)
        
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: 'gh' command not found. Please ensure GitHub CLI is installed.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    main()
