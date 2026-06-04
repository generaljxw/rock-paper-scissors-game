# 📝 详细设计文档 (DD - Detailed Design)

**项目**: 儿童猜拳小游戏
**版本**: v1.2.0
**日期**: 2026-06-03
**状态**: 待审核
**作者**: Planner架构师
**审批人**: 待确认

---

## 📋 版本控制记录

| 版本号 | 修订日期 | 修订人 | 修订内容摘要 | 审批状态 |
|--------|----------|--------|--------------|----------|
| v1.0.0 | 2026-06-01 | Planner架构师 | 初始版本，创建详细设计文档 | 已审批 |
| v1.1.0 | 2026-06-01 | Planner架构师 | 更新积分系统规则（模式3连续胜利加分）和对战模式2规则（3局2胜必须分出胜负） | 已审批 |
| v1.2.0 | 2026-06-03 | Coder开发工程师 | 新增音频管理模块（AudioManager）详细设计，包含模块划分、类结构、接口定义、数据结构、业务流程及技术实现方案 | 待审批 |

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
│                     音频管理层 (audio)                            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ AudioManager（BGM管理 + SFX管理 + Ducking机制）      │       │
│  └──────────────────────────────────────────────────────┘       │
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
| audio | 音频管理（背景音乐+音效+Ducking） | 被ui调用，控制音乐和音效播放 |
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
        total_rounds = self.current_session.get("total_rounds", 0)
        consecutive_wins = self.current_session.get("consecutive_wins", 0)

        if mode == 1:  # 一局定胜负
            return win_count >= 1 or lose_count >= 1
        elif mode == 2:  # 三局两胜
            # 必须分出胜负，每局平局则继续出拳；前两局同一选手获胜则无需第三局
            return win_count >= 2 or lose_count >= 2 or total_rounds >= 3
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
        3: {"win": 1, "lose": 0, "entry_fee": 3, "consecutive_win_bonus": 5, "consecutive_win_threshold": 3, "round_bonus": 5}
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

    def calculate_score_change(self, mode: int, result: str, round_count: int = 0, consecutive_wins: int = 0) -> int:
        """
        计算积分变化
        参数:
            mode: 对战模式
            result: 对战结果
            round_count: 回合数（模式3使用）
            consecutive_wins: 连续胜利次数（模式3使用）
        返回: 积分变化值
        """
        rules = self.MODE_SCORE_RULES.get(mode, {})

        if mode == 3:
            # 模式3：连续胜利超过3次奖励+5分
            threshold = rules.get("consecutive_win_threshold", 3)
            if consecutive_wins > threshold:
                return rules.get("consecutive_win_bonus", 5)
            # 每累计5次出拳额外+1分
            if round_count > 0 and round_count % rules.get("round_bonus", 5) == 0:
                return 1
            return 0

        if result == "胜利":
            return rules.get("win", 0)
        elif result == "失败":
            return rules.get("lose", 0)

        return 0

    def update_score(self, user_id: int, score_change: int) -> bool:
        """更新积分"""
        return self.score_dao.update_score(user_id, score_change)

    def get_score(self, user_id: int) -> int:
        """获取用户积分"""
        score = self.score_dao.get_score(user_id)
        return score.total_score if score else 0
```

### 2.4 音频管理类

#### AudioManager类

```python
# src/audio/audio_manager.py

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QSoundEffect
from PyQt6.QtCore import QUrl, QObject
from pathlib import Path
from typing import Optional


