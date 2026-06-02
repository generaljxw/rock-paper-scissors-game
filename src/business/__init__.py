# src/business/__init__.py
"""
业务逻辑层模块

本包包含游戏的核心业务逻辑模块：
- enums: 枚举类型定义
- user_manager: 用户管理
- game_engine: 游戏引擎
- score_manager: 积分管理
- statistics: 统计分析
"""

from .enums import Choice, Result, BattleMode
from .user_manager import UserManager
from .game_engine import GameEngine
from .score_manager import ScoreManager
from .statistics import Statistics

__all__ = [
    'Choice',
    'Result',
    'BattleMode',
    'UserManager',
    'GameEngine',
    'ScoreManager',
    'Statistics'
]
