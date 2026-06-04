# src/config/settings.py
"""
配置层应用配置模块

本模块定义了应用程序的全局配置项，
包括游戏参数、界面设置和数据库配置等。
"""

import os
from pathlib import Path


class Settings:
    """
    应用配置类
    集中管理应用程序的所有配置项
    """

    PROJECT_NAME = "猜拳小游戏"
    PROJECT_VERSION = "1.1.0"

    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    ASSETS_DIR = BASE_DIR / "assets"

    DB_PATH = DATA_DIR / "game.db"

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    WINDOW_TITLE = "猜拳小游戏"

    ROCK_IMAGE = "rock.png"
    SCISSORS_IMAGE = "scissors.png"
    PAPER_IMAGE = "paper.png"

    ROCK_KEY = "r"
    SCISSORS_KEY = "s"
    PAPER_KEY = "p"

    AI_DIFFICULTY_EASY = 0.3
    AI_DIFFICULTY_NORMAL = 0.5
    AI_DIFFICULTY_HARD = 0.8

    DEFAULT_USERNAME_MIN_LENGTH = 3
    DEFAULT_PASSWORD_MIN_LENGTH = 6

    MAX_HISTORY_RECORDS = 100

    # 音频配置
    SOUNDS_DIR = ASSETS_DIR / "sounds"
    BGM_VOLUME = 0.7           # 默认BGM音量
    SFX_VOLUME = 1.0           # 默认SFX音量
    DUCK_VOLUME = 0.2          # Ducking时BGM音量

    @classmethod
    def ensure_directories(cls):
        """
        确保必要的目录存在
        """
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
