# tests/test_audio_special.py
"""
音频模块专项测试
重点验证音量调节、BGM循环、SFX并发播放、Ducking时序、
音频切换、多声道支持、边界条件和异常场景
"""

import unittest
import os
import tempfile
import wave
import struct
import math
from pathlib import Path
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import QApplication
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtCore import QUrl

app = None


def _ensure_qapp():
    """确保QApplication实例存在"""
    global app
    if app is None:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])


def _create_test_wav(filepath: str, duration: float = 1.0, sample_rate: int = 44100,
                     channels: int = 1, sample_width: int = 2):
    """
    创建测试用WAV文件
    参数:
        filepath: 文件路径
        duration: 时长（秒）
        sample_rate: 采样率
        channels: 声道数（1=单声道，2=双声道）
        sample_width: 采样位宽（2=16位）
    """
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / sample_rate))
        sample = struct.pack('<h', max(-32768, min(32767, value)))
        # 多声道：每个声道写入相同数据
        samples.append(sample * channels)

    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(samples))


def _setup_audio_env():
    """创建完整的音频测试环境（临时目录+测试WAV文件）"""
    from src.audio.audio_manager import AudioManager
    temp_dir = tempfile.mkdtemp()
    bgm_dir = os.path.join(temp_dir, "bgm")
    sfx_dir = os.path.join(temp_dir, "sfx")
    os.makedirs(bgm_dir, exist_ok=True)
    os.makedirs(sfx_dir, exist_ok=True)

    for bgm_key, bgm_path in AudioManager.BGM_MAP.items():
        filepath = os.path.join(temp_dir, bgm_path)
        _create_test_wav(filepath, duration=2.0)

    for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
        filepath = os.path.join(temp_dir, sfx_path)
        _create_test_wav(filepath, duration=0.5)

    return temp_dir


# ============================================================
# 一、音量调节专项测试
# ============================================================
class TestVolumeControl(unittest.TestCase):
    """
    测试音量调节功能
    验证BGM音量、SFX音量、Ducking音量的正确设置和恢复
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bgm_initial_volume_matches_settings(self):
        """测试BGM初始音量与Settings配置一致"""
        from src.config.settings import Settings
        self.assertAlmostEqual(self.am._bgm_output.volume(), Settings.BGM_VOLUME, places=1)

    def test_sfx_volume_matches_settings(self):
        """测试SFX音量与Settings配置一致"""
        from src.config.settings import Settings
        for sfx_key, effect in self.am._sfx_cache.items():
            self.assertAlmostEqual(effect.volume(), Settings.SFX_VOLUME, places=1)

    def test_duck_volume_matches_settings(self):
        """测试Ducking音量与Settings配置一致"""
        from src.config.settings import Settings
        self.assertEqual(self.am._duck_volume, Settings.DUCK_VOLUME)

    def test_duck_sets_volume_to_duck_level(self):
        """测试Ducking将BGM音量设为Duck级别"""
        self.am.duck_bgm()
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._duck_volume, places=1)

    def test_restore_sets_volume_to_normal_level(self):
        """测试恢复将BGM音量设回正常级别"""
        self.am.duck_bgm()
        self.am.restore_bgm()
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._normal_volume, places=1)

    def test_volume_range_valid(self):
        """测试所有音量值在合法范围[0.0, 1.0]内"""
        self.assertGreaterEqual(self.am._normal_volume, 0.0)
        self.assertLessEqual(self.am._normal_volume, 1.0)
        self.assertGreaterEqual(self.am._duck_volume, 0.0)
        self.assertLessEqual(self.am._duck_volume, 1.0)
        self.assertGreaterEqual(self.am._sfx_volume, 0.0)
        self.assertLessEqual(self.am._sfx_volume, 1.0)

    def test_duck_volume_less_than_normal(self):
        """测试Duck音量低于正常音量"""
        self.assertLess(self.am._duck_volume, self.am._normal_volume)


# ============================================================
# 二、BGM循环播放专项测试
# ============================================================
class TestBGMLooping(unittest.TestCase):
    """
    测试BGM循环播放机制
    验证BGM播放结束后的自动循环逻辑
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bgm_loops_on_end_of_media(self):
        """测试BGM播放结束时自动从头播放"""
        # 模拟BGM播放结束信号
        self.am.play_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")

        # 触发EndOfMedia状态
        self.am._on_bgm_status_changed(QMediaPlayer.MediaStatus.EndOfMedia)
        # 验证播放器位置被重置且仍在播放
        self.assertEqual(self.am._bgm_player.position(), 0)

    def test_bgm_does_not_loop_on_other_status(self):
        """测试非EndOfMedia状态不触发循环"""
        self.am.play_bgm("login")

        # Buffered状态不应触发循环
        self.am._on_bgm_status_changed(QMediaPlayer.MediaStatus.BufferedMedia)
        # 不应改变播放位置
        self.assertEqual(self.am._current_bgm_key, "login")

    def test_bgm_same_key_no_repeat(self):
        """测试同一首BGM不重复播放"""
        self.am.play_bgm("login")
        source1 = self.am._bgm_player.source()

        # 再次播放同一首
        self.am.play_bgm("login")
        source2 = self.am._bgm_player.source()

        # source应该没有变化
        self.assertEqual(source1, source2)

    def test_switch_bgm_changes_source(self):
        """测试切换BGM会改变播放源"""
        self.am.play_bgm("login")
        source1 = self.am._bgm_player.source()

        self.am.switch_bgm("mode_select")
        source2 = self.am._bgm_player.source()

        self.assertNotEqual(source1, source2)


