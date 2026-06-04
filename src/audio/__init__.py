# src/audio/__init__.py
"""
音频管理模块

提供游戏背景音乐（BGM）和音效（SFX）的播放控制功能，
包括场景切换、Ducking机制和音量管理。
"""

from .audio_manager import AudioManager, get_audio_manager, reset_audio_manager

__all__ = ["AudioManager", "get_audio_manager", "reset_audio_manager"]
