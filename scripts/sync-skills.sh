#!/bin/bash

# =================================================================
# Core Foundry - Skills 终极同步工具
# 功能：
# 1. 自动检测环境 (Mac/Linux/WSL)
# 2. 支持 开发模式(软链接) 和 部署模式(复制)
# 3. 自动安装 Shell 别名 (cf-sync)
# 4. 自动清理过期技能 (Prune)
# 5. Git 远程检查
# =================================================================

# --- 颜色与图标 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

ICON_SYNC="🔄"
ICON_FIND="🔍"
ICON_LINK="🔗"
ICON_COPY="📦"
ICON_CLEAN="🧹"
ICON_OK="✅"
ICON_WARN="⚠️"

# --- 基础路径获取 ---
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SKILLS_SRC="$REPO_ROOT/skills"
HOOKS_DIR="$REPO_ROOT/.githooks"

echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN}      🚀 Core Foundry Skills Manager           ${NC}"
echo -e "${CYAN}===============================================${NC}"

# --- 1. Git 状态快速检查 ---
check_git_status() {
    echo -e "${BLUE}$ICON_FIND 检查远程更新...${NC}"
    # 异步获取更新，不阻塞
    git fetch --quiet origin main 2>/dev/null &
    
    LOCAL=$(git rev-parse @ 2>/dev/null)
    REMOTE=$(git rev-parse @{u} 2>/dev/null)
    
    if [ "$LOCAL" != "$REMOTE" ] && [ ! -z "$REMOTE" ]; then
        echo -e "${YELLOW}$ICON_WARN 注意：云端有新的技能更新，建议同步前执行 'git pull'${NC}"
    fi
}

# --- 2. 目标环境检测 (跨平台) ---
detect_targets() {
    local mac_app_support="$HOME/Library/Application Support"
    local linux_config="$HOME/.config"
    
    # 待检测列表: "名称|目标子目录|检测目录"
    local check_list=(
        "Antigravity|$HOME/.gemini/antigravity/global_skills|$HOME/.gemini/antigravity"
        "Cursor|$mac_app_support/Cursor/User/global_skills|$mac_app_support/Cursor/User"
        "Trae (字节)|$mac_app_support/Trae/User/global_skills|$mac_app_support/Trae/User"
        "MarsCode (豆包)|$mac_app_support/MarsCode/User/global_skills|$mac_app_support/MarsCode/User"
        "Windsurf|$mac_app_support/Windsurf/User/global_skills|$mac_app_support/Windsurf/User"
        "VS Code|$mac_app_support/Code/User/global_skills|$mac_app_support/Code/User"
        "Windsurf (Linux)|$linux_config/Windsurf/User/global_skills|$linux_config/Windsurf/User"
    )

    DETECTED_NAMES=()
    DETECTED_PATHS=()

    echo -e "${BLUE}$ICON_FIND 正在扫描本地 IDE...${NC}"
    for item in "${check_list[@]}"; do
        IFS="|" read -r name path parent <<< "$item"
        if [ -d "$parent" ]; then
            DETECTED_NAMES+=("$name")
            DETECTED_PATHS+=("$path")
            echo -e "${GREEN}  - 发现 $name${NC}"
        fi
    done
}

# --- 3. 别名安装逻辑 ---
install_alias() {
    local shell_rc=""
    if [[ "$SHELL" == */zsh ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ "$SHELL" == */bash ]]; then
        shell_rc="$HOME/.bashrc"
    fi

    if [ ! -z "$shell_rc" ] && [ -f "$shell_rc" ]; then
        if ! grep -q "alias cf-sync=" "$shell_rc"; then
            echo -e "\n${PURPLE}$ICON_LINK 是否安装命令别名 'cf-sync'？ (以后在任何地方输入 cf-sync 即可同步)${NC}"
            read -p "[y/n]: " install_confirm
            if [[ "$install_confirm" == "y" ]]; then
                echo "alias cf-sync='bash $REPO_ROOT/scripts/sync-skills.sh'" >> "$shell_rc"
                echo -e "${GREEN}$ICON_OK 已添加别名到 $shell_rc，请执行 'source $shell_rc' 生效。${NC}"
            fi
        fi
    fi
}