# ============================================================
# 三、SFX并发播放专项测试
# ============================================================
class TestSFXConcurrentPlayback(unittest.TestCase):
    """
    测试SFX并发播放
    验证多个SFX可以同时播放（出拳SFX+判定SFX）
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_play_choice_and_result_sfx_concurrently(self):
        """测试同时播放出拳SFX和判定SFX"""
        # 模拟BattleWindow中的Ducking+SFX流程
        self.am.duck_bgm()
        self.am.play_sfx("rock")
        self.am.play_sfx("win")
        self.am.restore_bgm()
        # 不应抛出异常

    def test_play_all_choice_sfx_sequentially(self):
        """测试顺序播放所有出拳SFX"""
        for sfx_key in ["rock", "scissors", "paper"]:
            self.am.play_sfx(sfx_key)
        # 不应抛出异常

    def test_play_all_result_sfx_sequentially(self):
        """测试顺序播放所有判定SFX"""
        for sfx_key in ["win", "lose", "draw"]:
            self.am.play_sfx(sfx_key)
        # 不应抛出异常

    def test_rapid_sfx_playback(self):
        """测试快速连续播放SFX"""
        for _ in range(10):
            self.am.play_sfx("rock")
        # 不应抛出异常或崩溃

    def test_sfx_cache_independent_playback(self):
        """测试SFX缓存中各音效独立播放"""
        # 同时播放多个不同SFX
        self.am.play_sfx("rock")
        self.am.play_sfx("win")
        self.am.play_sfx("draw")
        # 不应抛出异常


# ============================================================
# 四、Ducking时序专项测试
# ============================================================
class TestDuckingTiming(unittest.TestCase):
    """
    测试Ducking机制的时序正确性
    验证Ducking-播放SFX-恢复的完整时序
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_duck_before_sfx(self):
        """测试Ducking在SFX播放前执行"""
        # 初始状态：未Ducking
        self.assertFalse(self.am._is_ducking)

        # Ducking
        self.am.duck_bgm()
        self.assertTrue(self.am._is_ducking)
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._duck_volume, places=1)

        # 播放SFX
        self.am.play_sfx("rock")
        # Ducking状态应保持
        self.assertTrue(self.am._is_ducking)

    def test_restore_after_sfx(self):
        """测试SFX播放后恢复BGM音量"""
        self.am.duck_bgm()
        self.am.play_sfx("rock")
        self.am.play_sfx("win")
        self.am.restore_bgm()

        self.assertFalse(self.am._is_ducking)
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._normal_volume, places=1)

    def test_multiple_duck_restore_cycles(self):
        """测试多次Ducking-恢复循环"""
        for _ in range(5):
            self.am.duck_bgm()
            self.assertTrue(self.am._is_ducking)
            self.am.play_sfx("rock")
            self.am.play_sfx("win")
            self.am.restore_bgm()
            self.assertFalse(self.am._is_ducking)

    def test_duck_during_bgm_playback(self):
        """测试BGM播放中Ducking不影响BGM播放状态"""
        self.am.play_bgm("battle", mode=1)
        self.assertEqual(self.am._current_bgm_key, "battle_1")

        self.am.duck_bgm()
        # BGM仍在播放，只是音量降低
        self.assertEqual(self.am._current_bgm_key, "battle_1")

        self.am.restore_bgm()
        # BGM继续播放
        self.assertEqual(self.am._current_bgm_key, "battle_1")

    def test_stop_all_resets_ducking(self):
        """测试stop_all重置Ducking状态"""
        self.am.duck_bgm()
        self.assertTrue(self.am._is_ducking)
        self.am.stop_all()
        self.assertFalse(self.am._is_ducking)


