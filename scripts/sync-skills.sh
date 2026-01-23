#!/bin/bash

# =================================================================
# Core Foundry - Skills 终极同步工具
# 功能：
# 1. 自动检测环境 (Mac/Linux/WSL)
# 2. 物理复制模式同步技能到各 IDE
# 3. 自动安装 Shell 别名 (cf-sync)
# 4. 记忆用户偏好（IDE & Skill 选择）
# 5. Git 远程更新检查
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
# 获取脚本所在的目录 (scripts 目录)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# 仓库根目录应为脚本目录的上一级
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
SKILLS_SRC="$REPO_ROOT/skills"
HOOKS_DIR="$REPO_ROOT/.githooks"

echo -e "${CYAN}===============================================${NC}"
echo -e "${CYAN}      🚀 Core Foundry Skills Manager           ${NC}"
echo -e "${CYAN}===============================================${NC}"

# --- 1. Git 状态快速检查 ---
check_git_status() {
    echo -e "${BLUE}$ICON_FIND 检查远程更新...${NC}"
    # 在仓库目录下执行 git 命令
    pushd "$REPO_ROOT" > /dev/null 2>&1 || return
    
    # 异步获取更新，不阻塞
    git fetch --quiet origin main 2>/dev/null &
    
    LOCAL=$(git rev-parse @ 2>/dev/null)
    REMOTE=$(git rev-parse @{u} 2>/dev/null)
    
    if [ "$LOCAL" != "$REMOTE" ] && [ ! -z "$REMOTE" ]; then
        echo -e "${YELLOW}$ICON_WARN 注意：云端有新的技能更新，建议同步前执行 'cd $REPO_ROOT && git pull'${NC}"
    fi
    
    popd > /dev/null 2>&1
}

