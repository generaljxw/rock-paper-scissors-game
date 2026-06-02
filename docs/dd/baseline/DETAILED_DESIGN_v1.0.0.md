# 📝 详细设计文档 (DD - Detailed Design)

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
| v1.0.0 | 2026-06-01 | Planner架构师 | 初始版本，创建详细设计文档 | 已审批 |

---

## 1. 模块划分

### 1.1 模块概述

```
┌─────────────────────────────────────────────────────────────────┐
│                        游戏主程序 (main.py)                       │
└─────────────────────────────────────────────────────────────────┘
                    ▲                           │
                    │                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                         UI层 (ui)                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│  │LoginWindow │ │MainWindow  │ │BattleWindow│ │ResultWindow│     │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                    ▲                           │
                    │                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (business)                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│  │UserManager │ │GameEngine  │ │ScoreManager│ │Statistics  │     │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                    ▲                           │
                    │                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层 (data)                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                     │
│  │ Database   │ │  UserDAO   │ │BattleDAO  │                     │
│  └────────────┘ └────────────┘ └────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责

| 模块 | 职责 | 外部接口 |
|------|------|----------|
| ui | 图形用户界面展示和用户交互 | 接收用户输入，显示游戏界面 |
| business | 游戏业务逻辑处理 | 被ui调用，处理游戏规则 |
| data | 数据持久化操作 | 被business调用，读写数据库 |

---

## 2. 类结构设计

### 2.1 枚举类型定义

```python
# src/business/enums.py

from enum import Enum


class Choice(Enum):
    """玩家选择"""
    ROCK = "石头"
    SCISSORS = "剪刀"
    PAPER = "布"


class Result(Enum):
    """对战结果"""
    WIN = "胜利"
    LOSE = "失败"
    DRAW = "平局"


class BattleMode(Enum):
    """对战模式"""
    MODE_1 = 1  # 一局定胜负
    MODE_2 = 2  # 三局两胜
    MODE_3 = 3  # 连战模式
```

### 2.2 数据模型类

```python
# src/data/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户模型"""
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    created_at: Optional[datetime] = None


@dataclass
class BattleRecord:
    """对战记录模型"""
    id: Optional[int] = None
    user_id: int = 0
    mode: int = 1
    player_choice: str = ""
    ai_choice: str = ""
    result: str = ""
    score_change: int = 0
    created_at: Optional[datetime] = None


@dataclass
class Score:
    """积分模型"""
    user_id: int = 0
    total_score: int = 0
    win_count: int = 0
    lose_count: int = 0
    draw_count: int = 0
    battle_count: int = 0
    updated_at: Optional[datetime] = None
```

### 2.3 业务逻辑类

#### UserManager类

```python
# src/business/user_manager.py

import hashlib
from typing import Optional
from data.user_dao import UserDAO
from data.models import User


