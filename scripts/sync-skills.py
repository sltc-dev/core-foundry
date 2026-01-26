#!/usr/bin/env python3

# =================================================================
# Core Foundry - Skills 终极同步工具
# 功能：
# 1. 自动检测环境 (Mac/Linux/WSL)
# 2. 物理复制模式同步技能到各 IDE
# 3. 自动安装 Shell 别名 (cf-sync)
# 4. 记忆用户偏好（IDE & Skill 选择）
# 5. Git 远程更新检查
# =================================================================

import glob
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import List, Tuple


# --- Colors & Icons ---
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"


class Icons:
    SYNC = "🔄"
    FIND = "🔍"
    LINK = "🔗"
    COPY = "📦"
    CLEAN = "🧹"
    OK = "✅"
    WARN = "⚠️"


@dataclass
class Prefs:
    lastIdeIndexes: List[int] = field(default_factory=list)
    lastSkillIndexes: List[int] = field(default_factory=list)
    cachedIdeTargets: List[List[str]] = field(default_factory=list)  # [[name, path], ...]
    cachedProjects: List[str] = field(default_factory=list)


# --- Constants & Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SKILLS_SRC = os.path.join(REPO_ROOT, "skills")
PREF_FILE = os.path.expanduser("~/.config/core_foundry_prefs.json")


def find_projects(search_roots: List[str], cached_projects: List[str] = None) -> Tuple[List[str], bool]:
    """
    Finds potential projects in multiple directory roots with caching.
    Scans up to 2 levels deep to catch nested project structures.
    Returns: (project_paths, is_from_cache)
    """
    # 1. Try Cache
    if cached_projects:
        valid_cache = []
        all_valid = True
        for p in cached_projects:
            real_path = os.path.realpath(p)
            if os.path.exists(real_path) and os.path.isdir(real_path):
                valid_cache.append(real_path)
            else:
                all_valid = False
        
        if valid_cache and all_valid:
            # Deduplicate
            valid_cache = sorted(list(set(valid_cache)))
            print(f"{Colors.GREEN}{Icons.OK} 使用缓存的项目列表 ({len(valid_cache)} 个){Colors.NC}")
            return valid_cache, True
        elif valid_cache:
             print(f"{Colors.YELLOW}{Icons.WARN} 缓存的项目路径部分无效，重新扫描...{Colors.NC}")
    
    # 2. Scan
    # 2. Scan
    projects = []
    seen = set()
    
    # 排除自身 (Core Foundry) - 避免把自己识别为目标项目
    seen.add(os.path.realpath(REPO_ROOT).lower())
    
    # Add cached projects to the set first (keep known valid ones)
    if cached_projects:
        for p in cached_projects:
            real_path = os.path.realpath(p)
            if os.path.exists(real_path) and os.path.isdir(real_path):
                lower_path = real_path.lower()
                if lower_path not in seen:
                    projects.append(real_path)
                    seen.add(lower_path)

    # Directories to skip
    skip_dirs = {"Library", "System", "Users", "Applications", "public", "private", 
                 "node_modules", ".git", "dist", "build", "__pycache__", "venv", ".venv"}
    
    # Project markers
    markers = [
        ".git", "package.json", "pom.xml", "build.gradle", 
        "requirements.txt", "go.mod", "Cargo.toml", 
        "vite.config.ts", "next.config.js", "pyproject.toml"
    ]

    def is_project(path: str) -> bool:
        """Check if a directory is a project."""
        for marker in markers:
            if os.path.exists(os.path.join(path, marker)):
                return True
        return False

    def scan_directory(base_dir: str, current_depth: int, max_depth: int):
        """Recursively scan directories up to max_depth."""
        if current_depth > max_depth:
            return
        
        if not os.path.exists(base_dir):
            return
            
        try:
            with os.scandir(base_dir) as entries:
                for entry in entries:
                    if not entry.is_dir() or entry.name.startswith('.'):
                        continue
                    if entry.name in skip_dirs:
                        continue

                    real_path = os.path.realpath(entry.path)
                    
                    if is_project(real_path):
                        lower_path = real_path.lower()
                        if lower_path not in seen:
                            projects.append(real_path)
                            seen.add(lower_path)
                    elif current_depth < max_depth:
                        # Not a project, but scan deeper
                        scan_directory(real_path, current_depth + 1, max_depth)
        except PermissionError:
            pass
        except Exception:
            pass

    # Deduplicate search_roots as well
    normalized_roots = []
    seen_roots = set()
    for root in search_roots:
        if not os.path.exists(root):
            continue
        real_root = os.path.realpath(root)
        lower_root = real_root.lower()
        if lower_root not in seen_roots:
            normalized_roots.append(real_root)
            seen_roots.add(lower_root)
            
    for base_dir in normalized_roots:
        print(f"{Colors.BLUE}{Icons.FIND} 正在扫描项目 (Base: {base_dir}, 深度: 2)...{Colors.NC}")
        scan_directory(base_dir, 1, 2)  # Scan up to 2 levels deep

    return sorted(list(projects)), False


