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


# --- Constants & Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SKILLS_SRC = os.path.join(REPO_ROOT, "skills")
PREF_FILE = os.path.expanduser("~/.config/core_foundry_prefs.json")


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


def detect_targets() -> Tuple[List[str], List[str]]:
    """Detects available IDE directories."""
    home = os.path.expanduser("~")
    check_list = [
        (
            "Antigravity",
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

    detected_names = []
    detected_paths = []

    print(f"{Colors.BLUE}{Icons.FIND} 正在扫描本地 IDE...{Colors.NC}")
    for name, path_dir, parent_dir in check_list:
        if os.path.isdir(parent_dir):
            detected_names.append(name)
            detected_paths.append(path_dir)
            print(f"{Colors.GREEN}  - 发现 {name}{Colors.NC}")

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
    alias_cmd = f"alias cf-sync='python3 {os.path.join(SCRIPT_DIR, 'sync_skills.py')}'"
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


def load_prefs() -> Prefs:
    prefs: Prefs
    try:
        with open(PREF_FILE, "r") as f:
            data = json.load(f)
            prefs = Prefs(**data)
    except Exception as e:
        if e is not FileNotFoundError:
            logging.warning(f"读取首选项失败，使用默认配置: {e}")
        prefs = Prefs()
    return prefs


def save_prefs(prefs: Prefs):
    try:
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
    print(f"{Colors.CYAN}==============================================={Colors.NC}")

    check_git_status()

    # Detect Targets
    targets, target_paths = detect_targets()
    if not targets:
        print(f"{Colors.RED}{Icons.WARN} 未检测到可用 IDE。{Colors.NC}")
        sys.exit(1)

    # Load prefs
    prefs = load_prefs()

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

    # Sync
    for idx in selected_ide_indexes:
        sync_now(
            target_paths[idx],
            targets[idx],
            selected_skill_indixes,
            skill_names,
            skill_paths,
        )

    # Save prefs
    save_prefs(Prefs(selected_ide_indexes, selected_skill_indixes))

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
