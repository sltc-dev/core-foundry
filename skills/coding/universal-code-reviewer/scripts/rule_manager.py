#!/usr/bin/env python3
"""
规则管理器：负责上下文准备 (Context Loading)。
"""
import os
import sys
import json
from shared import get_core_foundry_root, get_rules_dir, get_references_dir, get_skill_root, print_header, print_line

def check_ready(project_name, project_root):
    """
    一键加载 CR 所需的所有上下文，并明确输出状态。
    综合：项目特定规则 (Project Rules) + 全局参考 (Global References)
    """
    rules_dir = get_rules_dir()
    
    # 动态发现规则文件
    def find_rule_files(search_root):
        """
        在指定目录下启发式搜索规则文件
        关键词: rule, review, style, contributing, convention, standard
        """
        found = []
        keywords = ["rule", "review", "style", "contributing", "convention", "standard", "spec"]
        
        # 搜索范围：项目根目录 + docs 子目录
        search_dirs = [search_root, os.path.join(search_root, "docs")]
        
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            
            try:
                for filename in os.listdir(d):
                    # 忽略非 markdown 文件和隐藏文件 (除 .cursorrules 外)
                    name_lower = filename.lower()
                    if not (name_lower.endswith(".md") or name_lower == ".cursorrules"):
                        continue
                        
                    filepath = os.path.join(d, filename)
                    if os.path.isdir(filepath):
                        continue

                    # 匹配关键词
                    if any(kw in name_lower for kw in keywords):
                        found.append(filepath)
            except OSError:
                continue
                
        return sorted(list(set(found))) # 去重并排序

    project_rule_paths = find_rule_files(project_root)
    
    # 始终包含 Skill 本地的项目规则存储 (作为补充)
    local_skill_rule = os.path.join(rules_dir, f"{project_name}.md")
    if os.path.exists(local_skill_rule):
        project_rule_paths.append(local_skill_rule)

    print_header(f"🔥 CR CONTEXT BUNDLE: {project_name}")
    
    # ========== 阶段 1: 加载项目特定规则 (Project Rules) ==========
    # 项目规则优先级最高，我们会加载所有找到的满足条件的规则文件，但在输出上会明确标识
    print_header("PHASE 1: PROJECT SPECIFIC RULES", char="-")
    project_rules_found = False
    
    for rule_path in project_rule_paths:
        if os.path.exists(rule_path):
            print(f"\n✅ [FOUND] Project Rule: {rule_path}")
            try:
                with open(rule_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        print(content)
                        project_rules_found = True
                        print_line()
            except Exception as e:
                print(f"❌ Error reading {rule_path}: {e}")

    if not project_rules_found:
        print("\nℹ️ [INFO] No project-specific rules found in project root or skill rules directory.")

    # ========== 阶段 2: 注入全局参考文档 (Global References) ==========
    # 全局参考（如 code-quality.md）作为兜底标准
    print_header("PHASE 2: GLOBAL REFERENCES & BEST PRACTICES", char="-")
    refs_dir = get_references_dir()
    refs_loaded = 0
    
    if os.path.exists(refs_dir):
        for filename in sorted(os.listdir(refs_dir)):
            if filename.endswith(".md"):
                ref_path = os.path.join(refs_dir, filename)
                print(f"\n📖 [LOADING] Reference: {filename}")
                try:
                    with open(ref_path, 'r', encoding='utf-8') as f:
                        print(f.read())
                        refs_loaded += 1
                        print_line()
                except Exception as e:
                    print(f"❌ Error reading {filename}: {e}")

    # ========== 最终状态判定与指令指导 ==========
    print("\n" + "="*60)
    print("🚀 [STATUS: READY] CR Context Loaded Successfully.")
    print("💡 指导原则:")
    if project_rules_found:
        print("   1. [最高优先级 - OVERRIDES] 严格遵守 PHASE 1 中的项目特定规则。")
        print("   2. [基础标准 - BASE] 如果项目规则未覆盖，则遵循 PHASE 2 中的全局标准。")
    else:
        print("   1. [基础标准 - BASE] 依据 PHASE 2 中的全局质量标准进行代码审查。")
    
    print(f"✅ Loaded: {refs_loaded} Global References.")
    if project_rules_found:
        print(f"✅ Loaded: Project Rules found and loaded.")
    else:
        print(f"⚠️ Note: No Project Rules found.")
    print("="*60)
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3 and (len(sys.argv) < 2 or sys.argv[1] != "ready"):
         # Minimal check, actually the logic below handles arguments
         pass

    if len(sys.argv) < 2:
        print("Usage: rule_manager.py ready {project_name} {project_root}")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "ready":
        if len(sys.argv) < 4:
             print("Usage: rule_manager.py ready {project_name} {project_root}")
             sys.exit(1)
        exit_code = check_ready(sys.argv[2], sys.argv[3])
        sys.exit(exit_code)
    else:
        print(f"Unknown command: {action}")
        print("Available commands: ready")
        sys.exit(1)