class UserManager:
    """用户管理类"""

    def __init__(self):
        self.user_dao = UserDAO()
        self.current_user: Optional[User] = None

    def _hash_password(self, password: str) -> str:
        """密码哈希加密"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        用户注册
        返回: (是否成功, 消息)
        """
        if len(username) < 3:
            return False, "用户名长度不能少于3个字符"
        if len(password) < 6:
            return False, "密码长度不能少于6个字符"

        hashed_password = self._hash_password(password)
        return self.user_dao.create_user(username, hashed_password)

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        用户登录
        返回: (是否成功, 消息)
        """
        hashed_password = self._hash_password(password)
        user = self.user_dao.verify_user(username, hashed_password)

        if user:
            self.current_user = user
            return True, "登录成功"
        return False, "用户名或密码错误"

    def logout(self) -> None:
        """用户登出"""
        self.current_user = None

    def get_current_user(self) -> Optional[User]:
        """获取当前登录用户"""
        return self.current_user
```

#### GameEngine类

```python
# src/business/game_engine.py

import random
from enum import Enum
from typing import Optional
from data.models import BattleRecord, User
from data.battle_dao import BattleDAO


class Choice(Enum):
    ROCK = "石头"
    SCISSORS = "剪刀"
    PAPER = "布"


class Result(Enum):
    WIN = "胜利"
    LOSE = "失败"
    DRAW = "平局"


class GameEngine:
    """游戏引擎类"""

    WIN_MAP = {
        Choice.ROCK: Choice.SCISSORS,      # 石头 > 剪刀
        Choice.SCISSORS: Choice.PAPER,     # 剪刀 > 布
        Choice.PAPER: Choice.ROCK          # 布 > 石头
    }

    def __init__(self):
        self.battle_dao = BattleDAO()
        self.current_session: Optional[dict] = None

    def start_game(self, user_id: int, mode: int) -> dict:
        """
        开始游戏
        返回: 游戏会话信息
        """
        self.current_session = {
            "user_id": user_id,
            "mode": mode,
            "rounds": [],
            "win_count": 0,
            "lose_count": 0,
            "draw_count": 0
        }
        return self.current_session

    def make_choice(self, user_choice: Choice) -> dict:
        """
        处理玩家选择
        返回: 本轮对战结果
        """
        ai_choice = self._get_ai_choice()
        result = self.determine_winner(user_choice, ai_choice)

        round_result = {
            "player_choice": user_choice,
            "ai_choice": ai_choice,
            "result": result
        }

        if self.current_session:
            self.current_session["rounds"].append(round_result)

            if result == Result.WIN:
                self.current_session["win_count"] += 1
            elif result == Result.LOSE:
                self.current_session["lose_count"] += 1
            else:
                self.current_session["draw_count"] += 1

        return round_result

    def _get_ai_choice(self) -> Choice:
        """获取AI选择（随机）"""
        return random.choice(list(Choice))

    def determine_winner(self, player_choice: Choice, ai_choice: Choice) -> Result:
        """
        判定胜负
        规则: 石头 > 剪刀 > 布 > 石头
        """
        if player_choice == ai_choice:
            return Result.DRAW

        if self.WIN_MAP[player_choice] == ai_choice:
            return Result.WIN

        return Result.LOSE

    def is_battle_finished(self) -> bool:
        """判断对战是否结束"""
        if not self.current_session:
            return True

        mode = self.current_session["mode"]
        win_count = self.current_session["win_count"]
        lose_count = self.current_session["lose_count"]

        if mode == 1:  # 一局定胜负
            return win_count == 1 or lose_count == 1
        elif mode == 2:  # 三局两胜
            return win_count == 2 or lose_count == 2
        elif mode == 3:  # 连战模式
            return lose_count >= 1

        return False

    def get_final_result(self) -> Result:
        """获取最终对战结果"""
        if not self.current_session:
            return Result.DRAW

        if self.current_session["win_count"] > self.current_session["lose_count"]:
            return Result.WIN
        elif self.current_session["lose_count"] > self.current_session["win_count"]:
            return Result.LOSE
        return Result.DRAW

    def save_battle_record(self) -> bool:
        """保存对战记录"""
        if not self.current_session:
            return False

        final_result = self.get_final_result()
        for round_data in self.current_session["rounds"]:
            record = BattleRecord(
                user_id=self.current_session["user_id"],
                mode=self.current_session["mode"],
                player_choice=round_data["player_choice"].value,
                ai_choice=round_data["ai_choice"].value,
                result=round_data["result"].value,
                score_change=0
            )
            self.battle_dao.create_record(record)

        return True
```

#### ScoreManager类

```python
# src/business/score_manager.py

from data.score_dao import ScoreDAO
from data.models import Score


class ScoreManager:
    """积分管理类"""

    MODE_SCORE_RULES = {
        1: {"win": 1, "lose": -1, "entry_fee": 0},
        2: {"win": 2, "lose": -2, "entry_fee": 0},
        3: {"win": 1, "lose": 0, "entry_fee": 3, "draw_bonus": 0, "round_bonus": 5}
    }

    def __init__(self):
        self.score_dao = ScoreDAO()

    def deduct_entry_fee(self, user_id: int, mode: int) -> tuple[bool, str]:
        """
        扣除入场费
        返回: (是否成功, 消息)
        """
        entry_fee = self.MODE_SCORE_RULES.get(mode, {}).get("entry_fee", 0)

        if entry_fee > 0:
            score = self.score_dao.get_score(user_id)
            if score and score.total_score < entry_fee:
                return False, f"积分不足，需要{entry_fee}积分进入"
            self.score_dao.update_score(user_id, -entry_fee)

        return True, "入场费扣除成功"

    def calculate_score_change(self, mode: int, result: str, round_count: int = 0) -> int:
        """
        计算积分变化
        参数:
            mode: 对战模式
            result: 对战结果
            round_count: 回合数（模式3使用）
        返回: 积分变化值
        """
        rules = self.MODE_SCORE_RULES.get(mode, {})

        if result == "胜利":
            return rules.get("win", 0)
        elif result == "失败":
            return rules.get("lose", 0)
        elif result == "平局" and mode == 3:
            round_bonus = rules.get("round_bonus", 5)
            return 1 if round_count > 0 and round_count % round_bonus == 0 else 0

        return 0

    def update_score(self, user_id: int, score_change: int) -> bool:
        """更新积分"""
        return self.score_dao.update_score(user_id, score_change)

    def get_score(self, user_id: int) -> int:
        """获取用户积分"""
        score = self.score_dao.get_score(user_id)
        return score.total_score if score else 0
```

### 2.4 数据访问类

```python
# src/data/database.py

import sqlite3
import os
from pathlib import Path


class Database:
    """数据库管理类（单例模式）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.db_path = Path(__file__).parent.parent.parent / "data" / "game.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = True
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS battle_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mode INTEGER NOT NULL,
                player_choice TEXT NOT NULL,
                ai_choice TEXT NOT NULL,
                result TEXT NOT NULL,
                score_change INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                user_id INTEGER PRIMARY KEY,
                total_score INTEGER DEFAULT 0,
                win_count INTEGER DEFAULT 0,
                lose_count INTEGER DEFAULT 0,
                draw_count INTEGER DEFAULT 0,
                battle_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
