# 📐 架构设计文档 (AD - Architecture Design)

**项目**: 儿童猜拳小游戏
**版本**: v1.0.0
**日期**: 2026-06-01
**状态**: 基线版本
**作者**: Planner架构师
**审批人**: 待确认

---

## 📋 版本控制记录

| 版本号 | 修订日期 | 修订人 | 修订内容摘要 | 审批状态 |
|--------|----------|--------|--------------|----------|
| v1.0.0 | 2026-06-01 | Planner架构师 | 初始版本，创建架构设计文档 | 已审批 |

---

## 1. 系统概述

### 1.1 项目背景
为10岁以下儿童开发一款有趣的猜拳游戏，融合卡通元素和社交属性，支持人机对战和玩家间对战，采用Python语言开发，支持免安装运行。

### 1.2 技术选型

| 技术类别 | 选型方案 | 版本 | 说明 |
|----------|----------|------|------|
| **编程语言** | Python | 3.11.x | 推荐3.11.9，LTS版本 |
| **GUI框架** | PyQt6 | 6.7.0+ | 跨平台GUI框架 |
| **数据库** | SQLite | 3.x | Python标准库，无需额外安装 |
| **打包工具** | PyInstaller | 6.5.0+ | 生成免安装exe |
| **测试框架** | pytest | 8.1.1+ | 单元测试框架 |
| **日志框架** | loguru | 0.7.2+ | 日志记录 |

### 1.3 技术选型理由

#### Python 3.11
- **广泛的兼容性**: 支持Windows、macOS、Linux
- **长期支持**: Python 3.11是成熟版本，社区活跃
- **游戏库支持**: PyQt6、pygame等游戏开发库支持良好
- **性能提升**: 3.11版本引入性能优化

#### PyQt6
- **跨平台能力**: 同一代码可运行在Windows、macOS、Linux
- **丰富的UI组件**: 提供完整的GUI组件库
- **信号/槽机制**: 良好的事件处理机制
- **社区支持**: 文档完善，社区活跃

#### SQLite
- **零配置**: 无需安装数据库服务器
- **单文件存储**: 便于数据备份和迁移
- **性能足够**: 对于单机游戏而言性能充足

---

## 2. 系统架构设计

### 2.1 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        GUI 层 (UI Layer)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 登录窗口  │ │ 主界面   │ │ 对战界面  │ │ 结算界面  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Layer)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 用户管理  │ │ 游戏引擎  │ │ 积分系统  │ │ 统计模块  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data Layer)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │ 用户数据  │ │ 对战记录  │ │ 积分数据  │                    │
│  └──────────┘ └──────────┘ └──────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 GUI层组件

| 组件名称 | 职责 | 依赖关系 |
|----------|------|----------|
| LoginWindow | 用户登录界面 | 依赖UserManager |
| MainWindow | 游戏主界面 | 依赖GameEngine |
| BattleWindow | 对战界面 | 依赖GameEngine |
| ResultWindow | 结算界面 | 依赖ScoreManager |
| HistoryWindow | 历史记录界面 | 依赖DataManager |

#### 2.2.2 业务逻辑层组件

| 组件名称 | 职责 | 公共接口 |
|----------|------|----------|
| UserManager | 用户管理 | login(), logout(), register(), get_current_user() |
| GameEngine | 游戏引擎 | start_game(), make_choice(), determine_winner() |
| ScoreManager | 积分管理 | update_score(), get_score(), deduct_entry_fee() |
| BattleModeManager | 对战模式管理 | select_mode(), calculate_battle_result() |
| StatisticsManager | 统计分析 | record_battle(), get_win_rate(), get_statistics() |

#### 2.2.3 数据层组件

| 组件名称 | 职责 | 数据表 |
|----------|------|--------|
| UserDataManager | 用户数据管理 | users |
| BattleRecordManager | 对战记录管理 | battle_records |
| ScoreDataManager | 积分数据管理 | scores |

---

## 3. 接口定义规范

### 3.1 用户管理接口

```python
class IUserManager:
    def login(self, username: str, password: str) -> bool:
        """用户登录"""

    def logout(self) -> None:
        """用户登出"""

    def register(self, username: str, password: str) -> bool:
        """用户注册"""

    def get_current_user(self) -> Optional[User]:
        """获取当前登录用户"""
```

### 3.2 游戏引擎接口

```python
class IGameEngine:
    def start_game(self, mode: BattleMode, user_id: int) -> GameSession:
        """开始游戏"""

    def make_choice(self, session_id: int, choice: Choice) -> RoundResult:
        """玩家做出选择"""

    def get_ai_choice(self, session_id: int) -> Choice:
        """获取AI选择"""

    def determine_winner(self, player_choice: Choice, ai_choice: Choice) -> Result:
        """判定胜负"""
```

### 3.3 积分管理接口

