#!/usr/bin/env python3
"""
共享工具模块：提供路径定位等核心函数，确保所有脚本行为一致。
"""
import os
import subprocess

def get_skill_root():
    """
    定位当前技能的根目录。
    无论是在 core-foundry 原始仓库，还是被同步到了项目的 .agent/skills/ 下，
    根目录始终是 scripts 文件夹的上一级。
    """
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_script_dir, ".."))

def get_core_foundry_root():
    """
    保留此函数以向下兼容，但优先基于 skill_root 推断。
    """
    skill_root = get_skill_root()
    # 如果在原始仓库中，skill_root 是 core-foundry/skills/coding/universal-code-reviewer
    # ../../../ 应该是 core-foundry 根目录
    prospective_root = os.path.abspath(os.path.join(skill_root, "../../.."))
    if os.path.basename(prospective_root) == "core-foundry":
        return prospective_root
    
    # 否则直接返回 skill_root 的上级作为回退（不建议再全局搜寻）
    return prospective_root

def get_rules_dir():
    """
    获取规则存放目录 (始终在当前技能根目录下)
    """
    return os.path.join(get_skill_root(), "rules")

def get_references_dir():
    """
    获取参考文档目录 (始终在当前技能根目录下)
    """
    return os.path.join(get_skill_root(), "references")

def print_header(title, char="=", width=60):
    """
    统一格式的打印头
    """
    print("\n" + char * width)
    print(f"{title}")
    print(char * width)

def print_line(char="-", width=40):
    """
    统一格式的分隔线
    """
    print(char * width)