# ============================================================
# 五、音频切换专项测试
# ============================================================
class TestAudioSwitching(unittest.TestCase):
    """
    测试音频切换功能
    验证BGM场景切换、SFX切换的正确性
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_switch_bgm_login_to_mode_select(self):
        """测试从登录BGM切换到模式选择BGM"""
        self.am.play_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")

        self.am.switch_bgm("mode_select")
        self.assertEqual(self.am._current_bgm_key, "mode_select")

    def test_switch_bgm_mode_select_to_battle(self):
        """测试从模式选择BGM切换到对战BGM"""
        self.am.play_bgm("mode_select")
        self.am.switch_bgm("battle", mode=1)
        self.assertEqual(self.am._current_bgm_key, "battle_1")

    def test_switch_bgm_battle_to_settlement(self):
        """测试从对战BGM切换到结算BGM"""
        self.am.play_bgm("battle", mode=1)
        self.am.switch_bgm("settlement", mode=1, result="win")
        self.assertEqual(self.am._current_bgm_key, "settlement_normal_win")

    def test_switch_bgm_settlement_to_mode_select(self):
        """测试从结算BGM切换回模式选择BGM"""
        self.am.play_bgm("settlement", mode=1, result="win")
        self.am.switch_bgm("mode_select")
        self.assertEqual(self.am._current_bgm_key, "mode_select")

    def test_switch_bgm_battle_mode1_to_mode2(self):
        """测试不同对战模式BGM切换"""
        self.am.play_bgm("battle", mode=1)
        self.am.switch_bgm("battle", mode=2)
        self.assertEqual(self.am._current_bgm_key, "battle_2")

    def test_switch_bgm_survival_win(self):
        """测试连战模式胜利结算BGM"""
        self.am.switch_bgm("settlement", mode=3, result="win")
        self.assertEqual(self.am._current_bgm_key, "survival_win")

    def test_switch_bgm_survival_lose(self):
        """测试连战模式失败结算BGM"""
        self.am.switch_bgm("settlement", mode=3, result="lose")
        self.assertEqual(self.am._current_bgm_key, "survival_lose")


# ============================================================
# 六、多声道支持专项测试
# ============================================================
class TestMultiChannelSupport(unittest.TestCase):
    """
    测试多声道音频文件支持
    验证单声道和双声道WAV文件均可正常加载和播放
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = tempfile.mkdtemp()
        bgm_dir = os.path.join(self.temp_dir, "bgm")
        sfx_dir = os.path.join(self.temp_dir, "sfx")
        os.makedirs(bgm_dir, exist_ok=True)
        os.makedirs(sfx_dir, exist_ok=True)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mono_wav_sfx_loads(self):
        """测试单声道SFX可正常加载"""
        from src.audio.audio_manager import AudioManager
        # 创建单声道SFX
        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            filepath = os.path.join(self.temp_dir, sfx_path)
            _create_test_wav(filepath, duration=0.5, channels=1)

        self.am.set_sounds_dir(self.temp_dir)
        for sfx_key in AudioManager.SFX_MAP:
            self.assertIn(sfx_key, self.am._sfx_cache)

    def test_stereo_wav_sfx_loads(self):
        """测试双声道SFX可正常加载"""
        from src.audio.audio_manager import AudioManager
        # 创建双声道SFX
        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            filepath = os.path.join(self.temp_dir, sfx_path)
            _create_test_wav(filepath, duration=0.5, channels=2)

        self.am.set_sounds_dir(self.temp_dir)
        for sfx_key in AudioManager.SFX_MAP:
            self.assertIn(sfx_key, self.am._sfx_cache)

    def test_stereo_wav_bgm_plays(self):
        """测试双声道BGM可正常播放"""
        from src.audio.audio_manager import AudioManager
        # 创建双声道BGM
        for bgm_key, bgm_path in AudioManager.BGM_MAP.items():
            filepath = os.path.join(self.temp_dir, bgm_path)
            _create_test_wav(filepath, duration=2.0, channels=2)

        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            filepath = os.path.join(self.temp_dir, sfx_path)
            _create_test_wav(filepath, duration=0.5, channels=2)

        self.am.set_sounds_dir(self.temp_dir)
        self.am.play_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")


