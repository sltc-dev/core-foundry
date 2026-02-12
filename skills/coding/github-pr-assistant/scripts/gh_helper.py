import subprocess
import sys
import os
import re

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

def main():
    # Pass all arguments to the script directly to gh, but check for safety first
    args = sys.argv[1:]
    
    # 1. Identify where we are
    current_repo = get_current_repo_nwo()
    
    # 2. Identify where the user wants to go
    target_repo = extract_target_repo(args)
    
    # 3. Policy Check
    if target_repo:
        # Normalize comparison (ignore case, though Github repos are generally case-insensitive but case-preserving)
        # If we couldn't determine current repo, we block explicit -R usage to be safe, 
        # OR we could allow it if it looks like "owner/repo". 
        # Safer to block if we are unsure of "self".
        
        if not current_repo:
             print("Error: Could not determine current repository context (are you in a git repo?). \n"
                   "Operations with --repo/-R are blocked when context is unknown to prevent external repository modification.", file=sys.stderr)
             sys.exit(1)

        if target_repo.lower() != current_repo.lower():
            print(f"Error: Operation blocked. You are attempting to operate on '{target_repo}' but the current repository is '{current_repo}'.\n"
                  "This wrapper script restricts specific repository operations to the current repository only.", file=sys.stderr)
            sys.exit(1)

    # 4. Execution
    # If we are here, either no -R was passed (defaults to current), or -R matches current.
    # We pass the original arguments exactly as received.
    try:
        # We use subprocess.run to allow interaction (like input prompts) to flow through attached stdin/out
        # capture_output=False ensures stdout/stderr go to terminal
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