# --- 4. 同步核心逻辑 ---
sync_now() {
    local target_path="$1"
    local target_name="$2"
    local mode="$3" # link or copy

    echo -e "\n${BLUE}$ICON_SYNC 同步至 $target_name ($mode 模式)...${NC}"
    mkdir -p "$target_path"

    # 获取当前仓库所有技能列表 (用于清理)
    local repo_skills=()
    
    for category in "$SKILLS_SRC"/*; do
        if [ -d "$category" ]; then
            # 特殊处理：只处理包含子目录的分类
            for skill_dir in "$category"/*; do
                if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
                    local s_name=$(basename "$skill_dir")
                    repo_skills+=("$s_name")
                    local dest="$target_path/$s_name"

                    # 删除旧的 (不论是软链还是文件)
                    rm -rf "$dest"

                    if [ "$mode" == "link" ]; then
                        ln -s "$skill_dir" "$dest"
                        echo -e "  ${CYAN}[LINK]${NC} $s_name"
                    else
                        cp -R "$skill_dir" "$dest"
                        echo -e "  ${GREEN}[COPY]${NC} $s_name"
                    fi
                fi
            done
        fi
    done

    # --- 反向清理 (Prune) ---
    echo -e "${YELLOW}$ICON_CLEAN 正在检查过期技能...${NC}"
    for existing in "$target_path"/*; do
        if [ -e "$existing" ] || [ -L "$existing" ]; then
            local e_name=$(basename "$existing")
            local found=false
            for r_name in "${repo_skills[@]}"; do
                if [ "$e_name" == "$r_name" ]; then
                    found=true
                    break
                fi
            done
            if [ "$found" == "false" ]; then
                echo -e "  ${RED}[PRUNE]${NC} 移除不再维护的技能: $e_name"
                rm -rf "$existing"
            fi
        fi
    done
}

# --- 执行流程 ---
check_git_status
detect_targets

if [ ${#DETECTED_NAMES[@]} -eq 0 ]; then
    echo -e "${RED}$ICON_WARN 未检测到可用 IDE。${NC}"
    exit 1
fi

echo -e "\n${BLUE}请选择目标编号 (如: 1 2) 或 'a' 全部, 'q' 退出:${NC}"
for i in "${!DETECTED_NAMES[@]}"; do
    echo -e "  $((i+1)). ${DETECTED_NAMES[$i]}"
done
read -p "选择: " choice

SELECTED_INDICES=()
if [[ "$choice" == "a" ]]; then
    for i in "${!DETECTED_NAMES[@]}"; do SELECTED_INDICES+=($i); done
elif [[ "$choice" == "q" ]]; then exit 0
else
    for c in $choice; do
        if [[ "$c" =~ ^[0-9]+$ ]] && [ "$c" -ge 1 ] && [ "$c" -le ${#DETECTED_NAMES[@]} ]; then
            SELECTED_INDICES+=($((c-1)))
        fi
    done
fi

if [ ${#SELECTED_INDICES[@]} -eq 0 ]; then exit 0; fi

echo -e "\n${BLUE}选择同步模式:${NC}"
echo -e "  1. ${CYAN}开发模式 (软链接)${NC} - 仓库修改实时生效，推荐本地开发"
echo -e "  2. ${GREEN}部署模式 (物理复制)${NC} - 独立副本，不受仓库变动影响"
read -p "模式编号 [1/2, 默认1]: " mode_choice
SYNC_MODE="link"
[ "$mode_choice" == "2" ] && SYNC_MODE="copy"

for idx in "${SELECTED_INDICES[@]}"; do
    sync_now "${DETECTED_PATHS[$idx]}" "${DETECTED_NAMES[$idx]}" "$SYNC_MODE"
done

# 自动安装别名
install_alias

echo -e "\n${GREEN}$ICON_OK 全部同步任务完成！${NC}"
echo -e "提示：如果是首次安装别名，请重启终端或执行 source ~/.zshrc (或 ~/.bashrc) 生效。"
