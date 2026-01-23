#!/bin/bash

# =================================================================
# Core Foundry - Skills 同步脚本
# 作用：将仓库内的 skills 软链接到各大 AI 助手工具的全局技能目录
# =================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}开始同步 Core Foundry Skills...${NC}"

# 获取仓库根目录
REPO_ROOT=$(pwd)
SKILLS_DIR="$REPO_ROOT/skills"

# --- 目标目录定义 ---
# 1. Antigravity 全局技能目录
ANTIGRAVITY_GLOBAL_DIR="$HOME/.gemini/antigravity/global_skills"

# TODO: 根据需要添加其他工具的目标目录
# CURSOR_GLOBAL_DIR="$HOME/Library/Application Support/Cursor/..." 
# VSCODE_GLOBAL_DIR="$HOME/.vscode/..."

# --- 函数：同步到指定目标 ---
sync_to_target() {
    local target_base=$1
    local target_name=$2

    if [ ! -d "$target_base" ]; then
        echo -e "${RED}跳过 $target_name: 目标目录不存在 ($target_base)${NC}"
        return
    fi

    echo -e "${BLUE}同步到 $target_name...${NC}"

    # 遍历 skills 目录下的所有分类
    for category in "$SKILLS_DIR"/*; do
        if [ -d "$category" ]; then
            # 遍历分类下的每个技能
            for skill in "$category"/*; do
                if [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]; then
                    skill_name=$(basename "$skill")
                    target_path="$target_base/$skill_name"

                    # 处理已存在的情况
                    if [ -L "$target_path" ]; then
                        rm "$target_path" # 如果之前是软链接，先删掉
                    elif [ -d "$target_path" ]; then
                        # 如果是目录，我们进行增量更新或提示
                        echo -e "${BLUE}  [Update] 更新已有技能: $skill_name${NC}"
                        rm -rf "$target_path"
                    fi

                    # 执行物理复制
                    cp -R "$skill" "$target_path"
                    echo -e "${GREEN}  [OK] 已复制: $skill_name${NC}"
                fi
            done
        fi
    done
}

# --- 执行同步 ---
sync_to_target "$ANTIGRAVITY_GLOBAL_DIR" "Antigravity"

# 如果未来有其他工具，也可以在这里调用
# sync_to_target "$CURSOR_GLOBAL_DIR" "Cursor"

echo -e "${BLUE}同步完成！${NC}"
echo -e "提示：如果你在仓库中添加了新技能，请重新运行此脚本。"
