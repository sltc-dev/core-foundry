import sys
import os
import subprocess
import gh_helper

# Add the universal-code-reviewer scripts to path
current_dir = os.path.dirname(os.path.abspath(__file__))
universal_skill_dir = os.path.join(current_dir, "../../universal-code-reviewer")
universal_scripts_dir = os.path.join(universal_skill_dir, "scripts")
sys.path.append(universal_scripts_dir)

# Import rule_manager from universal-code-reviewer
try:
    import rule_manager
except ImportError:
    # If the import fails (e.g. structure is different), we'll try to execute it as a subprocess
    rule_manager = None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pr_worker.py <pr_id_or_url>")
        sys.exit(1)

    pr_id = sys.argv[1]
    
    # 1. Fetch PR Diff
    print(f"🔄 [Step 1] Fetching details for PR: {pr_id}...")
    try:
        details = gh_helper.get_pr_details(pr_id)
        print(f"   Title: {details.get('title')}")
        print(f"   URL: {details.get('url')}")
        
        diff_path = f"/tmp/pr_{details.get('number')}.diff"
        gh_helper.get_pr_diff(pr_id, diff_path)
        print(f"✅ Diff saved to: {diff_path}")
        
    except Exception as e:
        print(f"❌ Error fetching PR: {e}")
        sys.exit(1)

    # 2. Load Universal Code Reviewer Context
    # We need project name and root. 
    # Current assumption: We are running in the project root or we can deduce it.
    # The agent usually runs tools from the workspace root.
    project_root = os.getcwd()
    project_name = os.path.basename(project_root)
    
    print(f"\n🔄 [Step 2] Loading Review Rules for '{project_name}'...")
    
    # We try to use the imported module first, otherwise subprocess
    if rule_manager:
        try:
            # We call the check_ready function directly if possible, or simulate main
            rule_manager.check_ready(project_name, project_root)
        except Exception as e:
            print(f"❌ Error loading rules via module: {e}")
            # Fallback to subprocess
            run_rule_manager_subprocess(universal_scripts_dir, project_name, project_root)
    else:
        run_rule_manager_subprocess(universal_scripts_dir, project_name, project_root)

    print("\n" + "="*60)
    print("🤖 [INSTRUCTIONS FOR AI AGENT]")
    print(f"1. Read the diff file: view_file {diff_path}")
    print("2. Review the code strictly following the [STATUS: READY] rules above.")
    print("3. You MUST declare '[CR Skill 激活]' at the start of your response.")
    print("="*60)

def run_rule_manager_subprocess(scripts_dir, project_name, project_root):
    script_path = os.path.join(scripts_dir, "rule_manager.py")
    if not os.path.exists(script_path):
        print(f"❌ Critical Error: rule_manager.py not found at {script_path}")
        return
        
    cmd = [sys.executable, script_path, "ready", project_name, project_root]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
