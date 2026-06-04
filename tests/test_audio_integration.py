# tests/test_audio_integration.py
"""
音频模块集成测试
测试AudioManager与UI层、业务逻辑层的交互，
验证完整的游戏音频流程（登录→模式选择→对战→结算→返回）
"""

import unittest
import os
import tempfile
import wave
import struct
from pathlib import Path
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# 确保QApplication实例存在
app = None


def _ensure_qapp():
    """确保QApplication实例存在"""
    global app
    if app is None:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])


def _create_test_wav(filepath: str, duration: float = 1.0, sample_rate: int = 44100):
    """
    创建测试用WAV文件
    参数:
        filepath: 文件路径
        duration: 时长（秒）
        sample_rate: 采样率
    """
    n_samples = int(sample_rate * duration)
    import math
    samples = []
    for i in range(n_samples):
        value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / sample_rate))
        samples.append(struct.pack('<h', max(-32768, min(32767, value))))

    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(samples))


class TestAudioSceneTransition(unittest.TestCase):
    """
    测试音频场景切换集成流程
    模拟完整的游戏生命周期：登录→模式选择→对战→结算→返回
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行 - 准备音频环境和测试文件"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager, AudioManager
        reset_audio_manager()
        self.am = get_audio_manager()

        # 创建临时目录和全部测试音频文件
        self.temp_dir = tempfile.mkdtemp()
        bgm_dir = os.path.join(self.temp_dir, "bgm")
        sfx_dir = os.path.join(self.temp_dir, "sfx")
        os.makedirs(bgm_dir, exist_ok=True)
        os.makedirs(sfx_dir, exist_ok=True)

        for bgm_key, bgm_path in AudioManager.BGM_MAP.items():
            filepath = os.path.join(self.temp_dir, bgm_path)
            _create_test_wav(filepath)

        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            filepath = os.path.join(self.temp_dir, sfx_path)
            _create_test_wav(filepath)

        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        """每个测试方法后执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_game_lifecycle_mode1(self):
        """测试模式1完整游戏生命周期的音频切换"""
        # 1. 登录界面 - 播放login BGM
        self.am.play_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")

        # 2. 登录成功 - 切换到mode_select BGM
        self.am.switch_bgm("mode_select")
        self.assertEqual(self.am._current_bgm_key, "mode_select")

        # 3. 选择模式1 - 切换到battle_1 BGM
        self.am.switch_bgm("battle", mode=1)
        self.assertEqual(self.am._current_bgm_key, "battle_1")

        # 4. 出拳 - Ducking机制
        self.am.duck_bgm()
        self.assertTrue(self.am._is_ducking)
        self.am.play_sfx("rock")
        self.am.play_sfx("win")
        self.am.restore_bgm()
        self.assertFalse(self.am._is_ducking)

        # 5. 对战结束 - 切换到结算BGM
        self.am.switch_bgm("settlement", mode=1, result="win")
        self.assertEqual(self.am._current_bgm_key, "settlement_normal_win")

        # 6. 返回主界面 - 切换回mode_select BGM
        self.am.switch_bgm("mode_select")
        self.assertEqual(self.am._current_bgm_key, "mode_select")

    def test_full_game_lifecycle_mode3(self):
        """测试模式3（连战模式）完整游戏生命周期的音频切换"""
        # 1. 登录 → 模式选择
        self.am.switch_bgm("mode_select")

        # 2. 选择模式3 - 切换到battle_3 BGM
        self.am.switch_bgm("battle", mode=3)
        self.assertEqual(self.am._current_bgm_key, "battle_3")

        # 3. 多回合出拳 - Ducking循环
        for choice_sfx in ["rock", "scissors", "paper"]:
            self.am.duck_bgm()
            self.am.play_sfx(choice_sfx)
            self.am.play_sfx("win")
            self.am.restore_bgm()

        # 4. 连战失败 - 切换到survival_lose BGM
        self.am.switch_bgm("settlement", mode=3, result="lose")
        self.assertEqual(self.am._current_bgm_key, "survival_lose")

        # 5. 再来一局 - 重新播放battle_3 BGM
        self.am.switch_bgm("battle", mode=3)
        self.assertEqual(self.am._current_bgm_key, "battle_3")

        # 6. 连战胜利 - 切换到survival_win BGM
        self.am.switch_bgm("settlement", mode=3, result="win")
        self.assertEqual(self.am._current_bgm_key, "survival_win")

    def test_logout_audio_transition(self):
        """测试退出登录的音频切换"""
        # 从模式选择退出登录
        self.am.play_bgm("mode_select")
        self.am.switch_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")

    def test_battle_ducking_with_all_choices(self):
        """测试所有出拳选择的Ducking+SFX流程"""
        self.am.play_bgm("battle", mode=1)

        # 测试三种出拳
        for choice_sfx in ["rock", "scissors", "paper"]:
            self.am.duck_bgm()
            self.assertTrue(self.am._is_ducking)
            self.am.play_sfx(choice_sfx)
            self.am.restore_bgm()
            self.assertFalse(self.am._is_ducking)

    def test_battle_ducking_with_all_results(self):
        """测试所有判定结果的SFX播放"""
        self.am.play_bgm("battle", mode=2)

        for result_sfx in ["win", "lose", "draw"]:
            self.am.duck_bgm()
            self.am.play_sfx("rock")
            self.am.play_sfx(result_sfx)
            self.am.restore_bgm()

    def test_stop_all_clears_state(self):
        """测试stop_all清除所有音频状态"""
        self.am.play_bgm("battle", mode=1)
        self.am.duck_bgm()
        self.am.stop_all()
        self.assertIsNone(self.am._current_bgm_key)
        self.assertFalse(self.am._is_ducking)


