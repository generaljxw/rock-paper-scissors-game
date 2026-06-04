# RockPaperScissors - 猜拳小游戏

一款面向儿童的猜拳小游戏，基于 Python 3.11 + PyQt6 开发，融合卡通元素、积分系统和沉浸式音频体验，支持多种对战模式。

## 功能特性

### 核心功能

- **用户系统**：注册/登录，密码 PBKDF2 加密存储
- **三种对战模式**：
  - 一局定胜负：不耗积分，胜+1/负-1
  - 三局两胜：不耗积分，胜+2/负-2
  - 连战模式：消耗3积分入场，连续胜利3次额外+5分
- **积分系统**：完整的积分计算和入场费机制
- **战绩查询**：每轮对战汇总记录，含对战时间、模式、结果、积分变化
- **胜率统计**：实时计算并展示玩家胜率

### 音频系统（v1.1.0 新增）

- **背景音乐（BGM）**：9首场景音乐，覆盖登录、模式选择、对战、结算等场景，支持无缝循环播放
- **音效（SFX）**：6个出拳与判定音效（石头/剪刀/布/胜利/失败/平局），低延迟触发
- **Ducking 机制**：出拳时自动压低BGM音量至20%，音效播放完毕后延迟恢复至70%，确保音效清晰可辨
- **音量控制**：BGM默认70%、SFX默认100%，支持独立调节

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| GUI框架 | PyQt6 |
| 音频播放 | QMediaPlayer（BGM）+ QSoundEffect（SFX） |
| 数据库 | SQLite |
| 密码加密 | PBKDF2-HMAC-SHA256 |
| 打包工具 | PyInstaller（onedir模式） |
| 日志 | loguru |

## 项目结构

```
RockPaperScissors/
├── src/                        # 源代码
│   ├── main.py                 # 应用入口
│   ├── audio/                  # 音频模块
│   │   ├── audio_manager.py    # 音频管理器（单例，BGM/SFX/Ducking）
│   │   └── __init__.py
│   ├── business/               # 业务逻辑层
│   │   ├── game_engine.py      # 游戏引擎
│   │   ├── score_manager.py    # 积分管理
│   │   ├── statistics.py       # 统计分析
│   │   ├── user_manager.py     # 用户管理
│   │   ├── enums.py            # 枚举定义
│   │   └── __init__.py
│   ├── data/                   # 数据访问层
│   │   ├── database.py         # 数据库管理（单例）
│   │   ├── battle_dao.py       # 对战记录DAO
│   │   ├── score_dao.py        # 积分DAO
│   │   ├── user_dao.py         # 用户DAO
│   │   ├── models.py           # 数据模型
│   │   └── __init__.py
│   ├── ui/                     # UI界面层
│   │   ├── login_window.py     # 登录窗口
│   │   ├── main_window.py      # 主窗口（模式选择）
│   │   ├── battle_window.py    # 对战窗口
│   │   ├── history_window.py   # 战绩窗口
│   │   └── __init__.py
│   ├── config/                 # 配置模块
│   │   ├── settings.py         # 应用配置（含音频参数）
│   │   └── __init__.py
│   └── __init__.py
├── assets/                     # 静态资源
│   └── sounds/                 # 音频资源
│       ├── bgm/                # 背景音乐（9首WAV）
│       └── sfx/                # 音效（6个WAV）
├── tests/                      # 测试代码
│   ├── test_audio_manager.py       # 音频单元测试（41个用例）
│   ├── test_audio_integration.py   # 音频集成测试（16个用例）
│   ├── test_audio_special.py       # 音频专项测试（59个用例）
│   ├── test_game_engine.py         # 游戏引擎测试
│   ├── test_user_manager.py        # 用户管理测试
│   ├── test_score_manager.py       # 积分管理测试
│   ├── e2e_verify.py               # 端到端验证脚本
│   └── ...
├── docs/                       # 项目文档
│   ├── srs/                    # 需求规格
│   ├── ad/                     # 架构设计
│   ├── dd/                     # 详细设计
│   ├── audio/                  # 音频评审文档
│   └── standards/              # 开发规范
├── multi_agents/               # 多智能体协作模块
├── requirements.txt            # 依赖清单
├── LICENSE                     # MIT许可证
└── .gitignore                  # Git忽略配置
```

## 安装与运行

### 环境要求

- Python 3.11+
- pip

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/generaljxw/rock-paper-scissors-game.git
cd RockPaperScissors

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行游戏
python -m src.main
```

### 打包为 EXE（onedir模式）

```bash
pip install pyinstaller
pyinstaller "猜拳小游戏.spec" --noconfirm
```

打包产物位于 `dist/猜拳小游戏/` 目录，双击 `猜拳小游戏.exe` 即可运行，无需安装Python环境。

> **注意**：打包后数据库文件自动存储在 `%APPDATA%\RockPaperScissors\` 目录，确保用户数据持久化。

## 运行测试

```bash
# 运行全部测试
python -m pytest tests/ -v

# 仅运行音频模块测试
python -m pytest tests/test_audio_manager.py tests/test_audio_integration.py tests/test_audio_special.py -v

# 运行端到端验证
python tests/e2e_verify.py
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: 描述你的更改"`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码风格
- 变量、函数、类名使用英文
- 每个函数、方法前添加注释
- 复杂代码片段前添加说明注释
- 提交信息遵循语义化版本规范（feat/fix/docs/refactor/test）

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

Copyright (c) 2026 RockPaperScissors