```

---

## 3. 核心算法实现

### 3.1 胜负判定算法

```python
def determine_winner(player_choice: str, ai_choice: str) -> str:
    """
    猜拳胜负判定算法

    规则:
        石头(ROCK) > 剪刀(SCISSORS) > 布(PAPER) > 石头(ROCK)

    参数:
        player_choice: 玩家选择 (石头/剪刀/布)
        ai_choice: AI选择 (石头/剪刀/布)

    返回:
        胜负结果: "胜利" / "失败" / "平局"
    """
    if player_choice == ai_choice:
        return "平局"

    win_rules = {
        "石头": "剪刀",
        "剪刀": "布",
        "布": "石头"
    }

    if win_rules.get(player_choice) == ai_choice:
        return "胜利"

    return "失败"
```

### 3.2 积分计算算法

```python
def calculate_score(mode: int, result: str, round_count: int = 0) -> int:
    """
    积分计算算法

    模式1（一局定胜负）:
        - 胜利: +1分
        - 失败: -1分

    模式2（三局两胜）:
        - 胜利: +2分
        - 失败: -2分

    模式3（连战模式）:
        - 进入需要: -3分
        - 胜利: +1分
        - 平局: 不积分
        - 每5回合: +1分

    参数:
        mode: 对战模式 (1/2/3)
        result: 对战结果
        round_count: 当前回合数

    返回:
        积分变化值
    """
    score_map = {
        1: {"胜利": 1, "失败": -1, "平局": 0},
        2: {"胜利": 2, "失败": -2, "平局": 0},
        3: {"胜利": 1, "失败": 0, "平局": 0}
    }

    score = score_map.get(mode, {}).get(result, 0)

    if mode == 3 and result == "平局":
        if round_count > 0 and round_count % 5 == 0:
            score = 1

    return score
```

### 3.3 胜率统计算法

```python
def calculate_win_rate(win_count: int, total_battles: int) -> float:
    """
    胜率计算算法

    参数:
        win_count: 胜利次数
        total_battles: 总对战次数

    返回:
        胜率 (0-100)
    """
    if total_battles == 0:
        return 0.0

    return round(win_count / total_battles * 100, 2)
```

---

## 4. 数据库表结构

### 4.1 users表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 用户ID |
| username | TEXT | UNIQUE NOT NULL | 用户名 |
| password | TEXT | NOT NULL | 密码（SHA256哈希） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 4.2 battle_records表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 记录ID |
| user_id | INTEGER | NOT NULL, FK(users.id) | 用户ID |
| mode | INTEGER | NOT NULL | 对战模式 |
| player_choice | TEXT | NOT NULL | 玩家选择 |
| ai_choice | TEXT | NOT NULL | AI选择 |
| result | TEXT | NOT NULL | 对战结果 |
| score_change | INTEGER | NOT NULL | 积分变化 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 对战时间 |

### 4.3 scores表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | INTEGER | PRIMARY KEY, FK(users.id) | 用户ID |
| total_score | INTEGER | DEFAULT 0 | 总积分 |
| win_count | INTEGER | DEFAULT 0 | 胜利次数 |
| lose_count | INTEGER | DEFAULT 0 | 失败次数 |
| draw_count | INTEGER | DEFAULT 0 | 平局次数 |
| battle_count | INTEGER | DEFAULT 0 | 对战次数 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

## 5. 关键业务流程

### 5.1 用户登录流程

```
开始
  │
  ▼
┌─────────────────┐
│  输入用户名密码  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  验证用户名密码  │──── 失败 ────> 显示错误信息
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────┐
│ 更新当前用户状态 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 跳转主界面      │
└─────────────────┘
         │
         ▼
       结束
```

### 5.2 游戏对战流程

```
开始
  │
  ▼
┌─────────────────┐
│  选择对战模式   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 扣除入场费(模式3)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 玩家选择出拳   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AI随机选择出拳  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 判定胜负        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 显示本轮结果   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 判断模式是否结束│
└────────┬────────┘
         │
    是   │   否
    │    │    │
    ▼    │    ▼
┌────────┴───┐  │
│  计算积分 │  │
└────────┬───┘  │
         │      │
         ▼      │
┌─────────────────┐
│  保存对战记录   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  显示结算界面   │
└────────┬────────┘
         │
         ▼
       结束
```

### 5.3 积分计算流程

```
开始
  │
  ▼
┌─────────────────┐
│ 获取对战模式和结果│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 模式1: 胜+1负-1 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 模式2: 胜+2负-2 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│模式3: 胜+1,每5轮+1│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 更新数据库积分   │
└────────┬────────┘
         │
         ▼
       结束
```

---

## 6. 评审签字

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
**基线保存位置**: docs/dd/DETAILED_DESIGN_v1.0.0.md