def check_git_status():
    """Checks for remote updates."""
    print(f"{Colors.BLUE}{Icons.FIND} 检查远程更新...{Colors.NC}")
    try:
        # Fetch remote silently
        subprocess.run(
            ["git", "fetch", "--quiet", "origin", "main"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        local = (
            subprocess.check_output(["git", "rev-parse", "@"], cwd=REPO_ROOT)
            .strip()
            .decode("utf-8")
        )

        remote = (
            subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=REPO_ROOT)
            .strip()
            .decode("utf-8")
        )

        if local != remote and remote:
            print(
                f"{Colors.YELLOW}{Icons.WARN} 注意：云端有新的技能更新，建议同步前执行 'cd {REPO_ROOT} && git pull'{Colors.NC}"
            )
    except Exception:
        # Ignore git errors (e.g. not a git repo, no network)
        pass


def detect_targets(cached_targets: List[List[str]] = None) -> Tuple[List[str], List[str]]:
    """Detects available IDE directories with caching."""
    detected_names = []
    detected_paths = []

    # 1. Try Cache
    if cached_targets:
        valid = True
        temp_names = []
        temp_paths = []
        
        for item in cached_targets:
            if len(item) != 2:
                valid = False
                break
            name, path = item
            # Special case for virtual paths or verify file existence
            if path == "__PROJECT_SELECT__" or os.path.isdir(path):
                temp_names.append(name)
                temp_paths.append(path)
            else:
                valid = False
                break
        
        if valid and temp_names:
            print(f"{Colors.GREEN}{Icons.OK} 使用缓存的 IDE 列表{Colors.NC}")
            return temp_names, temp_paths
        else:
             print(f"{Colors.YELLOW}{Icons.WARN} 缓存的 IDE 路径无效，重新扫描...{Colors.NC}")

    # 2. Scan
    home = os.path.expanduser("~")
    check_list = [
        (
            "Antigravity Global (⚠️ 可能不生效 - 慎用)",
            os.path.join(home, ".gemini/antigravity/global_skills"),
            os.path.join(home, ".gemini/antigravity"),
        ),
        ("Cursor", os.path.join(home, ".cursor/skills"), os.path.join(home, ".cursor")),
        (
            "Trae (字节)",
            os.path.join(home, ".trae/skills"),
            os.path.join(home, ".trae"),
        ),
    ]

    print(f"{Colors.BLUE}{Icons.FIND} 正在扫描本地 IDE...{Colors.NC}")
    for name, path_dir, parent_dir in check_list:
        if os.path.isdir(parent_dir):
            detected_names.append(name)
            detected_paths.append(path_dir)
            print(f"{Colors.GREEN}  - 发现 {name}{Colors.NC}")

    # Explicitly add the Project-Level option
    detected_names.append("Antigravity Project (✅ 推荐 - 稳定生效)")
    detected_paths.append("__PROJECT_SELECT__")
    print(f"{Colors.GREEN}  - 启用 Antigravity 项目级同步模式 (推荐){Colors.NC}")

    return detected_names, detected_paths


def install_alias():
    """Installs 'cf-sync' alias to shell profiles."""
    home = os.path.expanduser("~")
    shell_rcs = [
        os.path.join(home, ".zshrc"),
        os.path.join(home, ".bashrc"),
        os.path.join(home, ".bash_profile"),
    ]
    # Use python script execution for the alias
    alias_cmd = f"alias cf-sync='python3 {os.path.join(SCRIPT_DIR, 'sync-skills.py')}'"
    installed = False

    for rc in shell_rcs:
        if os.path.isfile(rc):
            try:
                with open(rc, "r") as f:
                    content = f.read()

                if "alias cf-sync=" not in content:
                    with open(rc, "a") as f:
                        f.write("\n# Core Foundry Skills Sync Alias\n")
                        f.write(f"{alias_cmd}\n")
                    installed = True
                else:
                    # Update existing - simple replacement logic
                    lines = content.splitlines()
                    new_lines = []
                    for line in lines:
                        if line.strip().startswith("alias cf-sync="):
                            new_lines.append(alias_cmd)
                        else:
                            new_lines.append(line)

                    with open(rc, "w") as f:
                        f.write("\n".join(new_lines) + "\n")
            except Exception as e:
                pass  # Silently fail if permissions etc issue

    if installed:
        print(f"{Colors.PURPLE}{Icons.LINK} 已自动为您安装别名 'cf-sync'{Colors.NC}")
        print(
            f"{Colors.YELLOW}提示：由于当前进程限制，请手动执行 'source ~/.zshrc' (或对应的 RC 文件) 以使别名在当前窗口生效。{Colors.NC}"
        )


def get_repo_skills() -> Tuple[List[str], List[str], List[str]]:
    """Scans for available skills in the repo."""
    names = []
    paths = []
    descs = []

    if not os.path.isdir(SKILLS_SRC):
        return names, paths, descs

    # Iterate categories
    for category in sorted(glob.glob(os.path.join(SKILLS_SRC, "*"))):
        if os.path.isdir(category):
            # Iterate skills
            for skill_dir in sorted(glob.glob(os.path.join(category, "*"))):
                skill_md = os.path.join(skill_dir, "SKILL.md")
                if os.path.isdir(skill_dir) and os.path.isfile(skill_md):
                    s_name = os.path.basename(skill_dir)
                    s_desc = ""

                    try:
                        with open(skill_md, "r", encoding="utf-8") as f:
                            lines = f.readlines()

                        # 1. Try YAML frontmatter
                        for line in lines:
                            if line.lower().startswith("description:"):
                                s_desc = line.split(":", 1)[1].strip().strip("\"'")
                                break

                        # 2. Try > Description
                        if not s_desc:
                            for line in lines:
                                if re.match(r"^> (描述|Description)：?", line):
                                    s_desc = re.sub(
                                        r"^> (描述|Description)：?", "", line
                                    ).strip()
                                    break

                        # 3. First non-empty, non-header line
                        if not s_desc:
                            for line in lines:
                                line = line.strip()
                                if (
                                    line
                                    and not line.startswith("---")
                                    and not line.startswith("#")
                                ):
                                    s_desc = line
                                    break

                        if not s_desc:
                            s_desc = "点击 SKILL.md 查看详情"

                        # Truncate
                        if len(s_desc) > 45:
                            s_desc = s_desc[:45] + "..."

                    except Exception:
                        s_desc = "Error reading description"

                    names.append(s_name)
                    paths.append(skill_dir)
                    descs.append(s_desc)

    return names, paths, descs


def sync_now(
    target_path: str,
    target_name: str,
    selected_indices: List[int],
    all_names: List[str],
    all_paths: List[str],
):
    print(f"\n{Colors.BLUE}{Icons.SYNC} 同步至 {target_name} (copy 模式)...{Colors.NC}")
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    for idx in selected_indices:
        s_name = all_names[idx]
        s_path = all_paths[idx]
        dest = os.path.join(target_path, s_name)

        # Remove old
        if os.path.exists(dest):
            if os.path.islink(dest):
                os.unlink(dest)
            else:
                shutil.rmtree(dest)

        # Copy new
        try:
            shutil.copytree(s_path, dest)
            print(f"  {Colors.GREEN}[COPY]{Colors.NC} {s_name}")
        except Exception as e:
            print(f"  {Colors.RED}[ERROR]{Colors.NC} {s_name}: {e}")


def ensure_git_local_ignore(project_root: str, pattern: str):
    """
    Appends pattern to .git/info/exclude to ignore files locally 
    without changing the project's committed .gitignore.
    """
    git_dir = os.path.join(project_root, ".git")
    if not os.path.isdir(git_dir):
        return  # Not a git repo or no access

    exclude_file = os.path.join(git_dir, "info", "exclude")
    
    try:
        # Ensure info dir exists (it should, but just in case)
        os.makedirs(os.path.dirname(exclude_file), exist_ok=True)
        
        content = ""
        if os.path.exists(exclude_file):
            with open(exclude_file, "r", encoding="utf-8") as f:
                content = f.read()
        
        # Check if already ignored (simple check)
        # We look for the exact pattern or the pattern with a newline
        if pattern in content:
            return

        print(f"{Colors.PURPLE}{Icons.CLEAN} 正在配置项目本地 Git 忽略 (不影响 .gitignore): {pattern}{Colors.NC}")
        
        with open(exclude_file, "a", encoding="utf-8") as f:
            if content and not content.endswith("\n"):
                f.write("\n")
            f.write(f"# Auto-ignored by Core Foundry Skills Sync\n{pattern}\n")

    except Exception as e:
        # Non-critical error, just warn
        print(f"{Colors.YELLOW}{Icons.WARN} 无法自动配置 Git 忽略规则: {e}{Colors.NC}")


def load_prefs() -> Prefs:
    prefs: Prefs
    try:
        with open(PREF_FILE, "r") as f:
            data = json.load(f)
            prefs = Prefs(**data)
    except FileNotFoundError:
        # First run, no prefs file yet - this is normal
        prefs = Prefs()
    except Exception as e:
        logging.warning(f"读取首选项失败，使用默认配置: {e}")
        prefs = Prefs()
    return prefs


def save_prefs(prefs: Prefs):
    try:
        # Ensure config directory exists
        os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
        with open(PREF_FILE, "w") as f:
            json.dump(prefs.__dict__, f)
    except Exception as e:
        logging.warning(f"保存首选项失败: {e}")


def get_user_selection(
    options: List[str],
    descriptions: List[str] = None,
    prompt_title: str = "",
    last_selection: List[int] = None,
) -> List[int]:
    """Handles user selection menu."""
    selected = []

    # Check if we can reuse last selection
    if last_selection:
        # Validate indices
        valid_last = [i for i in last_selection if 0 <= i < len(options)]
        if valid_last:
            print(f"\n{Colors.BLUE}{prompt_title}: 检测到上次选择{Colors.NC}")
            for idx in valid_last:
                print(f"  - {options[idx]}")

            # Simple input handling
            choice = input(f"是否沿用上次选择？[Y/n]: ").strip().lower()
            if choice != "n":
                return valid_last

    print(
        f"\n{Colors.BLUE}{prompt_title} (支持多选，如: 1 2, 'a' 全部, 'q' 退出):{Colors.NC}"
    )
    for i, option in enumerate(options):
        if descriptions:
            print(
                f"  {i+1:2d}. {Colors.CYAN}{option:<25}{Colors.NC} | {descriptions[i]}"
            )
        else:
            print(f"  {i+1}. {option}")

    choice = input("选择: ").strip().lower()

    if choice == "q":
        sys.exit(0)
    elif choice == "a":
        return list(range(len(options)))
    else:
        parts = choice.replace(",", " ").split()
        for p in parts:
            if p.isdigit():
                val = int(p)
                if 1 <= val <= len(options):
                    selected.append(val - 1)

    return selected


def main():
    print(f"{Colors.CYAN}==============================================={Colors.NC}")
    print(f"{Colors.CYAN}      🚀 Core Foundry Skills Manager (Python)  {Colors.NC}")
    print(f"{Colors.CYAN}      (运行 'python3 scripts/sync-skills.py clean' 可强制清除缓存){Colors.NC}")
    print(f"{Colors.CYAN}==============================================={Colors.NC}")

    # Handle Cache Cleaning
    if len(sys.argv) > 1 and sys.argv[1] in ["clean", "clear", "--clean", "--clear", "--reset", "-c"]:
        if os.path.exists(PREF_FILE):
            try:
                os.remove(PREF_FILE)
                print(f"{Colors.GREEN}{Icons.CLEAN} 成功根据指令清除缓存文件: {PREF_FILE}{Colors.NC}")
            except Exception as e:
                print(f"{Colors.RED}无法清除缓存文件: {e}{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}{Icons.WARN} 缓存文件不存在 ({PREF_FILE})，无需清除。{Colors.NC}")
        sys.exit(0)

    # Load prefs first
    prefs = load_prefs()

    check_git_status()

    # Detect Targets (with cache)
    targets, target_paths = detect_targets(prefs.cachedIdeTargets)
    
    # Save IDE cache immediately
    prefs.cachedIdeTargets = list(zip(targets, target_paths))
    save_prefs(prefs)

    if not targets:
        print(f"{Colors.RED}{Icons.WARN} 未检测到可用 IDE。{Colors.NC}")
        sys.exit(1)

    # Select IDEs
    selected_ide_indexes = get_user_selection(
        targets, prompt_title="1. 请选择目标 IDEs", last_selection=prefs.lastIdeIndexes
    )
    if not selected_ide_indexes:
        sys.exit(0)

    # Get Skills
    skill_names, skill_paths, skill_descs = get_repo_skills()
    if not skill_names:
        print(f"{Colors.RED}{Icons.WARN} 未找到可用技能。{Colors.NC}")
        sys.exit(1)

    # Select Skills
    selected_skill_indixes = get_user_selection(
        skill_names,
        descriptions=skill_descs,
        prompt_title="2. 请选择要同步的 Skills",
        last_selection=prefs.lastSkillIndexes,
    )
    if not selected_skill_indixes:
        sys.exit(0)

    # Sync to selected targets
    for idx in selected_ide_indexes:
        t_path = target_paths[idx]
        t_name = targets[idx]

        # Handle Special Project Selection Mode
        if t_path == "__PROJECT_SELECT__":
            # 1. Find projects
            # Assuming projects are in the same parent folder as this repo (code folder)
            # REPO_ROOT is .../core-foundry. Parent is .../code
            code_root = os.path.dirname(REPO_ROOT)
            home_dir = os.path.expanduser("~")
            
            # Define search roots priority
            search_roots = [
                code_root,
                os.path.join(home_dir, "Desktop"),
                os.path.join(home_dir, "Documents"),
                os.path.join(home_dir, "Projects"),
                os.path.join(home_dir, "Code"),
                os.path.join(home_dir, "Dev"),
                os.path.join(home_dir, "Work"),
                # home_dir, # Scanning home is risky/slow, user better use Manual Add
            ]
            # Deduplicate inputs
            search_roots = sorted(list(set(search_roots)))

            # Project Selection Loop (to handle Rescan and Manual Add)
            while True:
                available_projects, is_from_cache = find_projects(search_roots, prefs.cachedProjects)
                
                # Save Project cache if freshly scanned
                if not is_from_cache:
                    prefs.cachedProjects = available_projects
                    save_prefs(prefs)
                
                # 2. Select projects
                proj_names = [os.path.basename(p) for p in available_projects]
                
                # Extended Menu Options
                display_options = proj_names.copy()
                
                # Add Rescan Option
                display_options.append(f"{Colors.YELLOW}🔄 重新扫描全盘热点目录 (Rescan){Colors.NC}")
                rescan_index = len(display_options) - 1

                # Add Manual input Option
                display_options.append(f"{Colors.GREEN}➕ 手动添加项目路径 (Manual Add){Colors.NC}")
                manual_add_index = len(display_options) - 1

                # Count of actual projects (excluding special options)
                actual_project_count = len(available_projects)
                
                selected_proj_indices = get_user_selection(
                    display_options,
                    prompt_title="1.1 [Antigravity] 请选择要注入的目标项目",
                )
                
                # If user selected 'all', trim to only actual projects
                if len(selected_proj_indices) == len(display_options):
                    selected_proj_indices = list(range(actual_project_count))
                
                # Handle Special Actions
                if manual_add_index in selected_proj_indices:
                     path_input = input(f"\n{Colors.BLUE}请输入项目绝对路径: {Colors.NC}").strip()
                     # Clean up quotes/spaces
                     path_input = path_input.strip("'\"")
                     
                     if os.path.isdir(path_input):
                         if path_input not in prefs.cachedProjects:
                             prefs.cachedProjects.append(path_input)
                             prefs.cachedProjects.sort()
                             save_prefs(prefs)
                             print(f"{Colors.GREEN}{Icons.OK} 已添加并缓存路径: {path_input}{Colors.NC}")
                         else:
                             print(f"{Colors.YELLOW}路径已存在于列表中。{Colors.NC}")
                     else:
                         print(f"{Colors.RED}{Icons.WARN} 无效的目录: {path_input}{Colors.NC}")
                     
                     # Loop again to refresh list
                     continue

                if rescan_index in selected_proj_indices:
                     # Force clear cache and loop again
                     prefs.cachedProjects = [] 
                     print(f"\n{Colors.BLUE}正在刷新项目列表...{Colors.NC}")
                     continue
                
                if not selected_proj_indices:
                    break
                
                # 3. Sync to each selected project
                nothing_synced = True
                for p_idx in selected_proj_indices:
                    if p_idx >= len(available_projects):
                        continue # Skip special options
                        
                    project_path = available_projects[p_idx]
                    project_name = proj_names[p_idx]
                    # Antigravity project skills path: <project>/.agent/skills
                    dest_path = os.path.join(project_path, ".agent", "skills")
                    
                    # Pre-flight: Ensure .agent/skills/ is ignored locally
                    ensure_git_local_ignore(project_path, ".agent/skills/")

                    sync_now(
                        dest_path,
                        f"Antigravity Project ({project_name})",
                        selected_skill_indixes,
                        skill_names,
                        skill_paths,
                    )
                    nothing_synced = False
                
                if not nothing_synced:
                    break # Break loop if sync happened
                else:
                    break # Break if nothing selected properly
        else:
            # Standard Sync
            sync_now(
                t_path,
                t_name,
                selected_skill_indixes,
                skill_names,
                skill_paths,
            )

    # Save final prefs (preserve cache, update selections)
    prefs.lastIdeIndexes = selected_ide_indexes
    prefs.lastSkillIndexes = selected_skill_indixes
    save_prefs(prefs)

    # Alias
    install_alias()

    print(f"\n{Colors.GREEN}{Icons.OK} 全部同步任务完成！{Colors.NC}")
    print(
        "提示：如果是首次安装别名，请重启终端或执行 source ~/.zshrc (或 ~/.bashrc) 生效。"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}操作已取消{Colors.NC}")
        sys.exit(1)