# ============================================================
# 七、边界条件专项测试
# ============================================================
class TestBoundaryConditions(unittest.TestCase):
    """
    测试边界条件和异常场景
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def test_play_bgm_without_setting_dir(self):
        """测试未设置目录时播放BGM - 不崩溃"""
        self.am.play_bgm("login")
        self.assertIsNone(self.am._current_bgm_key)

    def test_play_sfx_without_setting_dir(self):
        """测试未设置目录时播放SFX - 不崩溃"""
        self.am.play_sfx("rock")

    def test_switch_bgm_without_setting_dir(self):
        """测试未设置目录时切换BGM - 不崩溃"""
        self.am.switch_bgm("battle", mode=1)

    def test_duck_without_bgm_output(self):
        """测试BGM输出不存在时Ducking - 不崩溃"""
        self.am._bgm_output = None
        self.am.duck_bgm()
        # 不应抛出异常

    def test_restore_without_bgm_output(self):
        """测试BGM输出不存在时恢复 - 不崩溃"""
        self.am._bgm_output = None
        self.am.restore_bgm()
        # 不应抛出异常

    def test_play_bgm_with_empty_scene(self):
        """测试空场景字符串播放BGM - 不崩溃"""
        self.am.play_bgm("")
        self.assertIsNone(self.am._current_bgm_key)

    def test_play_sfx_with_empty_type(self):
        """测试空类型字符串播放SFX - 不崩溃"""
        self.am.play_sfx("")

    def test_set_sounds_dir_nonexistent(self):
        """测试设置不存在的目录 - _sounds_dir应为None"""
        self.am.set_sounds_dir("/nonexistent/path/that/does/not/exist")
        self.assertIsNone(self.am._sounds_dir)

    def test_set_sounds_dir_empty_string(self):
        """测试设置空字符串目录 - 不崩溃"""
        self.am.set_sounds_dir("")
        self.assertIsNone(self.am._sounds_dir)

    def test_resolve_bgm_key_invalid_mode_zero(self):
        """测试模式0解析BGM键 - 返回None"""
        result = self.am._resolve_bgm_key("battle", mode=0)
        self.assertIsNone(result)

    def test_resolve_bgm_key_negative_mode(self):
        """测试负数模式解析BGM键 - 返回None"""
        result = self.am._resolve_bgm_key("battle", mode=-1)
        self.assertIsNone(result)

    def test_resolve_bgm_key_settlement_mode3_draw(self):
        """测试连战模式平局结算 - 返回None（draw不是有效结算结果）"""
        result = self.am._resolve_bgm_key("settlement", mode=3, result="draw")
        self.assertIsNone(result)

    def test_stop_all_when_nothing_playing(self):
        """测试无音频播放时stop_all - 不崩溃"""
        self.am.stop_all()
        self.assertIsNone(self.am._current_bgm_key)
        self.assertFalse(self.am._is_ducking)

    def test_multiple_stop_all_calls(self):
        """测试多次调用stop_all - 不崩溃"""
        for _ in range(5):
            self.am.stop_all()

    def test_multiple_reset_instance(self):
        """测试多次重置单例 - 不崩溃"""
        from src.audio.audio_manager import reset_audio_manager
        for _ in range(5):
            reset_audio_manager()


# ============================================================
# 八、SFX缓存管理专项测试
# ============================================================
class TestSFXCacheManagement(unittest.TestCase):
    """
    测试SFX缓存管理
    验证缓存清空、重新加载的正确性
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sfx_cache_populated_after_set_dir(self):
        """测试设置目录后SFX缓存被填充"""
        from src.audio.audio_manager import AudioManager
        self.assertEqual(len(self.am._sfx_cache), len(AudioManager.SFX_MAP))

    def test_sfx_cache_cleared_on_dir_reset(self):
        """测试重新设置目录时旧缓存被清空"""
        # 先记录旧缓存中的effect对象
        old_effect = self.am._sfx_cache.get("rock")
        self.assertIsNotNone(old_effect)

        # 重新设置同一目录
        self.am.set_sounds_dir(self.temp_dir)
        new_effect = self.am._sfx_cache.get("rock")

        # 缓存应被重建，effect对象应是新的
        self.assertIsNotNone(new_effect)

    def test_sfx_cache_empty_when_dir_invalid(self):
        """测试设置无效目录后缓存为空"""
        self.am.set_sounds_dir("/nonexistent")
        self.assertEqual(len(self.am._sfx_cache), 0)