class AudioManager(QObject):
    """
    音频管理器类（单例模式）
    负责管理游戏所有背景音乐和音效的播放控制
    底层基于QMediaPlayer（BGM）和QSoundEffect（SFX）实现
    """

    _instance: Optional['AudioManager'] = None

    # BGM场景映射表
    BGM_MAP = {
        "login": "bgm/login.wav",
        "mode_select": "bgm/mode_select.wav",
        "battle_1": "bgm/battle_mode1.wav",
        "battle_2": "bgm/battle_mode2.wav",
        "battle_3": "bgm/battle_mode3.wav",
        "settlement_normal_win": "bgm/settlement_normal_win.wav",
        "settlement_normal_lose": "bgm/settlement_normal_lose.wav",
        "survival_win": "bgm/survival_win.wav",
        "survival_lose": "bgm/survival_lose.wav",
    }

    # SFX类型映射表
    SFX_MAP = {
        "rock": "sfx/rock.wav",
        "scissors": "sfx/scissors.wav",
        "paper": "sfx/paper.wav",
        "win": "sfx/win.wav",
        "lose": "sfx/lose.wav",
        "draw": "sfx/draw.wav",
    }

    # Ducking参数
    DUCK_VOLUME = 0.2       # Ducking时BGM音量（原音量的20%）
    NORMAL_VOLUME = 0.7     # 正常BGM音量（70%）
    SFX_VOLUME = 1.0        # SFX音量（100%）

    def __new__(cls):
        """单例模式：确保全局只有一个AudioManager实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化音频管理器"""
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._current_bgm_key: Optional[str] = None
        self._is_ducking = False
        self._sounds_dir: Optional[Path] = None
        self._bgm_player: Optional[QMediaPlayer] = None
        self._bgm_output: Optional[QAudioOutput] = None
        self._sfx_cache: dict[str, QSoundEffect] = {}
        self._init_players()

    def _init_players(self):
        """初始化BGM播放器和SFX缓存"""
        # BGM播放器
        self._bgm_player = QMediaPlayer()
        self._bgm_output = QAudioOutput()
        self._bgm_player.setAudioOutput(self._bgm_output)
        self._bgm_output.setVolume(self.NORMAL_VOLUME)

        # BGM循环播放
        self._bgm_player.mediaStatusChanged.connect(self._on_bgm_status_changed)

        # 预加载SFX
        self._preload_sfx()

    def _on_bgm_status_changed(self, status):
        """BGM播放状态变化回调，实现自动循环"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._bgm_player.setPosition(0)
            self._bgm_player.play()

    def _preload_sfx(self):
        """预加载所有SFX到缓存"""
        if not self._sounds_dir:
            return
        for sfx_key, sfx_path in self.SFX_MAP.items():
            full_path = self._sounds_dir / sfx_path
            if full_path.exists():
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(str(full_path)))
                effect.setVolume(self.SFX_VOLUME)
                self._sfx_cache[sfx_key] = effect

    def set_sounds_dir(self, sounds_dir: str):
        """设置音频资源根目录"""
        self._sounds_dir = Path(sounds_dir)
        self._preload_sfx()

    def play_bgm(self, scene: str, mode: int = None, result: str = None) -> None:
        """
        播放背景音乐
        参数:
            scene: 场景标识（login/mode_select/battle/settlement）
            mode: 对战模式（1/2/3），仅battle场景使用
            result: 结算结果（win/lose），仅settlement场景使用
        """
        bgm_key = self._resolve_bgm_key(scene, mode, result)
        if bgm_key is None:
            return
        if bgm_key == self._current_bgm_key:
            return  # 同一首BGM，不重复播放
        self._play_bgm_by_key(bgm_key)

    def stop_bgm(self) -> None:
        """停止当前背景音乐"""
        if self._bgm_player:
            self._bgm_player.stop()
        self._current_bgm_key = None

    def switch_bgm(self, scene: str, mode: int = None, result: str = None) -> None:
        """
        无缝切换背景音乐
        停止当前音乐并播放目标场景音乐
        """
        self.stop_bgm()
        self.play_bgm(scene, mode, result)

    def play_sfx(self, sfx_type: str) -> None:
        """
        播放音效
        参数:
            sfx_type: 音效类型（rock/scissors/paper/win/lose/draw）
        """
        effect = self._sfx_cache.get(sfx_type)
        if effect:
            effect.play()

    def duck_bgm(self) -> None:
        """压低背景音乐音量（Ducking机制）
        出拳时调用，确保音效清晰可闻
        """
        if not self._is_ducking and self._bgm_output:
            self._bgm_output.setVolume(self.DUCK_VOLUME)
            self._is_ducking = True

    def restore_bgm(self) -> None:
        """恢复背景音乐音量
        音效播放完毕后调用
        """
        if self._is_ducking and self._bgm_output:
            self._bgm_output.setVolume(self.NORMAL_VOLUME)
            self._is_ducking = False

    def stop_all(self) -> None:
        """停止所有音乐和音效（应用退出时调用）"""
        self.stop_bgm()
        for effect in self._sfx_cache.values():
            effect.stop()

    def _resolve_bgm_key(self, scene: str, mode: int = None, result: str = None) -> Optional[str]:
        """
        根据场景参数解析BGM资源键
        参数:
            scene: 场景标识
            mode: 对战模式
            result: 结算结果
        返回:
            BGM_MAP中的键名，或None
        """
        if scene == "login":
            return "login"
        elif scene == "mode_select":
            return "mode_select"
        elif scene == "battle":
            if mode in (1, 2, 3):
                return f"battle_{mode}"
        elif scene == "settlement":
            if mode == 3:
                return f"survival_{result}" if result in ("win", "lose") else None
            else:
                return f"settlement_normal_{result}" if result in ("win", "lose") else None
        return None

    def _play_bgm_by_key(self, bgm_key: str) -> None:
        """
        根据BGM键名播放音乐
        参数:
            bgm_key: BGM_MAP中的键名
        """
        if not self._sounds_dir:
            return
        bgm_path = self.BGM_MAP.get(bgm_key)
        if bgm_path is None:
            return
        full_path = self._sounds_dir / bgm_path
        if not full_path.exists():
            return
        source = QUrl.fromLocalFile(str(full_path))
        self._bgm_player.setSource(source)
        self._bgm_player.play()
        self._current_bgm_key = bgm_key

    @classmethod
    def reset_instance(cls):
        """重置单例实例（仅用于测试）"""
        if cls._instance:
            cls._instance.stop_all()
        cls._instance = None
```

### 2.5 数据访问类

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

### 5.4 音频管理 - BGM场景切换流程

```
┌──────────────────────────────────────────────────────────────┐
│                    BGM场景切换状态机                           │
│                                                              │
│  ┌─────────┐  登录成功   ┌──────────────┐  开始对战  ┌───────┤
│  │  login  │ ──────────> │ mode_select  │ ──────────>│battle │
│  └─────────┘             └──────────────┘            │ _1/2/3│
│       ▲                       ▲  ▲                   └───┬───┘
│       │                       │  │                       │
│       │ 退出登录              │  │ 返回主界面            │对战结束
│       │                       │  │                       ▼
│       │                       │  │              ┌────────────────┐
│       │                       │  │              │   settlement   │
│       │                       │  │              │ normal_win/lose│
│       │                       │  │              │ survival_win   │
│       │                       │  │              │ /survival_lose │
│       │                       │  │              └───────┬────────┘
│       │                       │  │                      │
│       │                       │  │  返回主界面          │再来一局
│       │                       │  └──────────────────────┤
│       │                       │                         │
│       └───────────────────────┘                         ▼
│                                               重新进入battle
└──────────────────────────────────────────────────────────────┘
```

**场景切换规则表:**

| 当前场景 | 触发事件 | 目标场景 | BGM切换方式 |
|----------|----------|----------|-------------|
| login | 登录成功 | mode_select | switch_bgm("mode_select") |
| login | 登录失败 | login | 不切换，继续循环 |
| mode_select | 开始对战 | battle | switch_bgm("battle", mode=N) |
| mode_select | 退出登录 | login | switch_bgm("login") |
| mode_select | 查看战绩 | mode_select | 不切换，继续循环 |
| battle | 对战结束 | settlement | switch_bgm("settlement", mode=N, result=R) |
| battle | 返回主界面 | mode_select | switch_bgm("mode_select") |
| battle | 出拳 | battle(ducking) | duck_bgm() → play_sfx() → restore_bgm() |
| battle | 再来一局 | battle | switch_bgm("battle", mode=N) 从头播放 |
| settlement | 再来一局 | battle | switch_bgm("battle", mode=N) |
| settlement | 返回主界面 | mode_select | switch_bgm("mode_select") |
| 任意 | 关闭应用 | - | stop_all() |

### 5.5 音频管理 - Ducking机制流程

```
玩家点击出拳按钮
       │
       ▼
┌──────────────────┐
│ duck_bgm()       │  BGM音量: 70% → 20%
│ 压低背景音乐音量  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ play_sfx(type)   │  播放出拳音效(rock/scissors/paper)
│ 播放出拳音效      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 判定胜负结果      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ play_sfx(result) │  播放判定音效(win/lose/draw)
│ 播放判定音效      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ restore_bgm()    │  BGM音量: 20% → 70%
│ 恢复背景音乐音量  │
└────────┬─────────┘
         │
         ▼
   准备下一回合
```

### 5.6 音频管理 - UI层集成调用时序

```
GameMainWindow          LoginWindow          AudioManager
     │                      │                     │
     │  创建LoginWindow     │                     │
     │─────────────────────>│                     │
     │                      │  play_bgm("login")  │
     │                      │────────────────────>│
     │                      │                     │──> 播放login.wav
     │                      │                     │
     │  登录成功            │                     │
     │<─────────────────────│                     │
     │                      │                     │
     │  创建MainWindow      │                     │
     │──────────────────────┼────────────────────>│
     │                      │  switch_bgm         │
     │                      │  ("mode_select")    │
     │                      │                     │──> 停止login.wav
     │                      │                     │──> 播放mode_select.wav
     │                      │                     │
     │  开始对战(mode=1)    │                     │
     │──────────────────────┼────────────────────>│
     │                      │  switch_bgm         │
     │                      │  ("battle",1)       │
     │                      │                     │──> 播放battle_mode1.wav

BattleWindow            AudioManager
     │                      │
     │  玩家点击"石头"      │
     │  duck_bgm()          │
     │─────────────────────>│──> BGM音量 70%→20%
     │  play_sfx("rock")    │
     │─────────────────────>│──> 播放rock.wav
     │  判定结果为"胜利"    │
     │  play_sfx("win")     │
     │─────────────────────>│──> 播放win.wav
     │  restore_bgm()       │
     │─────────────────────>│──> BGM音量 20%→70%
     │                      │
     │  对战结束(mode=1,win)│
     │  switch_bgm          │
     │  ("settlement",1,"win")│
     │─────────────────────>│──> 播放settlement_normal_win.wav
```

---

## 6. 音频管理模块详细设计

### 6.1 模块内部结构

```
src/audio/
├── __init__.py              # 模块初始化，导出AudioManager
└── audio_manager.py         # 音频管理器实现
```

### 6.2 数据结构设计

#### 6.2.1 BGM场景映射表

```python
BGM_MAP = {
    "login":                    "bgm/login.wav",                # 登录界面
    "mode_select":              "bgm/mode_select.wav",          # 模式选择界面
    "battle_1":                 "bgm/battle_mode1.wav",         # 一局定胜负
    "battle_2":                 "bgm/battle_mode2.wav",         # 三局两胜
    "battle_3":                 "bgm/battle_mode3.wav",         # 连战模式
    "settlement_normal_win":    "bgm/settlement_normal_win.wav", # 普通胜利结算
    "settlement_normal_lose":   "bgm/settlement_normal_lose.wav",# 普通失败结算
    "survival_win":             "bgm/survival_win.wav",          # 连战胜利结算
    "survival_lose":            "bgm/survival_lose.wav",         # 连战失败结算
}
```

#### 6.2.2 SFX类型映射表

```python
SFX_MAP = {
    "rock":     "sfx/rock.wav",      # 石头出拳
    "scissors": "sfx/scissors.wav",   # 剪刀出拳
    "paper":    "sfx/paper.wav",      # 布出拳
    "win":      "sfx/win.wav",        # 胜利判定
    "lose":     "sfx/lose.wav",       # 失败判定
    "draw":     "sfx/draw.wav",       # 平局判定
}
```

#### 6.2.3 音频参数配置

```python
# Ducking参数
DUCK_VOLUME = 0.2       # Ducking时BGM音量（原音量的20%）
NORMAL_VOLUME = 0.7     # 正常BGM音量（70%）
SFX_VOLUME = 1.0        # SFX音量（100%）
```

#### 6.2.4 内部状态变量

| 变量名 | 类型 | 说明 |
|--------|------|------|
| _current_bgm_key | Optional[str] | 当前播放的BGM键名，防止重复播放同一首 |
| _is_ducking | bool | 是否处于Ducking状态 |
| _sounds_dir | Optional[Path] | 音频资源根目录路径 |
| _bgm_player | QMediaPlayer | BGM播放器实例 |
| _bgm_output | QAudioOutput | BGM音频输出实例 |
| _sfx_cache | dict[str, QSoundEffect] | SFX预加载缓存 |

### 6.3 接口详细定义

#### 6.3.1 公共接口

| 方法签名 | 说明 | 调用方 |
|----------|------|--------|
| `set_sounds_dir(sounds_dir: str) -> None` | 设置音频资源根目录 | GameMainWindow |
| `play_bgm(scene: str, mode: int = None, result: str = None) -> None` | 播放背景音乐 | UI层各窗口 |
| `stop_bgm() -> None` | 停止当前背景音乐 | AudioManager内部 |
| `switch_bgm(scene: str, mode: int = None, result: str = None) -> None` | 无缝切换背景音乐 | UI层各窗口 |
| `play_sfx(sfx_type: str) -> None` | 播放音效 | BattleWindow |
| `duck_bgm() -> None` | 压低BGM音量 | BattleWindow |
| `restore_bgm() -> None` | 恢复BGM音量 | BattleWindow |
| `stop_all() -> None` | 停止所有音频 | GameMainWindow |

#### 6.3.2 私有方法

| 方法签名 | 说明 |
|----------|------|
| `_init_players() -> None` | 初始化BGM播放器和SFX缓存 |
| `_on_bgm_status_changed(status) -> None` | BGM播放状态回调，实现循环播放 |
| `_preload_sfx() -> None` | 预加载所有SFX到缓存 |
| `_resolve_bgm_key(scene, mode, result) -> Optional[str]` | 根据场景参数解析BGM资源键 |
| `_play_bgm_by_key(bgm_key: str) -> None` | 根据键名播放BGM |

### 6.4 技术实现方案

#### 6.4.1 BGM播放 - QMediaPlayer

**选型理由:**
- QMediaPlayer支持WAV/MP3/OGG等格式
- 内置播放状态管理（Playing/Paused/Stopped）
- 支持音量控制（QAudioOutput），便于实现Ducking
- 支持mediaStatusChanged信号，便于实现循环播放

**循环播放实现:**
```python
# 监听播放状态，播放结束后自动重头播放
self._bgm_player.mediaStatusChanged.connect(self._on_bgm_status_changed)

def _on_bgm_status_changed(self, status):
    if status == QMediaPlayer.MediaStatus.EndOfMedia:
        self._bgm_player.setPosition(0)
        self._bgm_player.play()
```

**音量控制实现:**
```python
# 通过QAudioOutput控制音量
self._bgm_output = QAudioOutput()
self._bgm_player.setAudioOutput(self._bgm_output)
self._bgm_output.setVolume(0.7)  # 0.0 ~ 1.0
```

#### 6.4.2 SFX播放 - QSoundEffect

**选型理由:**
- QSoundEffect专为低延迟音效设计
- 支持WAV格式，播放延迟极低（<50ms）
- 支持同时播放多个音效（与BGM互不干扰）
- 支持预加载，首次播放无延迟

**预加载实现:**
```python
# 在初始化时预加载所有SFX到缓存
def _preload_sfx(self):
    for sfx_key, sfx_path in self.SFX_MAP.items():
        full_path = self._sounds_dir / sfx_path
        if full_path.exists():
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(str(full_path)))
            effect.setVolume(1.0)
            self._sfx_cache[sfx_key] = effect
```

#### 6.4.3 Ducking机制实现

**原理:** 出拳时将BGM音量从0.7压低至0.2，确保SFX清晰可闻；音效播放完毕后恢复至0.7。

```python
def duck_bgm(self):
    """出拳时调用"""
    if not self._is_ducking and self._bgm_output:
        self._bgm_output.setVolume(self.DUCK_VOLUME)  # 0.2
        self._is_ducking = True

def restore_bgm(self):
    """音效播放完毕后调用"""
    if self._is_ducking and self._bgm_output:
        self._bgm_output.setVolume(self.NORMAL_VOLUME)  # 0.7
        self._is_ducking = False
```

**Ducking时序:**
1. 玩家点击出拳 → `duck_bgm()` → BGM音量降至20%
2. `play_sfx("rock")` → 播放出拳音效
3. 判定结果 → `play_sfx("win")` → 播放判定音效
4. `restore_bgm()` → BGM音量恢复至70%

#### 6.4.4 单例模式实现

**理由:** 全局只需一个音频管理器，避免多个BGM播放器同时播放造成混乱。

```python
_instance = None

def __new__(cls):
    if cls._instance is None:
        cls._instance = super().__new__(cls)
        cls._instance._initialized = False
    return cls._instance

def __init__(self):
    if self._initialized:
        return
    # ... 初始化逻辑
    self._initialized = True
```

### 6.5 UI层集成方案

#### 6.5.1 GameMainWindow集成

```python
# src/main.py 修改点
from src.audio.audio_manager import AudioManager
from src.config.settings import Settings

class GameMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化AudioManager
        self.audio_manager = AudioManager()
        self.audio_manager.set_sounds_dir(str(Settings.ASSETS_DIR / "sounds"))
        # ... 其余初始化

    def closeEvent(self, event):
        """应用关闭时停止所有音频"""
        self.audio_manager.stop_all()
        event.accept()
```

#### 6.5.2 LoginWindow集成

```python
# src/ui/login_window.py 修改点
from ..audio.audio_manager import AudioManager

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_manager = AudioManager()
        # 登录界面显示时播放BGM
        self.audio_manager.play_bgm("login")
        # ... 其余初始化

    def _on_login_clicked(self):
        # 登录成功后切换BGM
        if success:
            self.audio_manager.switch_bgm("mode_select")
            self.login_success.emit(user.id, user.username)
```

#### 6.5.3 MainWindow集成

```python
# src/ui/main_window.py 修改点
from ..audio.audio_manager import AudioManager

class MainWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.audio_manager = AudioManager()
        # 进入主界面时确保播放mode_select BGM
        self.audio_manager.play_bgm("mode_select")
        # ... 其余初始化

    def _on_logout_clicked(self):
        # 退出登录切换回login BGM
        self.audio_manager.switch_bgm("login")
        self.logout_requested.emit()

    def _on_history_clicked(self):
        # 查看战绩不切换BGM，继续播放mode_select
        pass
```

#### 6.5.4 BattleWindow集成

```python
# src/ui/battle_window.py 修改点
from ..audio.audio_manager import AudioManager

class BattleWindow(QWidget):
    def __init__(self, game_engine, score_manager, user_id, mode):
        super().__init__()
        self.audio_manager = AudioManager()
        self.mode = mode
        # 进入对战界面切换BGM
        self.audio_manager.switch_bgm("battle", mode=mode)
        # ... 其余初始化

    def _on_choice_selected(self, choice: Choice):
        # Ducking机制：出拳时压低BGM
        self.audio_manager.duck_bgm()

        # 播放出拳音效
        sfx_map = {
            Choice.ROCK: "rock",
            Choice.SCISSORS: "scissors",
            Choice.PAPER: "paper"
        }
        self.audio_manager.play_sfx(sfx_map[choice])

        # ... 处理对战逻辑

        # 播放判定音效
        result_sfx_map = {
            Result.WIN: "win",
            Result.LOSE: "lose",
            Result.DRAW: "draw"
        }
        self.audio_manager.play_sfx(result_sfx_map[result])

        # 恢复BGM音量
        self.audio_manager.restore_bgm()

    def _finish_game(self):
        # 对战结束，切换到结算BGM
        final_result = self.game_engine.get_final_result()
        result_str = "win" if final_result == Result.WIN else "lose"
        self.audio_manager.switch_bgm("settlement", mode=self.mode, result=result_str)

    def _on_continue_clicked(self):
        # 再来一局，重新播放对战BGM
        self.audio_manager.switch_bgm("battle", mode=self.mode)

    def _on_finish_clicked(self):
        # 返回主界面，切换到mode_select BGM
        self.audio_manager.switch_bgm("mode_select")
```

### 6.6 异常处理设计

| 异常场景 | 处理策略 | 说明 |
|----------|----------|------|
| 音频文件不存在 | 静默跳过，不播放 | `_play_bgm_by_key`和`_preload_sfx`中检查文件存在性 |
| BGM播放失败 | 静默跳过，不影响游戏流程 | QMediaPlayer内部错误不抛出异常 |
| SFX播放失败 | 静默跳过，不影响游戏流程 | QSoundEffect播放失败不抛出异常 |
| sounds_dir未设置 | 所有播放操作静默返回 | `set_sounds_dir`未调用时不播放 |
| 应用异常关闭 | closeEvent中调用stop_all | 确保音频资源释放 |

### 6.7 配置项设计

在 `src/config/settings.py` 中新增音频相关配置：

```python
# 音频配置
SOUNDS_DIR = ASSETS_DIR / "sounds"
BGM_VOLUME = 0.7           # 默认BGM音量
SFX_VOLUME = 1.0           # 默认SFX音量
DUCK_VOLUME = 0.2          # Ducking时BGM音量
```

---

## 7. 评审签字

| 角色 | 姓名 | 日期 | 签字 |
|------|------|------|------|
| 项目负责人 |  |  |  |
| Planner架构师 | Planner | 2026-06-01 | ✓ |
| Coder开发工程师 | Coder | 2026-06-03 | ✓ |
| Tester测试工程师 |  |  |  |
| Reviewer代码审查 |  |  |  |

---

**文档状态**: 待审核
**当前版本号**: v1.2.0
**基线版本号**: v1.0.0
**基线创建日期**: 2026-06-01
**基线保存位置**: docs/dd/DETAILED_DESIGN_v1.0.0.md
