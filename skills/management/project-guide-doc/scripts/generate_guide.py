#!/usr/bin/env python3
"""
Project Development Guide Generator

Automatically scans project structure, detects tech stack, and generates
a comprehensive DEVELOPMENT_GUIDE.md file in the docs/ directory.

Usage:
    generate_guide.py --project-root <path> [--output <path>] [--language <lang>]

Examples:
    # Generate guide for a project (default: Chinese)
    python3 generate_guide.py --project-root /path/to/project
    
    # Generate English guide
    python3 generate_guide.py --project-root /path/to/project --language en
    
    # Custom output location
    python3 generate_guide.py --project-root /path/to/project --output docs/DEV_GUIDE.md
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Language configurations
LANGUAGES = {
    'zh': {
        'doc_subtitle': '本文档为开发团队提供项目概览、技术栈、开发流程和最佳实践指南。',
        'overview_title': '📋 项目概述',
        'overview_placeholder': '[请补充项目简介、主要功能和目标用户]',
        'structure_title': '🏗️ 项目结构',
        'tech_stack_title': '🛠️ 技术栈',
        'setup_title': '🚀 开发环境设置',
        'setup_clone': '1. 克隆项目',
        'setup_install': '2. 安装依赖',
        'setup_env': '3. 环境配置',
        'setup_env_placeholder': '[请配置必要的环境变量]',
        'commands_title': '💻 常用命令',
        'commands_dev': '开发',
        'commands_build': '构建',
        'commands_test': '测试',
        'commands_lint': '代码检查与格式化',
        'commands_other': '其他命令',
        'coding_title': '📝 编码规范',
        'coding_placeholder': '[请补充项目特定的代码风格和最佳实践]',
        'docker_title': '🐳 Docker',
        'docker_description': '项目包含 Docker 配置文件。',
        'docker_build': '# 构建镜像',
        'docker_run': '# 运行容器',
        'docker_note': '[请根据实际情况调整端口和配置]',
        'testing_title': '🧪 测试',
        'testing_description': '项目包含测试文件，请参考测试目录了解测试策略。',
        'testing_placeholder': '[请补充测试命令和覆盖率要求]',
        'dir_src': '源代码',
        'dir_app': '应用代码',
        'dir_pages': '页面组件',
        'dir_components': '可复用组件',
        'dir_composables': 'Composables',
        'dir_lib': '库代码',
        'dir_utils': '工具函数',
        'dir_helpers': '辅助函数',
        'dir_api': 'API 路由/端点',
        'dir_server': '服务器代码',
        'dir_services': '服务层',
        'dir_models': '数据模型',
        'dir_controllers': '控制器',
        'dir_views': '视图模板',
        'dir_public': '公共静态文件',
        'dir_static': '静态资源',
        'dir_assets': '资源文件',
        'dir_styles': '样式文件',
        'dir_css': 'CSS 文件',
        'dir_scss': 'SCSS 文件',
        'dir_tests': '测试文件',
        'dir_test': '测试文件',
        'dir___tests__': '测试文件',
        'dir_docs': '文档',
        'dir_scripts': '工具脚本',
        'dir_config': '配置文件',
        'dir_database': '数据库文件',
        'dir_migrations': '数据库迁移',
        'dir_middleware': '中间件',
        'dir_plugins': '插件',
        'dir_layouts': '布局组件',
        'dir_store': '状态管理',
        'dir_types': '类型定义',
    },
    'en': {
        'doc_subtitle': 'This document provides project overview, tech stack, development workflow and best practices for the development team.',
        'overview_title': '📋 Project Overview',
        'overview_placeholder': '[Please add project introduction, main features and target users]',
        'structure_title': '🏗️ Project Structure',
        'tech_stack_title': '🛠️ Tech Stack',
        'setup_title': '🚀 Environment Setup',
        'setup_clone': '1. Clone Repository',
        'setup_install': '2. Install Dependencies',
        'setup_env': '3. Environment Configuration',
        'setup_env_placeholder': '[Please configure necessary environment variables]',
        'commands_title': '💻 Common Commands',
        'commands_dev': 'Development',
        'commands_build': 'Build',
        'commands_test': 'Testing',
        'commands_lint': 'Linting & Formatting',
        'commands_other': 'Other Commands',
        'coding_title': '📝 Coding Standards',
        'coding_placeholder': '[Please add project-specific code style and best practices]',
        'docker_title': '🐳 Docker',
        'docker_description': 'This project includes Docker configuration.',
        'docker_build': '# Build image',
        'docker_run': '# Run container',
        'docker_note': '[Please adjust ports and configurations as needed]',
        'testing_title': '🧪 Testing',
        'testing_description': 'This project includes test files. Please refer to the test directory for testing strategy.',
        'testing_placeholder': '[Please add test commands and coverage requirements]',
        'dir_src': 'Source code',
        'dir_app': 'Application code',
        'dir_pages': 'Page components',
        'dir_components': 'Reusable components',
        'dir_composables': 'Composables',
        'dir_lib': 'Library code',
        'dir_utils': 'Utility functions',
        'dir_helpers': 'Helper functions',
        'dir_api': 'API routes/endpoints',
        'dir_server': 'Server code',
        'dir_services': 'Service layer',
        'dir_models': 'Data models',
        'dir_controllers': 'Controllers',
        'dir_views': 'View templates',
        'dir_public': 'Public static files',
        'dir_static': 'Static assets',
        'dir_assets': 'Asset files',
        'dir_styles': 'Stylesheets',
        'dir_css': 'CSS files',
        'dir_scss': 'SCSS files',
        'dir_tests': 'Test files',
        'dir_test': 'Test files',
        'dir___tests__': 'Test files',
        'dir_docs': 'Documentation',
        'dir_scripts': 'Utility scripts',
        'dir_config': 'Configuration files',
        'dir_database': 'Database files',
        'dir_migrations': 'Database migrations',
        'dir_middleware': 'Middleware',
        'dir_plugins': 'Plugins',
        'dir_layouts': 'Layout components',
        'dir_store': 'State management',
        'dir_types': 'Type definitions',
    },
    'ja': {
        'doc_subtitle': 'このドキュメントは、開発チームにプロジェクト概要、技術スタック、開発ワークフロー、ベストプラクティスを提供します。',
        'overview_title': '📋 プロジェクト概要',
        'overview_placeholder': '[プロジェクトの紹介、主な機能、対象ユーザーを追加してください]',
        'structure_title': '🏗️ プロジェクト構造',
        'tech_stack_title': '🛠️ 技術スタック',
        'setup_title': '🚀 開発環境のセットアップ',
        'setup_clone': '1. リポジトリのクローン',
        'setup_install': '2. 依存関係のインストール',
        'setup_env': '3. 環境設定',
        'setup_env_placeholder': '[必要な環境変数を設定してください]',
        'commands_title': '💻 よく使うコマンド',
        'commands_dev': '開発',
        'commands_build': 'ビルド',
        'commands_test': 'テスト',
        'commands_lint': 'リントとフォーマット',
        'commands_other': 'その他のコマンド',
        'coding_title': '📝 コーディング規約',
        'coding_placeholder': '[プロジェクト固有のコードスタイルとベストプラクティスを追加してください]',
        'docker_title': '🐳 Docker',
        'docker_description': 'このプロジェクトにはDocker設定が含まれています。',
        'docker_build': '# イメージをビルド',
        'docker_run': '# コンテナを実行',
        'docker_note': '[必要に応じてポートと設定を調整してください]',
        'testing_title': '🧪 テスト',
        'testing_description': 'このプロジェクトにはテストファイルが含まれています。テスト戦略については、testディレクトリを参照してください。',
        'testing_placeholder': '[テストコマンドとカバレッジ要件を追加してください]',
        'dir_src': 'ソースコード',
        'dir_app': 'アプリケーションコード',
        'dir_pages': 'ページコンポーネント',
        'dir_components': '再利用可能なコンポーネント',
        'dir_composables': 'Composables',
        'dir_lib': 'ライブラリコード',
        'dir_utils': 'ユーティリティ関数',
        'dir_helpers': 'ヘルパー関数',
        'dir_api': 'APIルート/エンドポイント',
        'dir_server': 'サーバーコード',
        'dir_services': 'サービス層',
        'dir_models': 'データモデル',
        'dir_controllers': 'コントローラー',
        'dir_views': 'ビューテンプレート',
        'dir_public': '公開静的ファイル',
        'dir_static': '静的アセット',
        'dir_assets': 'アセットファイル',
        'dir_styles': 'スタイルシート',
        'dir_css': 'CSSファイル',
        'dir_scss': 'SCSSファイル',
        'dir_tests': 'テストファイル',
        'dir_test': 'テストファイル',
        'dir___tests__': 'テストファイル',
        'dir_docs': 'ドキュメント',
        'dir_scripts': 'ユーティリティスクリプト',
        'dir_config': '設定ファイル',
        'dir_database': 'データベースファイル',
        'dir_migrations': 'データベースマイグレーション',
        'dir_middleware': 'ミドルウェア',
        'dir_plugins': 'プラグイン',
        'dir_layouts': 'レイアウトコンポーネント',
        'dir_store': '状態管理',
        'dir_types': '型定義',
    }
}


class ProjectAnalyzer:
    """Analyzes project structure and detects technology stack"""
    
    def __init__(self, project_root: Path, language: str = 'zh'):
        self.project_root = project_root
        self.language = language
        self.lang = LANGUAGES.get(language, LANGUAGES['zh'])
        self.tech_stack = []
        self.package_manager = None
        self.framework = None
        self.scripts = {}
        self.directories = {}
        self.has_docker = False
        self.has_tests = False
        
    def analyze(self) -> Dict:
        """Run full project analysis"""
        self._detect_tech_stack()
        self._analyze_structure()
        self._extract_commands()
        
        return {
            'tech_stack': self.tech_stack,
            'package_manager': self.package_manager,
            'framework': self.framework,
            'scripts': self.scripts,
            'directories': self.directories,
            'has_docker': self.has_docker,
            'has_tests': self.has_tests,
        }
    
    def _detect_tech_stack(self):
        """Detect technology stack from project files"""
        
        # Node.js / JavaScript / TypeScript
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                    
                # Detect package manager
                if (self.project_root / 'pnpm-lock.yaml').exists():
                    self.package_manager = 'pnpm'
                elif (self.project_root / 'yarn.lock').exists():
                    self.package_manager = 'yarn'
                elif (self.project_root / 'package-lock.json').exists():
                    self.package_manager = 'npm'
                else:
                    self.package_manager = 'npm'
                
                # Detect framework
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                
                if 'next' in deps:
                    self.framework = 'Next.js'
                    version = deps.get('next', '').replace('^', '').replace('~', '')
                    self.tech_stack.append(f"Next.js {version}")
                elif 'nuxt' in deps:
                    self.framework = 'Nuxt'
                    version = deps.get('nuxt', '').replace('^', '').replace('~', '')
                    self.tech_stack.append(f"Nuxt {version}")
                elif 'react' in deps:
                    self.framework = 'React'
                    version = deps.get('react', '').replace('^', '').replace('~', '')
                    self.tech_stack.append(f"React {version}")
                elif 'vue' in deps:
                    self.framework = 'Vue'
                    version = deps.get('vue', '').replace('^', '').replace('~', '')
                    self.tech_stack.append(f"Vue {version}")
                elif 'svelte' in deps:
                    self.framework = 'Svelte'
                    self.tech_stack.append("Svelte")
                
                # TypeScript
                if 'typescript' in deps:
                    self.tech_stack.append("TypeScript")
                
                # Build tools
                if 'vite' in deps:
                    self.tech_stack.append("Vite")
                elif 'webpack' in deps:
                    self.tech_stack.append("Webpack")
                
                # Backend frameworks (only if clearly backend)
                if 'express' in deps and not any(fw in deps for fw in ['next', 'nuxt']):
                    self.tech_stack.append("Express.js")
                if 'fastify' in deps:
                    self.tech_stack.append("Fastify")
                if 'koa' in deps:
                    self.tech_stack.append("Koa")
                    
            except json.JSONDecodeError:
                pass
        
        # Python
        requirements_txt = self.project_root / 'requirements.txt'
        pyproject_toml = self.project_root / 'pyproject.toml'
        
        if requirements_txt.exists() or pyproject_toml.exists():
            self.tech_stack.append("Python")
            self.package_manager = 'pip'
            
            if requirements_txt.exists():
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        self.framework = 'Django'
                        self.tech_stack.append("Django")
                    elif 'flask' in content:
                        self.framework = 'Flask'
                        self.tech_stack.append("Flask")
                    elif 'fastapi' in content:
                        self.framework = 'FastAPI'
                        self.tech_stack.append("FastAPI")
        
        # Go
        go_mod = self.project_root / 'go.mod'
        if go_mod.exists():
            self.tech_stack.append("Go")
            self.package_manager = 'go modules'
        
        # Ruby
        gemfile = self.project_root / 'Gemfile'
        if gemfile.exists():
            self.tech_stack.append("Ruby")
            self.package_manager = 'bundler'
            with open(gemfile, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'rails' in content.lower():
                    self.framework = 'Ruby on Rails'
                    self.tech_stack.append("Ruby on Rails")
        
        # Java / Kotlin
        pom_xml = self.project_root / 'pom.xml'
        build_gradle = self.project_root / 'build.gradle'
        if pom_xml.exists():
            self.tech_stack.append("Java")
            self.package_manager = 'Maven'
        elif build_gradle.exists():
            self.tech_stack.append("Java/Kotlin")
            self.package_manager = 'Gradle'
        
        # Flutter
        pubspec_yaml = self.project_root / 'pubspec.yaml'
        if pubspec_yaml.exists():
            self.tech_stack.append("Flutter")
            self.package_manager = 'pub'
        
        # Docker
        if (self.project_root / 'Dockerfile').exists():
            self.has_docker = True
            self.tech_stack.append("Docker")
        if (self.project_root / 'docker-compose.yml').exists() or (self.project_root / 'docker-compose.yaml').exists():
            self.has_docker = True
            if "Docker" not in self.tech_stack:
                self.tech_stack.append("Docker Compose")
    
    def _analyze_structure(self):
        """Analyze project directory structure"""
        common_dirs = {
            'src': 'dir_src',
            'app': 'dir_app',
            'pages': 'dir_pages',
            'components': 'dir_components',
            'composables': 'dir_composables',
            'lib': 'dir_lib',
            'utils': 'dir_utils',
            'helpers': 'dir_helpers',
            'api': 'dir_api',
            'server': 'dir_server',
            'services': 'dir_services',
            'models': 'dir_models',
            'controllers': 'dir_controllers',
            'views': 'dir_views',
            'public': 'dir_public',
            'static': 'dir_static',
            'assets': 'dir_assets',
            'styles': 'dir_styles',
            'css': 'dir_css',
            'scss': 'dir_scss',
            'tests': 'dir_tests',
            'test': 'dir_test',
            '__tests__': 'dir___tests__',
            'docs': 'dir_docs',
            'scripts': 'dir_scripts',
            'config': 'dir_config',
            'database': 'dir_database',
            'migrations': 'dir_migrations',
            'middleware': 'dir_middleware',
            'plugins': 'dir_plugins',
            'layouts': 'dir_layouts',
            'store': 'dir_store',
            'types': 'dir_types',
        }
        
        for dir_name, lang_key in common_dirs.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # Get localized description
                description = self.lang.get(lang_key, dir_name)
                self.directories[dir_name] = description
                # Check if it's a test directory
                if dir_name in ['tests', 'test', '__tests__']:
                    self.has_tests = True
    
    def _extract_commands(self):
        """Extract common commands from package.json, Makefile, etc."""
        
        # npm/yarn/pnpm scripts
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                    scripts = pkg.get('scripts', {})
                    
                    for script_name, script_cmd in scripts.items():
                        cmd_prefix = self.package_manager if self.package_manager else 'npm'
                        self.scripts[script_name] = {
                            'command': f"{cmd_prefix} run {script_name}",
                            'description': script_cmd,
                            'category': self._categorize_script(script_name, script_cmd)
                        }
            except json.JSONDecodeError:
                pass
        
        # Makefile
        makefile = self.project_root / 'Makefile'
        if makefile.exists():
            try:
                with open(makefile, 'r', encoding='utf-8') as f:
                    for line in f:
                        if ':' in line and not line.startswith('\t') and not line.startswith('#'):
                            target = line.split(':')[0].strip()
                            if target and not target.startswith('.'):
                                self.scripts[f"make_{target}"] = {
                                    'command': f"make {target}",
                                    'description': f"运行 make 目标: {target}",
                                    'category': 'make'
                                }
            except Exception:
                pass

    def _categorize_script(self, name: str, cmd: str) -> str:
        """Categorize a script by its purpose"""
        name_lower = name.lower()
        cmd_lower = cmd.lower()
        
        # Development
        if any(word in name_lower for word in ['dev', 'serve', 'start']):
            return 'dev'
        # Build
        if any(word in name_lower for word in ['build', 'compile']):
            return 'build'
        # Test
        if any(word in name_lower for word in ['test', 'spec']):
            return 'test'
        # Lint
        if any(word in name_lower for word in ['lint', 'format', 'prettier']):
            return 'lint'
        # Deploy
        if any(word in name_lower for word in ['deploy', 'publish', 'release']):
            return 'deploy'
        # Other
        return 'other'


class GuideGenerator:
    """Generates DEVELOPMENT_GUIDE.md dynamically based on project content"""
    
    def __init__(self, analysis: Dict, project_name: str, language: str = 'zh'):
        self.analysis = analysis
        self.project_name = project_name
        self.language = language
        self.lang = LANGUAGES.get(language, LANGUAGES['zh'])
    
    def generate(self) -> str:
        """Generate guide content dynamically"""
        sections = []
        
        # Header
        if self.language == 'zh':
            sections.append(f"# {self.project_name} - 开发指南")
        elif self.language == 'ja':
            sections.append(f"# {self.project_name} - 開発ガイド")
        else:
            sections.append(f"# {self.project_name} - Development Guide")
        sections.append("")
        sections.append(f"> {self.lang['doc_subtitle']}")
        sections.append("")
        
        # Project Overview
        sections.extend(self._generate_overview())
        
        # Architecture & Structure (only if we have directories)
        if self.analysis['directories']:
            sections.extend(self._generate_architecture())
        
        # Tech Stack (only if detected)
        if self.analysis['tech_stack']:
            sections.extend(self._generate_tech_stack())
        
        # Setup
        sections.extend(self._generate_setup())
        
        # Commands (only if we have commands)
        if self.analysis['scripts']:
            sections.extend(self._generate_commands())
        
        # Coding Standards (minimal)
        sections.extend(self._generate_coding_standards())
        
        # Docker (only if has docker)
        if self.analysis['has_docker']:
            sections.extend(self._generate_docker_section())
        
        # Testing (only if has tests)
        if self.analysis['has_tests']:
            sections.extend(self._generate_testing_section())
        
        return '\n'.join(sections)
    
    def _generate_overview(self) -> List[str]:
        """Generate project overview section"""
        return [
            f"## {self.lang['overview_title']}",
            "",
            self.lang['overview_placeholder'],
            "",
            "---",
            ""
        ]
    
    def _generate_architecture(self) -> List[str]:
        """Generate architecture section"""
        lines = [
            f"## {self.lang['structure_title']}",
            "",
            "```"
        ]
        
        lines.append(f"{self.project_name}/")
        for dir_name, description in sorted(self.analysis['directories'].items()):
            lines.append(f"├── {dir_name}/     # {description}")
        
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _generate_tech_stack(self) -> List[str]:
        """Generate tech stack section"""
        lines = [
            f"## {self.lang['tech_stack_title']}",
            ""
        ]
        
        for tech in self.analysis['tech_stack']:
            lines.append(f"- {tech}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _generate_setup(self) -> List[str]:
        """Generate setup section"""
        clone_text = 'git clone [仓库地址]' if self.language == 'zh' else ('git clone [リポジトリURL]' if self.language == 'ja' else 'git clone [repository-url]')
        
        lines = [
            f"## {self.lang['setup_title']}",
            "",
            f"### {self.lang['setup_clone']}",
            "",
            "```bash",
            clone_text,
            f"cd {self.project_name}",
            "```",
            "",
            f"### {self.lang['setup_install']}",
            ""
        ]
        
        pm = self.analysis.get('package_manager')
        if pm == 'npm':
            lines.append("```bash")
            lines.append("npm install")
            lines.append("```")
        elif pm == 'pnpm':
            lines.append("```bash")
            lines.append("pnpm install")
            lines.append("```")
        elif pm == 'yarn':
            lines.append("```bash")
            lines.append("yarn install")
            lines.append("```")
        elif pm == 'pip':
            lines.append("```bash")
            lines.append("pip install -r requirements.txt")
            lines.append("```")
        elif pm == 'go modules':
            lines.append("```bash")
            lines.append("go mod download")
            lines.append("```")
        else:
            install_placeholder = '[请补充安装命令]' if self.language == 'zh' else ('[インストールコマンドを追加]' if self.language == 'ja' else '[add install command]')
            lines.append(install_placeholder)
        
        lines.append("")
        
        # Environment config if needed
        if (Path(self.analysis.get('project_root', '.')) / '.env.example').exists():
            lines.append(f"### {self.lang['setup_env']}")
            lines.append("")
            lines.append("```bash")
            lines.append("cp .env.example .env")
            lines.append("```")
            lines.append("")
            lines.append(self.lang['setup_env_placeholder'])
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _generate_commands(self) -> List[str]:
        """Generate commands section"""
        lines = [
            f"## {self.lang['commands_title']}",
            ""
        ]
        
        # Categorize scripts
        dev_scripts = []
        build_scripts = []
        test_scripts = []
        lint_scripts = []
        other_scripts = []
        
        for name, info in self.analysis['scripts'].items():
            category = info.get('category', 'other')
            script_info = (name, info['command'])
            
            if category == 'dev':
                dev_scripts.append(script_info)
            elif category == 'build':
                build_scripts.append(script_info)
            elif category == 'test':
                test_scripts.append(script_info)
            elif category == 'lint':
                lint_scripts.append(script_info)
            else:
                other_scripts.append(script_info)
        
        # Dev commands
        if dev_scripts:
            lines.append(f"### {self.lang['commands_dev']}")
            lines.append("")
            for name, cmd in dev_scripts:
                lines.append(f"```bash")
                lines.append(f"# {name}")
                lines.append(cmd)
                lines.append("```")
                lines.append("")
        
        # Build commands
        if build_scripts:
            lines.append(f"### {self.lang['commands_build']}")
            lines.append("")
            for name, cmd in build_scripts:
                lines.append(f"```bash")
                lines.append(f"# {name}")
                lines.append(cmd)
                lines.append("```")
                lines.append("")
        
        # Test commands
        if test_scripts:
            lines.append(f"### {self.lang['commands_test']}")
            lines.append("")
            for name, cmd in test_scripts:
                lines.append(f"```bash")
                lines.append(f"# {name}")
                lines.append(cmd)
                lines.append("```")
                lines.append("")
        
        # Lint/format commands
        if lint_scripts:
            lines.append(f"### {self.lang['commands_lint']}")
            lines.append("")
            for name, cmd in lint_scripts:
                lines.append(f"```bash")
                lines.append(f"# {name}")
                lines.append(cmd)
                lines.append("```")
                lines.append("")
        
        # Other commands (limit to 5)
        if other_scripts:
            lines.append(f"### {self.lang['commands_other']}")
            lines.append("")
            for name, cmd in other_scripts[:5]:
                lines.append(f"```bash")
                lines.append(f"# {name}")
                lines.append(cmd)
                lines.append("```")
                lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _generate_coding_standards(self) -> List[str]:
        """Generate minimal coding standards section"""
        return [
            f"## {self.lang['coding_title']}",
            "",
            self.lang['coding_placeholder'],
            "",
            "---",
            ""
        ]
    
    def _generate_docker_section(self) -> List[str]:
        """Generate Docker section if Docker files exist"""
        return [
            f"## {self.lang['docker_title']}",
            "",
            self.lang['docker_description'],
            "",
            "```bash",
            self.lang['docker_build'],
            "docker build -t " + self.project_name + " .",
            "",
            self.lang['docker_run'],
            "docker run -p 3000:3000 " + self.project_name,
            "```",
            "",
            self.lang['docker_note'],
            "",
            "---",
            ""
        ]
    
    def _generate_testing_section(self) -> List[str]:
        """Generate testing section if tests exist"""
        return [
            f"## {self.lang['testing_title']}",
            "",
            self.lang['testing_description'],
            "",
            self.lang['testing_placeholder'],
            "",
            "---",
            ""
        ]


def main():
    parser = argparse.ArgumentParser(description='Generate project development guide')
    parser.add_argument('--project-root', required=True, help='Project root directory')
    parser.add_argument('--output', help='Output file path (default: docs/DEVELOPMENT_GUIDE.md)')
    parser.add_argument('--project-name', help='Project name (default: inferred from directory)')
    parser.add_argument('--language', default='zh', choices=['zh', 'en', 'ja'], help='Output language (default: zh)')
    
    args = parser.parse_args()
    
    # Validate project root
    project_root = Path(args.project_root).resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"❌ Error: Project root does not exist: {project_root}")
        sys.exit(1)
    
    # Determine project name
    project_name = args.project_name or project_root.name
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = project_root / output_path
    else:
        output_path = project_root / 'docs' / 'DEVELOPMENT_GUIDE.md'
    
    # Localized messages
    lang_messages = {
        'zh': {
            'analyzing': '🔍 分析项目',
            'path': '   路径',
            'detected': '✅ 检测到技术栈:',
            'no_tech': '⚠️  未检测到明确的技术栈',
            'dirs_found': '📁 检测到',
            'dirs_suffix': '个目录',
            'commands_found': '⚙️  检测到',
            'commands_suffix': '个命令',
            'generating': '📝 生成开发指南...',
            'success': '✅ 开发指南生成成功!',
            'output': '   输出路径',
            'next_steps': '💡 下一步:',
            'step1': '   1. 审阅生成的文档',
            'step2': '   2. 补充标记为 [请补充] 的内容',
            'step3': '   3. 添加项目特定的业务逻辑说明',
        },
        'en': {
            'analyzing': '🔍 Analyzing project',
            'path': '   Path',
            'detected': '✅ Detected tech stack:',
            'no_tech': '⚠️  No explicit tech stack detected',
            'dirs_found': '📁 Found',
            'dirs_suffix': 'directories',
            'commands_found': '⚙️  Found',
            'commands_suffix': 'commands',
            'generating': '📝 Generating development guide...',
            'success': '✅ Development guide generated successfully!',
            'output': '   Output path',
            'next_steps': '💡 Next steps:',
            'step1': '   1. Review the generated document',
            'step2': '   2. Fill in content marked with placeholders',
            'step3': '   3. Add project-specific business logic descriptions',
        },
        'ja': {
            'analyzing': '🔍 プロジェクトを分析中',
            'path': '   パス',
            'detected': '✅ 検出された技術スタック:',
            'no_tech': '⚠️  明示的な技術スタックが検出されませんでした',
            'dirs_found': '📁 検出',
            'dirs_suffix': 'ディレクトリ',
            'commands_found': '⚙️  検出',
            'commands_suffix': 'コマンド',
            'generating': '📝 開発ガイドを生成中...',
            'success': '✅ 開発ガイドが正常に生成されました!',
            'output': '   出力パス',
            'next_steps': '💡 次のステップ:',
            'step1': '   1. 生成されたドキュメントを確認',
            'step2': '   2. プレースホルダーでマークされたコンテンツを入力',
            'step3': '   3. プロジェクト固有のビジネスロジックの説明を追加',
        }
    }
    
    msg = lang_messages.get(args.language, lang_messages['zh'])
    
    print(f"{msg['analyzing']}: {project_name}")
    print(f"{msg['path']}: {project_root}")
    
    # Analyze project
    analyzer = ProjectAnalyzer(project_root, args.language)
    analyzer.analysis = {'project_root': str(project_root)}  # Store for later use
    analysis = analyzer.analyze()
    
    if analysis['tech_stack']:
        print(f"\n{msg['detected']}")
        for tech in analysis['tech_stack']:
            print(f"   - {tech}")
    else:
        print(f"\n{msg['no_tech']}")
    
    if analysis['directories']:
        print(f"\n{msg['dirs_found']} {len(analysis['directories'])} {msg['dirs_suffix']}")
    
    if analysis['scripts']:
        print(f"{msg['commands_found']} {len(analysis['scripts'])} {msg['commands_suffix']}")
    
    # Generate guide
    print(f"\n{msg['generating']}")
    generator = GuideGenerator(analysis, project_name, args.language)
    content = generator.generate()
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n{msg['success']}")
    print(f"{msg['output']}: {output_path}")
    print(f"\n{msg['next_steps']}")
    print(msg['step1'])
    print(msg['step2'])
    print(msg['step3'])


if __name__ == '__main__':
    main()