# ============================================================
# 九、Settings配置集成测试
# ============================================================
class TestSettingsAudioConfig(unittest.TestCase):
    """
    测试Settings音频配置与AudioManager的集成
    """

    def test_settings_bgm_volume_range(self):
        """测试Settings中BGM音量在合法范围"""
        from src.config.settings import Settings
        self.assertGreaterEqual(Settings.BGM_VOLUME, 0.0)
        self.assertLessEqual(Settings.BGM_VOLUME, 1.0)

    def test_settings_sfx_volume_range(self):
        """测试Settings中SFX音量在合法范围"""
        from src.config.settings import Settings
        self.assertGreaterEqual(Settings.SFX_VOLUME, 0.0)
        self.assertLessEqual(Settings.SFX_VOLUME, 1.0)

    def test_settings_duck_volume_range(self):
        """测试Settings中Duck音量在合法范围"""
        from src.config.settings import Settings
        self.assertGreaterEqual(Settings.DUCK_VOLUME, 0.0)
        self.assertLessEqual(Settings.DUCK_VOLUME, 1.0)

    def test_settings_duck_less_than_bgm(self):
        """测试Settings中Duck音量低于BGM音量"""
        from src.config.settings import Settings
        self.assertLess(Settings.DUCK_VOLUME, Settings.BGM_VOLUME)

    def test_settings_sounds_dir_exists(self):
        """测试Settings中SOUNDS_DIR路径存在"""
        from src.config.settings import Settings
        self.assertTrue(Settings.SOUNDS_DIR.exists())

    def test_settings_sounds_dir_has_bgm_subdir(self):
        """测试Settings中SOUNDS_DIR下有bgm子目录"""
        from src.config.settings import Settings
        bgm_dir = Settings.SOUNDS_DIR / "bgm"
        self.assertTrue(bgm_dir.exists())

    def test_settings_sounds_dir_has_sfx_subdir(self):
        """测试Settings中SOUNDS_DIR下有sfx子目录"""
        from src.config.settings import Settings
        sfx_dir = Settings.SOUNDS_DIR / "sfx"
        self.assertTrue(sfx_dir.exists())


# ============================================================
# 十、BGM错误处理专项测试
# ============================================================
class TestBGMErrorHandling(unittest.TestCase):
    """
    测试BGM播放错误处理
    """

    @classmethod
    def setUpClass(cls):
        _ensure_qapp()

    def setUp(self):
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()
        self.temp_dir = _setup_audio_env()
        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bgm_error_callback_does_not_crash(self):
        """测试BGM错误回调不导致崩溃"""
        self.am.play_bgm("login")
        # 模拟BGM错误
        self.am._on_bgm_error(QMediaPlayer.Error.ResourceError, "Test error")
        # 不应抛出异常

    def test_bgm_missing_file_does_not_crash(self):
        """测试BGM文件缺失不导致崩溃"""
        # 设置一个空目录
        empty_dir = tempfile.mkdtemp()
        try:
            self.am.set_sounds_dir(empty_dir)
            self.am.play_bgm("login")
            self.assertIsNone(self.am._current_bgm_key)
        finally:
            import shutil
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_sfx_missing_file_does_not_crash(self):
        """测试SFX文件缺失不导致崩溃"""
        empty_dir = tempfile.mkdtemp()
        try:
            self.am.set_sounds_dir(empty_dir)
            self.am.play_sfx("rock")
            # 不应抛出异常
        finally:
            import shutil
            shutil.rmtree(empty_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
