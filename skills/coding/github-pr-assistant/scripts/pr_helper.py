import subprocess
import sys
import argparse
import os

def get_repo_root():
    """Returns the root directory of the current git repository."""
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT).decode('utf-8').strip()
        return root
    except subprocess.CalledProcessError:
        return None

def check_repo_safety():
    """Ensures the script is running in the expected repository (core-foundry)."""
    root = get_repo_root()
    if not root:
        print("Error: Not in a git repository.")
        sys.exit(1)
    
    # Check if the repository name is core-foundry
    repo_name = os.path.basename(root)
    if repo_name != 'core-foundry':
        print(f"Error: Operation not allowed in repository '{repo_name}'. This tool only operates on 'core-foundry'.")
        sys.exit(1)
    
    return root

def run_gh_command(cmd, success_msg):
    """Executes a gh command safely."""
    print(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if success_msg:
            print(success_msg)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        sys.exit(1)

def handle_create(args):
    """Creates a new PR."""
    cmd = ['gh', 'pr', 'create', '--title', args.title, '--body', args.body]
    if args.draft:
        cmd.append('--draft')
    if args.base:
        cmd.extend(['--base', args.base])
    if args.head:
        cmd.extend(['--head', args.head])
    run_gh_command(cmd, "PR created successfully!")

def handle_list(args):
    """Lists open PRs."""
    cmd = ['gh', 'pr', 'list']
    if args.limit:
        cmd.extend(['--limit', str(args.limit)])
    run_gh_command(cmd, None)

def handle_view(args):
    """Views a specific PR."""
    cmd = ['gh', 'pr', 'view', str(args.pr_id)]
    if args.web:
        cmd.append('--web')
    run_gh_command(cmd, None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub PR Helper for core-foundry repository.")
    subparsers = parser.add_subparsers(dest="command", help="PR command to run", required=True)

    # Create subcommand
    create_parser = subparsers.add_parser("create", help="Create a new PR")
    create_parser.add_argument("--title", required=True, help="Title of the PR")
    create_parser.add_argument("--body", required=True, help="Body/description of the PR")
    create_parser.add_argument("--draft", action="store_true", help="Create the PR as a draft")
    create_parser.add_argument("--base", help="Target branch")
    create_parser.add_argument("--head", help="Source branch")

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List PRs")
    list_parser.add_argument("--limit", type=int, default=30, help="Maximum number of PRs to list")

    # View subcommand
    view_parser = subparsers.add_parser("view", help="View a PR")
    view_parser.add_argument("pr_id", help="PR number or branch name")
    view_parser.add_argument("--web", action="store_true", help="Open in browser")

    args = parser.parse_args()
    
    # Safety Check
    check_repo_safety()
    
    if args.command == "create":
        handle_create(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "view":
        handle_view(args)
