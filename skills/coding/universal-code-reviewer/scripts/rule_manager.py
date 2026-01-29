#!/usr/bin/env python3
"""
规则管理器：负责上下文准备 (Context Loading)。
支持智能检测项目类型（Vue/React/Node等）并加载对应的最佳实践规则。
"""
import os
import sys
import json
from shared import get_core_foundry_root, get_rules_dir, get_references_dir, get_skill_root, print_header, print_line


# ========== 项目类型检测 ==========

def detect_project_type(project_root):
    """
    检测项目类型，返回需要加载的额外参考文档列表。
    支持: vue, react, node, python 等
    """
    detected_types = []
    
    # 检查 package.json
    package_json_path = os.path.join(project_root, "package.json")
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                deps = {}
                deps.update(package_data.get("dependencies", {}))
                deps.update(package_data.get("devDependencies", {}))
                
                # Vue 项目检测
                if any(key.startswith("vue") or key == "@vue/cli-service" or key == "nuxt" for key in deps):
                    detected_types.append("vue")
                
                # React 项目检测
                if any(key in ["react", "react-dom", "next", "@remix-run/react"] for key in deps):
                    detected_types.append("react")
                    
        except (json.JSONDecodeError, IOError):
            pass
    
    # 检查 Vue 相关配置文件
    vue_indicators = ["vite.config.ts", "vite.config.js", "nuxt.config.ts", "nuxt.config.js", "vue.config.js"]
    for indicator in vue_indicators:
        if os.path.exists(os.path.join(project_root, indicator)):
            if "vue" not in detected_types:
                # 需要进一步检查是否真的是 Vue 项目
                config_path = os.path.join(project_root, indicator)
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "vue" in content.lower() or indicator.startswith("nuxt") or indicator.startswith("vue"):
                            detected_types.append("vue")
                            break
                except IOError:
                    pass
    
    # 检查 .vue 文件
    if "vue" not in detected_types:
        src_dir = os.path.join(project_root, "src")
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                if any(f.endswith(".vue") for f in files):
                    detected_types.append("vue")
                    break
                # 只检查前两层
                if root.count(os.sep) - src_dir.count(os.sep) >= 2:
                    break
    
    return list(set(detected_types))


def get_sibling_skill_path(skill_name):
    """
    获取同级 skill 的路径。
    skills/coding/universal-code-reviewer -> skills/coding/{skill_name}
    """
    skill_root = get_skill_root()
    parent_dir = os.path.dirname(skill_root)
    return os.path.join(parent_dir, skill_name)


def load_external_skill_rules(skill_name, rules_subdir="rules"):
    """
    从外部 skill 加载规则文件。
    返回: [(filename, filepath), ...]
    """
    skill_path = get_sibling_skill_path(skill_name)
    rules_path = os.path.join(skill_path, rules_subdir)
    
    if not os.path.exists(rules_path):
        return []
    
    rules = []
    for filename in sorted(os.listdir(rules_path)):
        if filename.endswith(".md"):
            rules.append((filename, os.path.join(rules_path, filename)))
    
    return rules


TYPE_TO_SKILL_MAP = {
    "vue": "vue-best-practices",
    "react": "vercel-react-best-practices",
}

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

    # ========== 阶段 2: 检测项目类型 ==========
    print_header("PHASE 2: PROJECT TYPE DETECTION", char="-")
    detected_types = detect_project_type(project_root)
    
    if detected_types:
        print(f"🔍 [DETECTED] Project types: {', '.join(detected_types)}")
        for ptype in detected_types:
            if ptype in TYPE_TO_SKILL_MAP:
                print(f"📚 [WILL LOAD] External skill: {TYPE_TO_SKILL_MAP[ptype]}")
    else:
        print("ℹ️ [INFO] No specific project type detected. Using general code quality rules.")
    
    # ========== 阶段 3: 加载外部 Skill 规则 ==========
    type_refs_loaded = 0
    for ptype in detected_types:
        skill_name = TYPE_TO_SKILL_MAP.get(ptype)
        if not skill_name:
            continue
            
        external_rules = load_external_skill_rules(skill_name)
        if external_rules:
            print_header(f"PHASE 3a: {skill_name.upper()} RULES", char="-")
            for filename, filepath in external_rules:
                print(f"\n🎯 [LOADING] {skill_name}/{filename}")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        print(f.read())
                        type_refs_loaded += 1
                        print_line()
                except Exception as e:
                    print(f"❌ Error reading {filepath}: {e}")
    
    # ========== 阶段 3b: 注入全局参考文档 (Global References) ==========
    print_header("PHASE 3b: GLOBAL REFERENCES & BEST PRACTICES", char="-")
    refs_dir = get_references_dir()
    refs_loaded = 0
    
    # 加载通用参考文档
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
        print("   2. [类型规则 - TYPE] 遵循 PHASE 3 中项目类型特定的最佳实践。")
        print("   3. [基础标准 - BASE] 如果项目规则未覆盖，则遵循通用标准。")
    elif detected_types:
        print("   1. [类型规则 - TYPE] 严格遵守项目类型特定的最佳实践（如 Vue Best Practices）。")
        print("   2. [基础标准 - BASE] 遵循通用代码质量标准。")
    else:
        print("   1. [基础标准 - BASE] 依据 PHASE 3 中的全局质量标准进行代码审查。")
    
    print(f"✅ Loaded: {refs_loaded} Global References.")
    if type_refs_loaded > 0:
        print(f"✅ Loaded: {type_refs_loaded} Type-Specific References ({', '.join(detected_types)}).")
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