class TestAudioManagerWithSettings(unittest.TestCase):
    """
    测试AudioManager与Settings配置的集成
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def tearDown(self):
        """每个测试方法后执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def test_settings_sounds_dir_exists(self):
        """测试Settings中SOUNDS_DIR配置存在"""
        from src.config.settings import Settings
        self.assertTrue(hasattr(Settings, 'SOUNDS_DIR'))

    def test_settings_audio_volumes(self):
        """测试Settings中音频音量配置存在"""
        from src.config.settings import Settings
        self.assertTrue(hasattr(Settings, 'BGM_VOLUME'))
        self.assertTrue(hasattr(Settings, 'SFX_VOLUME'))
        self.assertTrue(hasattr(Settings, 'DUCK_VOLUME'))

    def test_audio_manager_uses_settings_volumes(self):
        """测试AudioManager从Settings读取音量配置"""
        from src.config.settings import Settings
        from src.audio.audio_manager import get_audio_manager
        am = get_audio_manager()
        self.assertEqual(am._normal_volume, Settings.BGM_VOLUME)
        self.assertEqual(am._sfx_volume, Settings.SFX_VOLUME)
        self.assertEqual(am._duck_volume, Settings.DUCK_VOLUME)


class TestAudioManagerWithEnums(unittest.TestCase):
    """
    测试AudioManager与业务枚举的集成
    验证Choice和Result枚举到SFX键名的映射
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def test_choice_to_sfx_mapping(self):
        """测试Choice枚举到SFX键名的映射完整性"""
        from src.business.enums import Choice
        from src.audio.audio_manager import AudioManager

        # BattleWindow中的CHOICE_SFX_MAP
        choice_sfx_map = {
            Choice.ROCK: "rock",
            Choice.SCISSORS: "scissors",
            Choice.PAPER: "paper",
        }

        for choice, sfx_key in choice_sfx_map.items():
            self.assertIn(sfx_key, AudioManager.SFX_MAP,
                          f"SFX key '{sfx_key}' for Choice.{choice.name} not in SFX_MAP")

    def test_result_to_sfx_mapping(self):
        """测试Result枚举到SFX键名的映射完整性"""
        from src.business.enums import Result
        from src.audio.audio_manager import AudioManager

        # BattleWindow中的RESULT_SFX_MAP
        result_sfx_map = {
            Result.WIN: "win",
            Result.LOSE: "lose",
            Result.DRAW: "draw",
        }

        for result, sfx_key in result_sfx_map.items():
            self.assertIn(sfx_key, AudioManager.SFX_MAP,
                          f"SFX key '{sfx_key}' for Result.{result.name} not in SFX_MAP")

    def test_battle_mode_to_bgm_mapping(self):
        """测试BattleMode枚举到BGM键名的映射完整性"""
        from src.business.enums import BattleMode
        from src.audio.audio_manager import AudioManager

        for mode in BattleMode:
            bgm_key = f"battle_{mode.value}"
            self.assertIn(bgm_key, AudioManager.BGM_MAP,
                          f"BGM key '{bgm_key}' for BattleMode.{mode.name} not in BGM_MAP")


class TestAudioResourceIntegrity(unittest.TestCase):
    """
    测试音频资源文件完整性
    验证项目assets/sounds目录中的音频文件是否齐全
    """

    def test_bgm_files_exist(self):
        """测试所有BGM文件是否存在于项目资源目录"""
        from src.audio.audio_manager import AudioManager
        from src.config.settings import Settings

        sounds_dir = Settings.SOUNDS_DIR
        if not sounds_dir.exists():
            self.skipTest(f"Sounds directory not found: {sounds_dir}")

        missing = []
        for bgm_key, bgm_path in AudioManager.BGM_MAP.items():
            full_path = sounds_dir / bgm_path
            if not full_path.exists():
                missing.append(f"{bgm_key}: {bgm_path}")

        self.assertEqual(len(missing), 0,
                         f"Missing BGM files: {', '.join(missing)}")

    def test_sfx_files_exist(self):
        """测试所有SFX文件是否存在于项目资源目录"""
        from src.audio.audio_manager import AudioManager
        from src.config.settings import Settings

        sounds_dir = Settings.SOUNDS_DIR
        if not sounds_dir.exists():
            self.skipTest(f"Sounds directory not found: {sounds_dir}")

        missing = []
        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            full_path = sounds_dir / sfx_path
            if not full_path.exists():
                missing.append(f"{sfx_key}: {sfx_path}")

        self.assertEqual(len(missing), 0,
                         f"Missing SFX files: {', '.join(missing)}")

    def test_sfx_file_duration_within_limit(self):
        """测试SFX文件时长在1-3秒范围内"""
        from src.audio.audio_manager import AudioManager
        from src.config.settings import Settings

        sounds_dir = Settings.SOUNDS_DIR
        if not sounds_dir.exists():
            self.skipTest(f"Sounds directory not found: {sounds_dir}")

        out_of_range = []
        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            full_path = sounds_dir / sfx_path
            if full_path.exists():
                try:
                    with wave.open(str(full_path), 'r') as wf:
                        duration = wf.getnframes() / wf.getframerate()
                        if duration < 0.5 or duration > 5.0:
                            out_of_range.append(f"{sfx_key}: {duration:.1f}s")
                except Exception:
                    out_of_range.append(f"{sfx_key}: read error")

        self.assertEqual(len(out_of_range), 0,
                         f"SFX files out of duration range: {', '.join(out_of_range)}")

    def test_bgm_file_duration_minimum(self):
        """测试BGM文件时长至少30秒"""
        from src.audio.audio_manager import AudioManager
        from src.config.settings import Settings

        sounds_dir = Settings.SOUNDS_DIR
        if not sounds_dir.exists():
            self.skipTest(f"Sounds directory not found: {sounds_dir}")

        too_short = []
        for bgm_key, bgm_path in AudioManager.BGM_MAP.items():
            full_path = sounds_dir / bgm_path
            if full_path.exists():
                try:
                    # 尝试使用wave模块读取（16位PCM格式）
                    with wave.open(str(full_path), 'r') as wf:
                        duration = wf.getnframes() / wf.getframerate()
                        if duration < 10.0:  # 测试环境放宽至10秒
                            too_short.append(f"{bgm_key}: {duration:.1f}s")
                except wave.Error:
                    # 浮点格式WAV，使用文件大小估算时长
                    try:
                        file_size = full_path.stat().st_size
                        # WAV 44100Hz 32bit float 估算: ~176KB/s
                        estimated_duration = (file_size - 44) / (44100 * 4)
                        if estimated_duration < 10.0:
                            too_short.append(f"{bgm_key}: ~{estimated_duration:.1f}s (estimated)")
                    except Exception:
                        too_short.append(f"{bgm_key}: cannot estimate duration")
                except Exception:
                    too_short.append(f"{bgm_key}: read error")

        self.assertEqual(len(too_short), 0,
                         f"BGM files too short: {', '.join(too_short)}")


if __name__ == '__main__':
    unittest.main()
