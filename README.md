# RockPaperScissors - 猜拳小游戏

一款面向儿童的猜拳小游戏，基于 Python 3.11 + PyQt6 开发，融合卡通元素和积分系统，支持多种对战模式。

## 功能特性

- **用户系统**：注册/登录，密码 PBKDF2 加密存储
- **三种对战模式**：
  - 一局定胜负：不耗积分，胜+1/负-1
  - 三局两胜：不耗积分，胜+2/负-2
  - 连战模式：消耗3积分入场，连续胜利3次额外+5分
- **积分系统**：完整的积分计算和入场费机制
- **战绩查询**：每轮对战汇总记录，含对战时间、模式、结果、积分变化
- **胜率统计**：实时计算并展示玩家胜率

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| GUI框架 | PyQt6 |
| 数据库 | SQLite |
| 密码加密 | PBKDF2-HMAC-SHA256 |
| 打包工具 | PyInstaller |

## 项目结构

```
RockPaperScissors/
├── src/                        # 源代码
│   ├── main.py                 # 应用入口
│   ├── business/               # 业务逻辑层
│   │   ├── game_engine.py      # 游戏引擎
│   │   ├── score_manager.py    # 积分管理
│   │   ├── statistics.py       # 统计分析
│   │   ├── user_manager.py     # 用户管理
│   │   └── enums.py            # 枚举定义
│   ├── data/                   # 数据访问层
│   │   ├── database.py         # 数据库管理
│   │   ├── battle_dao.py       # 对战记录DAO
│   │   ├── score_dao.py        # 积分DAO
│   │   ├── user_dao.py         # 用户DAO
│   │   └── models.py           # 数据模型
│   ├── ui/                     # UI界面层
│   │   ├── login_window.py     # 登录窗口
│   │   ├── main_window.py      # 主窗口
│   │   ├── battle_window.py    # 对战窗口
│   │   └── history_window.py   # 战绩窗口
│   └── config/                 # 配置模块
│       └── settings.py         # 应用配置
├── tests/                      # 测试代码
├── docs/                       # 项目文档
├── multi_agents/               # 多智能体协作模块
├── requirements.txt            # 依赖清单
└── .gitignore                  # Git忽略配置
```

## 安装与运行

### 环境要求

- Python 3.11+
- pip

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/RockPaperScissors.git
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

### 打包为 EXE

```bash
pip install pyinstaller
pyinstaller RockPaperScissors.spec --noconfirm
```

打包产物位于 `dist/RockPaperScissors/` 目录。

## 运行测试

```bash
# 运行单元测试
python -m pytest tests/ -v

# 运行E2E验证
python tests/e2e_verify.py
```

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
