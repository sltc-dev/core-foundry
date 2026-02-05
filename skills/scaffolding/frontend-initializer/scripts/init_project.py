import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import json

REPO_URL = "git@github.com:shuluntc/shuluntc-frontend-templates.git"

def run_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Stderr: {e.stderr}")
        raise

def get_templates(base_dir):
    templates = []
    # Walk through directories to find package.json files which indicate a template root
    for root, dirs, files in os.walk(base_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        
        if "package.json" in files:
            # Calculate relative path from base_dir
            rel_path = os.path.relpath(root, base_dir)
            if rel_path != ".":
                # Read package.json for description
                pkg_path = os.path.join(root, "package.json")
                description = ""
                try:
                    with open(pkg_path, 'r') as f:
                        data = json.load(f)
                        description = data.get('description', '')
                except:
                    pass
                templates.append((rel_path, description))
    
    # Sort templates for consistent ordering
    if templates:
        templates.sort(key=lambda x: x[0])
        
    return templates

def list_templates():
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_command(["git", "clone", "--depth", "1", REPO_URL, temp_dir])
            
            templates = get_templates(temp_dir)
            
            if templates:
                for idx, (path, desc) in enumerate(templates, 1):
                    desc_str = f" ({desc})" if desc else ""
                    print(f"{idx}. {path}{desc_str}")
            else:
                print("No templates found in the repository.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def setup_project_files(template_path, target_dir, project_name):
    # Copy files
    shutil.copytree(template_path, target_dir)
    
    # Update package.json
    package_json_path = os.path.join(target_dir, "package.json")
    if os.path.exists(package_json_path):
        print(f"Updating package.json name to '{project_name}'...")
        with open(package_json_path, 'r') as f:
            data = json.load(f)
        
        data['name'] = project_name
        
        with open(package_json_path, 'w') as f:
            json.dump(data, f, indent=2)

def create_project(template_name, project_name):
    target_dir = os.path.join(os.getcwd(), project_name)
    
    if os.path.exists(target_dir):
        print(f"Error: Directory '{project_name}' already exists.")
        sys.exit(1)
        
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning {REPO_URL}...")
            run_command(["git", "clone", "--depth", "1", REPO_URL, temp_dir])
            
            template_path = os.path.join(temp_dir, template_name)
            if not os.path.exists(template_path):
                print(f"Error: Template '{template_name}' not found in repository.")
                sys.exit(1)
            
            # Verify it's a valid template (has package.json)
            if not os.path.exists(os.path.join(template_path, "package.json")):
                 print(f"Warning: Template '{template_name}' does not contain a package.json file.")

            print(f"Initializing project from '{template_name}' into '{target_dir}'...")
            setup_project_files(template_path, target_dir, project_name)
                    
            print(f"Successfully created project '{project_name}'.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir) # Cleanup on failure
        sys.exit(1)



def main():
    parser = argparse.ArgumentParser(description="Frontend Project Initializer")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    subparsers.add_parser("list", help="List available templates")
    
    create_parser = subparsers.add_parser("create", help="Initialize a project from a template")
    create_parser.add_argument("template_name", help="Name of the template to use (e.g., react/nextjs-tailwind)")
    create_parser.add_argument("project_name", help="Name of the new project (creates a directory)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_templates()
    elif args.command == "create":
        create_project(args.template_name, args.project_name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