# --- 2. 目标环境检测 (跨平台) ---
detect_targets() {
    local mac_app_support="$HOME/Library/Application Support"
    local linux_config="$HOME/.config"
    
    # 待检测列表: "名称|目标子目录|检测目录"
    local check_list=(
        "Antigravity|$HOME/.gemini/antigravity/global_skills|$HOME/.gemini/antigravity"
        "Cursor|$HOME/.cursor/skills|$HOME/.cursor"
        "Trae (字节)|$HOME/.trae/skills|$HOME/.trae"
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

# --- 3. 别名自动安装 (cf-sync) ---
install_alias() {
    local shell_rcs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile")
    local alias_cmd="alias cf-sync='bash $SCRIPT_DIR/sync-skills.sh'"
    local installed=false

    for rc in "${shell_rcs[@]}"; do
        if [ -f "$rc" ]; then
            if ! grep -q "alias cf-sync=" "$rc"; then
                echo "" >> "$rc"
                echo "# Core Foundry Skills Sync Alias" >> "$rc"
                echo "$alias_cmd" >> "$rc"
                installed=true
            else
                # 更新现有的 alias，防止路径变动 (兼容 macOS 和 Linux)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s|alias cf-sync=.*|$alias_cmd|" "$rc" 2>/dev/null
                else
                    sed -i "s|alias cf-sync=.*|$alias_cmd|" "$rc" 2>/dev/null
                fi
            fi
        fi
    done

    if [ "$installed" = true ]; then
        echo -e "${PURPLE}$ICON_LINK 已自动为您安装别名 'cf-sync'${NC}"
        echo -e "${YELLOW}提示：由于当前进程限制，请手动执行 'source ~/.zshrc' (或对应的 RC 文件) 以使别名在当前窗口生效。${NC}"
    fi
}

# --- 4. 获取所有可用技能 ---
get_repo_skills() {
    ALL_SKILLS_NAMES=()
    ALL_SKILLS_PATHS=()
    ALL_SKILLS_DESCS=()
    
    for category in "$SKILLS_SRC"/*; do
        if [ -d "$category" ]; then
            for skill_dir in "$category"/*; do
                if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
                    local s_name=$(basename "$skill_dir")
                    local skill_md="$skill_dir/SKILL.md"
                    local s_desc=""
                    
                    # 1. 尝试从 YAML Frontmatter 提取 (description: xxx)
                    s_desc=$(grep -i "^description:" "$skill_md" | head -n 1 | sed 's/^[Dd]escription: *//i' | sed 's/^["'\'']//;s/["'\'']$//')
                    
                    # 2. 如果没找到，尝试从第一行或描述行提取 (> 描述：xxx)
                    if [ -z "$s_desc" ]; then
                        s_desc=$(grep -E "^> (描述|Description)：?" "$skill_md" | head -n 1 | sed -E 's/^> (描述|Description)：?//g')
                    fi
                    
                    # 3. 实在不行取第一行文本 (去掉 # 标题)
                    if [ -z "$s_desc" ]; then
                        s_desc=$(grep -v "^---" "$skill_md" | grep -v "^#" | grep -v "^$" | head -n 1 | sed 's/^[[:space:]]*//')
                    fi

                    # 清理可能存在的引号和空格
                    s_desc=$(echo "$s_desc" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                    [ -z "$s_desc" ] && s_desc="点击 SKILL.md 查看详情"

                    # 智能截断：控制在 45 个字符以内（考虑中文字符宽度）
                    if [ ${#s_desc} -gt 45 ]; then
                        s_desc="${s_desc:0:45}..."
                    fi
                    
                    ALL_SKILLS_NAMES+=("$s_name")
                    ALL_SKILLS_PATHS+=("$skill_dir")
                    ALL_SKILLS_DESCS+=("$s_desc")
                fi
            done
        fi
    done
}

# --- 5. 同步核心逻辑 ---
sync_now() {
    local target_path="$1"
    local target_name="$2"
    local mode="$3" # link or copy
    local selected_skills_indices=($4)

    echo -e "\n${BLUE}$ICON_SYNC 同步至 $target_name ($mode 模式)...${NC}"
    mkdir -p "$target_path"

    # 执行同步
    for idx in "${selected_skills_indices[@]}"; do
        local s_name="${ALL_SKILLS_NAMES[$idx]}"
        local s_path="${ALL_SKILLS_PATHS[$idx]}"
        local dest="$target_path/$s_name"

        # 删除旧的 (不论是软链还是文件)
        rm -rf "$dest"

        if [ "$mode" == "link" ]; then
            ln -s "$s_path" "$dest"
            echo -e "  ${CYAN}[LINK]${NC} $s_name"
        else
            cp -R "$s_path" "$dest"
            echo -e "  ${GREEN}[COPY]${NC} $s_name"
        fi
    done

    # --- 反向清理 (只清理不在 ALL_SKILLS_NAMES 里的，且用户可能想保留的非本项目技能除外) ---
    # 注意：为了安全，这里只清理在本次仓库中存在但未被选中的技能（可选，但通常建议全量清理旧的本项目技能）
}

# --- 6. 偏好记忆逻辑 ---
PREF_FILE="$HOME/.core_foundry_prefs"
load_prefs() {
    if [ -f "$PREF_FILE" ]; then
        source "$PREF_FILE" 2>/dev/null
    fi
}

save_prefs() {
    local ide_indices="$1"
    local skill_indices="$2"
    echo "LAST_IDE_INDICES=\"$ide_indices\"" > "$PREF_FILE"
    echo "LAST_SKILL_INDICES=\"$skill_indices\"" >> "$PREF_FILE"
}

# 验证偏好索引是否仍然有效
validate_ide_indices() {
    local valid_indices=()
    for idx in $LAST_IDE_INDICES; do
        if [ "$idx" -ge 0 ] && [ "$idx" -lt ${#DETECTED_NAMES[@]} ] 2>/dev/null; then
            valid_indices+=($idx)
        fi
    done
    LAST_IDE_INDICES="${valid_indices[*]}"
}

# --- 执行流程 ---
load_prefs
check_git_status
detect_targets

if [ ${#DETECTED_NAMES[@]} -eq 0 ]; then
    echo -e "${RED}$ICON_WARN 未检测到可用 IDE。${NC}"
    exit 1
fi

# 1. 选择 IDE
SELECTED_IDE_INDICES=()
validate_ide_indices
if [ ! -z "$LAST_IDE_INDICES" ]; then
    echo -e "\n${BLUE}1. 检测到上次选择的 IDE: ${NC}"
    for idx in $LAST_IDE_INDICES; do
        echo -e "  - ${DETECTED_NAMES[$idx]}"
    done
    read -p "是否沿用上次选择？[Y/n]: " use_last
    if [[ "$use_last" != "n" ]]; then
        for idx in $LAST_IDE_INDICES; do SELECTED_IDE_INDICES+=($idx); done
    fi
fi

if [ ${#SELECTED_IDE_INDICES[@]} -eq 0 ]; then
    echo -e "\n${BLUE}1. 请选择目标 IDEs (支持多选，如: 1 2, 'a' 全部, 'q' 退出):${NC}"
    for i in "${!DETECTED_NAMES[@]}"; do
        echo -e "  $((i+1)). ${DETECTED_NAMES[$i]}"
    done
    read -p "选择 IDE: " ide_choice

    if [[ "$ide_choice" == "a" ]]; then
        for i in "${!DETECTED_NAMES[@]}"; do SELECTED_IDE_INDICES+=($i); done
    elif [[ "$ide_choice" == "q" ]]; then exit 0
    else
        for c in $ide_choice; do
            if [[ "$c" =~ ^[0-9]+$ ]] && [ "$c" -ge 1 ] && [ "$c" -le ${#DETECTED_NAMES[@]} ]; then
                SELECTED_IDE_INDICES+=($((c-1)))
            fi
        done
    fi
fi

if [ ${#SELECTED_IDE_INDICES[@]} -eq 0 ]; then exit 0; fi

# 2. 选择技能
get_repo_skills

# 验证 Skill 索引有效性
validate_skill_indices() {
    local valid_indices=()
    for idx in $LAST_SKILL_INDICES; do
        if [ "$idx" -ge 0 ] && [ "$idx" -lt ${#ALL_SKILLS_NAMES[@]} ] 2>/dev/null; then
            valid_indices+=($idx)
        fi
    done
    LAST_SKILL_INDICES="${valid_indices[*]}"
}

SELECTED_SKILL_INDICES=()
validate_skill_indices
if [ ! -z "$LAST_SKILL_INDICES" ]; then
    echo -e "\n${BLUE}2. 检测到上次选择的 Skills: ${NC}"
    for idx in $LAST_SKILL_INDICES; do
        echo -e "  - ${ALL_SKILLS_NAMES[$idx]}"
    done
    read -p "是否沿用上次选择？[Y/n]: " use_last_skill
    if [[ "$use_last_skill" != "n" ]]; then
        for idx in $LAST_SKILL_INDICES; do SELECTED_SKILL_INDICES+=($idx); done
    fi
fi

if [ ${#SELECTED_SKILL_INDICES[@]} -eq 0 ]; then
    echo -e "\n${BLUE}2. 请选择要同步的 Skills (支持多选，如: 1 2, 'a' 全部, 'q' 退出):${NC}"
    for i in "${!ALL_SKILLS_NAMES[@]}"; do
        printf "  %2d. ${CYAN}%-25s${NC} | %s\n" "$((i+1))" "${ALL_SKILLS_NAMES[$i]}" "${ALL_SKILLS_DESCS[$i]}"
    done
    read -p "选择 Skill: " skill_choice

    if [[ "$skill_choice" == "a" ]]; then
        for i in "${!ALL_SKILLS_NAMES[@]}"; do SELECTED_SKILL_INDICES+=($i); done
    elif [[ "$skill_choice" == "q" ]]; then exit 0
    else
        for c in $skill_choice; do
            if [[ "$c" =~ ^[0-9]+$ ]] && [ "$c" -ge 1 ] && [ "$c" -le ${#ALL_SKILLS_NAMES[@]} ]; then
                SELECTED_SKILL_INDICES+=($((c-1)))
            fi
        done
    fi
fi

if [ ${#SELECTED_SKILL_INDICES[@]} -eq 0 ]; then exit 0; fi

# 3. 执行同步
for idx in "${SELECTED_IDE_INDICES[@]}"; do
    sync_now "${DETECTED_PATHS[$idx]}" "${DETECTED_NAMES[$idx]}" "copy" "${SELECTED_SKILL_INDICES[*]}"
done

# 保存用户偏好
save_prefs "${SELECTED_IDE_INDICES[*]}" "${SELECTED_SKILL_INDICES[*]}"

# 自动安装别名
install_alias

echo -e "\n${GREEN}$ICON_OK 全部同步任务完成！${NC}"
echo -e "提示：如果是首次安装别名，请重启终端或执行 source ~/.zshrc (或 ~/.bashrc) 生效。"
