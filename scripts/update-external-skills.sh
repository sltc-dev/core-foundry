#!/bin/bash
# =============================================================================
# Core Foundry - 外部 Skills 更新脚本
# 
# 从 GitHub 上游仓库拉取最新的外部 Skills 并同步到本仓库。
#
# 用法:
#   ./scripts/update-external-skills.sh [skill_name]
#
# 示例:
#   ./scripts/update-external-skills.sh              # 更新所有外部 skills
#   ./scripts/update-external-skills.sh vue           # 只更新 vue-best-practices
#   ./scripts/update-external-skills.sh react         # 只更新 vercel-react-best-practices
#   ./scripts/update-external-skills.sh ui            # 只更新 ui-ux-pro-max
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$PROJECT_ROOT/skills/coding"

# 临时目录
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# =============================================================================
# 外部 Skills 配置
# 格式: REPO_URL | 仓库子目录路径 | 本地目标目录名 | 额外说明
# =============================================================================

declare -A SKILLS
SKILLS[react]="vercel-labs/agent-skills|skills/react-best-practices|vercel-react-best-practices"
SKILLS[vue]="vuejs-ai/skills|skills/vue-best-practices|vue-best-practices"
SKILLS[ui]="nextlevelbuilder/ui-ux-pro-max-skill|src/ui-ux-pro-max|ui-ux-pro-max"

# =============================================================================
# 函数定义
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  🔄 Core Foundry - 外部 Skills 更新器${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

update_skill() {
    local key=$1
    local config=${SKILLS[$key]}
    
    IFS='|' read -r repo subdir local_dir <<< "$config"
    
    local target_dir="$SKILLS_DIR/$local_dir"
    
    echo -e "${YELLOW}📦 正在更新: ${local_dir}${NC}"
    echo -e "   来源: https://github.com/${repo}"
    echo -e "   路径: ${subdir}"
    
    # Clone 仓库 (shallow)
    local clone_dir="$TMP_DIR/$key"
    echo -e "   📡 正在拉取最新版本..."
    if ! git clone --depth 1 "https://github.com/${repo}.git" "$clone_dir" 2>/dev/null; then
        echo -e "   ${RED}❌ 拉取失败! 请检查网络连接或仓库地址${NC}"
        return 1
    fi
    
    local source_dir="$clone_dir/$subdir"
    
    if [ ! -d "$source_dir" ]; then
        echo -e "   ${RED}❌ 源目录不存在: ${subdir}${NC}"
        return 1
    fi
    
    # 特殊处理: ui-ux-pro-max 不删除 SKILL.md（因为我们维护自己的版本）
    if [ "$key" = "ui" ]; then
        echo -e "   🔄 同步数据文件和脚本..."
        
        # 同步 scripts
        if [ -d "$source_dir/scripts" ]; then
            rsync -a --delete --exclude='.DS_Store' --exclude='__pycache__' \
                "$source_dir/scripts/" "$target_dir/scripts/"
        fi
        
        # 同步 data
        if [ -d "$source_dir/data" ]; then
            rsync -a --delete --exclude='.DS_Store' \
                "$source_dir/data/" "$target_dir/data/"
        fi
        
        # 同步 templates
        if [ -d "$source_dir/templates" ]; then
            rsync -a --delete --exclude='.DS_Store' \
                "$source_dir/templates/" "$target_dir/templates/"
        fi
    else
        # 直接全量同步
        echo -e "   🔄 同步文件..."
        rsync -a --delete --exclude='.DS_Store' --exclude='__pycache__' \
            "$source_dir/" "$target_dir/"
    fi
    
    # 获取远程版本信息
    local remote_commit=$(cd "$clone_dir" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    local remote_date=$(cd "$clone_dir" && git log -1 --format="%ci" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
    
    echo -e "   ${GREEN}✅ 更新完成${NC} (commit: ${remote_commit}, date: ${remote_date})"
    echo ""
}

# =============================================================================
# 主程序
# =============================================================================

print_header

FILTER="${1:-all}"

updated=0
failed=0

if [ "$FILTER" = "all" ]; then
    for key in react vue ui; do
        if update_skill "$key"; then
            ((updated++))
        else
            ((failed++))
        fi
    done
else
    if [ -n "${SKILLS[$FILTER]}" ]; then
        if update_skill "$FILTER"; then
            ((updated++))
        else
            ((failed++))
        fi
    else
        echo -e "${RED}❌ 未知的 skill: ${FILTER}${NC}"
        echo "可用选项: react, vue, ui, all"
        exit 1
    fi
fi

# 打印总结
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ 更新完成: ${updated} 个 skill${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}  ❌ 更新失败: ${failed} 个 skill${NC}"
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 显示 Git 变更
echo ""
echo -e "${YELLOW}📋 Git 变更摘要:${NC}"
cd "$PROJECT_ROOT"
git diff --stat -- skills/coding/ 2>/dev/null || true
echo ""

# 提示仍需 git add / commit
untracked=$(git ls-files --others --exclude-standard -- skills/coding/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$untracked" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 ${untracked} 个新文件，请检查后执行:${NC}"
    echo "   git add skills/coding/"
    echo "   git commit -m 'chore: update external skills to latest version'"
fi
