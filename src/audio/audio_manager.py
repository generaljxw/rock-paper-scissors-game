# src/audio/audio_manager.py
"""
音频管理器模块

基于PyQt6的QMediaPlayer和QSoundEffect实现游戏音频管理，
支持背景音乐（BGM）循环播放、音效（SFX）即时播放和Ducking机制。
采用单例模式确保全局只有一个音频管理器实例。
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QUrl, QObject
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect

logger = logging.getLogger(__name__)


class AudioManager(QObject):
    """
    音频管理器类
    负责管理游戏所有背景音乐和音效的播放控制
    底层基于QMediaPlayer（BGM）和QSoundEffect（SFX）实现
    通过模块级get_audio_manager()函数获取单例实例
    """

    # BGM场景映射表：场景键名 -> 音频文件相对路径
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

    # SFX类型映射表：音效键名 -> 音频文件相对路径
    SFX_MAP = {
        "rock": "sfx/rock.wav",
        "scissors": "sfx/scissors.wav",
        "paper": "sfx/paper.wav",
        "win": "sfx/win.wav",
        "lose": "sfx/lose.wav",
        "draw": "sfx/draw.wav",
    }

    def __init__(self):
        """初始化音频管理器"""
        super().__init__()

        # 从Settings读取音量配置，避免配置重复定义
        from ..config.settings import Settings
        self._duck_volume: float = Settings.DUCK_VOLUME
        self._normal_volume: float = Settings.BGM_VOLUME
        self._sfx_volume: float = Settings.SFX_VOLUME

        # 当前播放的BGM键名，防止重复播放同一首
        self._current_bgm_key: Optional[str] = None
        # 是否处于Ducking状态
        self._is_ducking: bool = False
        # 音频资源根目录路径
        self._sounds_dir: Optional[Path] = None

        # BGM播放器和音频输出
        self._bgm_player: Optional[QMediaPlayer] = None
        self._bgm_output: Optional[QAudioOutput] = None

        # SFX预加载缓存
        self._sfx_cache: dict[str, QSoundEffect] = {}

        # 初始化播放器和缓存
        self._init_players()
        logger.info("AudioManager initialized")

    def _init_players(self):
        """初始化BGM播放器和SFX缓存"""
        # 创建BGM播放器
        self._bgm_player = QMediaPlayer()
        self._bgm_output = QAudioOutput()
        self._bgm_player.setAudioOutput(self._bgm_output)
        self._bgm_output.setVolume(self._normal_volume)

        # 监听BGM播放状态，实现自动循环
        self._bgm_player.mediaStatusChanged.connect(self._on_bgm_status_changed)
        self._bgm_player.errorOccurred.connect(self._on_bgm_error)

        logger.debug("BGM player initialized, volume=%.1f", self._normal_volume)

    def _on_bgm_status_changed(self, status: QMediaPlayer.MediaStatus):
        """
        BGM播放状态变化回调
        当BGM播放结束时自动从头重新播放，实现循环效果
        参数:
            status: 媒体状态
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            logger.debug("BGM ended, looping: %s", self._current_bgm_key)
            self._bgm_player.setPosition(0)
            self._bgm_player.play()

    def _on_bgm_error(self, error: QMediaPlayer.Error, error_string: str):
        """
        BGM播放错误回调
        记录错误日志但不抛出异常，不影响游戏流程
        参数:
            error: 错误类型
            error_string: 错误描述
        """
        logger.warning("BGM playback error: %s - %s", error, error_string)

    def _preload_sfx(self):
        """预加载所有SFX到缓存，确保播放时无延迟"""
        if not self._sounds_dir:
            return

        # 清空旧缓存，避免陈旧引用
        self._sfx_cache.clear()

        loaded_count = 0
        for sfx_key, sfx_path in self.SFX_MAP.items():
            full_path = self._sounds_dir / sfx_path
            if full_path.exists():
                try:
                    effect = QSoundEffect()
                    effect.setSource(QUrl.fromLocalFile(str(full_path)))
                    effect.setVolume(self._sfx_volume)
                    self._sfx_cache[sfx_key] = effect
                    loaded_count += 1
                    logger.debug("SFX preloaded: %s -> %s", sfx_key, full_path)
                except Exception as e:
                    logger.warning("Failed to preload SFX %s: %s", sfx_key, e)
            else:
                logger.warning("SFX file not found: %s", full_path)

        logger.info("SFX preloaded: %d/%d", loaded_count, len(self.SFX_MAP))

    def set_sounds_dir(self, sounds_dir: str):
        """
        设置音频资源根目录
        设置后自动预加载所有SFX
        参数:
            sounds_dir: 音频资源根目录的绝对路径
        """
        # 清空旧缓存和状态
        self._sfx_cache.clear()
        self._sounds_dir = None

        if not sounds_dir:
            logger.warning("Empty sounds directory path")
            return

        path = Path(sounds_dir)
        if not path.exists():
            logger.warning("Sounds directory not found: %s", sounds_dir)
            return
        self._sounds_dir = path
        self._preload_sfx()
        logger.info("Sounds directory set: %s", sounds_dir)

    def play_bgm(self, scene: str, mode: int = None, result: str = None) -> None:
        """
        播放背景音乐
        如果当前已在播放同一首BGM则不重复播放
        参数:
            scene: 场景标识（login/mode_select/battle/settlement）
            mode: 对战模式（1/2/3），仅battle场景使用
            result: 结算结果（win/lose），仅settlement场景使用
        """
        bgm_key = self._resolve_bgm_key(scene, mode, result)
        if bgm_key is None:
            logger.warning("Cannot resolve BGM key: scene=%s, mode=%s, result=%s",
                           scene, mode, result)
            return

        # 同一首BGM不重复播放
        if bgm_key == self._current_bgm_key:
            logger.debug("BGM already playing: %s, skip", bgm_key)
            return

        self._play_bgm_by_key(bgm_key)

    def stop_bgm(self) -> None:
        """停止当前背景音乐"""
        if self._bgm_player:
            self._bgm_player.stop()
        old_key = self._current_bgm_key
        self._current_bgm_key = None
        logger.debug("BGM stopped: %s", old_key)

    def switch_bgm(self, scene: str, mode: int = None, result: str = None) -> None:
        """
        无缝切换背景音乐
        先停止当前音乐再播放目标场景音乐
        参数:
            scene: 场景标识（login/mode_select/battle/settlement）
            mode: 对战模式（1/2/3），仅battle场景使用
            result: 结算结果（win/lose），仅settlement场景使用
        """
        logger.debug("Switching BGM: scene=%s, mode=%s, result=%s", scene, mode, result)
        self.stop_bgm()
        self.play_bgm(scene, mode, result)

    def play_sfx(self, sfx_type: str) -> None:
        """
        播放音效
        从缓存中获取预加载的音效并播放
        参数:
            sfx_type: 音效类型（rock/scissors/paper/win/lose/draw）
        """
        effect = self._sfx_cache.get(sfx_type)
        if effect:
            effect.play()
            logger.debug("SFX played: %s", sfx_type)
        else:
            logger.warning("SFX not found in cache: %s", sfx_type)

    def duck_bgm(self) -> None:
        """
        压低背景音乐音量（Ducking机制）
        出拳时调用，将BGM音量降至_duck_volume，
        确保出拳音效和判定音效清晰可闻
        """
        if not self._is_ducking and self._bgm_output:
            self._bgm_output.setVolume(self._duck_volume)
            self._is_ducking = True
            logger.debug("BGM ducked: volume %.1f -> %.1f",
                         self._normal_volume, self._duck_volume)

    def restore_bgm(self) -> None:
        """
        恢复背景音乐音量
        音效播放完毕后调用，将BGM音量恢复至_normal_volume
        """
        if self._is_ducking and self._bgm_output:
            self._bgm_output.setVolume(self._normal_volume)
            self._is_ducking = False
            logger.debug("BGM restored: volume %.1f", self._normal_volume)

    def stop_all(self) -> None:
        """停止所有音乐和音效（应用退出时调用）"""
        self.stop_bgm()
        self._is_ducking = False
        for sfx_key, effect in self._sfx_cache.items():
            effect.stop()
        logger.info("All audio stopped")

    def _resolve_bgm_key(self, scene: str, mode: int = None,
                         result: str = None) -> Optional[str]:
        """
        根据场景参数解析BGM资源键
        参数:
            scene: 场景标识
            mode: 对战模式
            result: 结算结果
        返回:
            BGM_MAP中的键名，无法解析时返回None
        """
        if scene == "login":
            return "login"
        elif scene == "mode_select":
            return "mode_select"
        elif scene == "battle":
            if mode in (1, 2, 3):
                return f"battle_{mode}"
        elif scene == "settlement":
            if result not in ("win", "lose"):
                return None
            if mode == 3:
                return f"survival_{result}"
            else:
                return f"settlement_normal_{result}"
        return None

    def _play_bgm_by_key(self, bgm_key: str) -> None:
        """
        根据BGM键名播放音乐
        参数:
            bgm_key: BGM_MAP中的键名
        """
        if not self._sounds_dir:
            logger.warning("Sounds directory not set, cannot play BGM")
            return

        bgm_path = self.BGM_MAP.get(bgm_key)
        if bgm_path is None:
            logger.warning("Unknown BGM key: %s", bgm_key)
            return

        full_path = self._sounds_dir / bgm_path
        if not full_path.exists():
            logger.warning("BGM file not found: %s", full_path)
            return

        source = QUrl.fromLocalFile(str(full_path))
        self._bgm_player.setSource(source)
        self._bgm_player.play()
        self._current_bgm_key = bgm_key
        logger.info("BGM playing: %s -> %s", bgm_key, full_path)


# 模块级单例实例
_instance: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """
    获取AudioManager单例实例
    首次调用时创建实例，后续调用返回同一实例
    返回:
        AudioManager单例实例
    """
    global _instance
    if _instance is None:
        _instance = AudioManager()
    return _instance


def reset_audio_manager():
    """
    重置AudioManager单例实例
    仅用于单元测试，清理单例状态
    """
    global _instance
    if _instance:
        _instance.stop_all()
    _instance = None
    logger.debug("AudioManager instance reset")