```python
class IScoreManager:
    def update_score(self, user_id: int, score_change: int) -> bool:
        """更新积分"""

    def get_score(self, user_id: int) -> int:
        """获取积分"""

    def deduct_entry_fee(self, user_id: int, fee: int) -> bool:
        """扣除入场费"""

    def add_bonus(self, user_id: int, bonus: int) -> bool:
        """添加奖励"""
```

---

## 4. 非功能性需求设计

### 4.1 性能需求

| 指标 | 要求 | 说明 |
|------|------|------|
| 启动时间 | ≤ 3秒 | 从点击exe到显示主界面 |
| 响应时间 | ≤ 100ms | 用户操作到界面反馈 |
| 内存占用 | ≤ 200MB | 正常运行状态 |

### 4.2 安全性需求

| 需求项 | 设计措施 |
|--------|----------|
| 用户认证 | 密码加密存储（SHA256） |
| 数据隔离 | 用户只能访问自己的数据 |
| 输入验证 | 所有用户输入进行验证 |

### 4.3 可扩展性设计

| 扩展点 | 设计方案 |
|--------|----------|
| 新增对战模式 | 策略模式实现 |
| 新增AI难度 | 工厂模式创建不同AI |
| 网络对战 | 预留网络接口层 |

### 4.4 可维护性设计

| 设计原则 | 具体措施 |
|----------|----------|
| 模块化 | 分层架构，模块间低耦合 |
| 命名规范 | 遵循PEP8命名规范 |
| 代码注释 | 关键逻辑添加注释 |
| 日志记录 | 使用loguru记录运行日志 |

---

## 5. 数据库设计

### 5.1 ER图

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   users     │       │  battle_records │       │   scores    │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ id (PK)     │──────<│ user_id (FK)    │       │ user_id(FK) │
│ username    │       │ id (PK)         │       │ total_score │
│ password    │       │ mode            │       │ win_count   │
│ created_at  │       │ result          │       │ lose_count  │
└─────────────┘       │ score_change    │       │ draw_count  │
                      │ created_at      │       │ battle_count│
                      └─────────────────┘       └─────────────┘
```

### 5.2 数据表结构

#### users表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### battle_records表
```sql
CREATE TABLE battle_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mode INTEGER NOT NULL,
    player_choice TEXT NOT NULL,
    ai_choice TEXT NOT NULL,
    result TEXT NOT NULL,
    score_change INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### scores表
```sql
CREATE TABLE scores (
    user_id INTEGER PRIMARY KEY,
    total_score INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    lose_count INTEGER DEFAULT 0,
    draw_count INTEGER DEFAULT 0,
    battle_count INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 6. 目录结构设计

```
RockPaperScissors/
├── src/                          # 源代码目录
│   ├── main.py                  # 程序入口
│   ├── __init__.py
│   ├── ui/                      # GUI层
│   │   ├── __init__.py
│   │   ├── login_window.py     # 登录窗口
│   │   ├── main_window.py      # 主窗口
│   │   ├── battle_window.py    # 对战窗口
│   │   ├── result_window.py    # 结算窗口
│   │   └── widgets/            # 自定义控件
│   │       └── __init__.py
│   ├── business/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_manager.py     # 用户管理
│   │   ├── game_engine.py      # 游戏引擎
│   │   ├── score_manager.py    # 积分管理
│   │   └── statistics.py       # 统计分析
│   ├── data/                   # 数据层
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库管理
│   │   ├── user_dao.py         # 用户数据访问
│   │   ├── battle_dao.py       # 对战记录访问
│   │   └── score_dao.py        # 积分数据访问
│   └── config/                 # 配置目录
│       ├── __init__.py
│       └── settings.py         # 配置项
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── test_game_engine.py
│   ├── test_score_manager.py
│   └── test_user_manager.py
├── docs/                        # 文档目录
│   ├── ad/                     # 架构设计文档
│   ├── dd/                     # 详细设计文档
│   └── manuals/                # 用户手册
├── assets/                      # 资源目录
│   ├── images/                 # 图片资源
│   ├── sounds/                 # 音效资源
│   └── fonts/                  # 字体资源
├── requirements.txt             # 依赖清单
├── setup.bat                   # Windows初始化脚本
├── setup.sh                    # Linux/macOS初始化脚本
└── README.md                   # 项目说明
```

---

## 7. 评审签字

| 角色 | 姓名 | 日期 | 签字 |
|------|------|------|------|
| 项目负责人 |  |  |  |
| Planner架构师 | Planner | 2026-06-01 | ✓ |
| Coder开发工程师 |  |  |  |
| Tester测试工程师 |  |  |  |
| Reviewer代码审查 |  |  |  |

---

**文档状态**: ✅ 已审批为基线版本
**基线版本号**: v1.0.0
**基线创建日期**: 2026-06-01
**基线保存位置**: docs/ad/ARCHITECTURE_DESIGN_v1.0.0.md
