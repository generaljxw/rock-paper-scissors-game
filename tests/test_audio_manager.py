# tests/test_audio_manager.py
"""
音频管理器模块单元测试
测试AudioManager的核心功能，包括单例模式、BGM键解析、
SFX缓存、Ducking机制和播放控制逻辑
"""

import unittest
import os
import tempfile
import wave
import struct
from unittest.mock import patch, MagicMock
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtMultimedia import QMediaPlayer

# 确保QApplication实例存在（PyQt6多媒体组件需要）
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
    # 生成440Hz正弦波
    samples = []
    for i in range(n_samples):
        value = int(32767 * 0.5 * __import__('math').sin(2 * __import__('math').pi * 440 * i / sample_rate))
        samples.append(struct.pack('<h', max(-32768, min(32767, value))))

    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(samples))


class TestAudioManagerSingleton(unittest.TestCase):
    """
    测试AudioManager单例模式
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化 - 确保QApplication存在"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行 - 重置单例"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def tearDown(self):
        """每个测试方法后执行 - 清理单例"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def test_singleton_returns_same_instance(self):
        """测试单例模式 - 多次获取返回同一对象"""
        from src.audio.audio_manager import get_audio_manager
        am1 = get_audio_manager()
        am2 = get_audio_manager()
        self.assertIs(am1, am2)

    def test_reset_instance_creates_new(self):
        """测试重置单例 - 重置后创建新实例"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        am1 = get_audio_manager()
        reset_audio_manager()
        am2 = get_audio_manager()
        self.assertIsNot(am1, am2)


class TestResolveBGMKey(unittest.TestCase):
    """
    测试BGM键解析逻辑
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()

    def tearDown(self):
        """每个测试方法后执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def test_resolve_login(self):
        """测试解析登录场景BGM键"""
        result = self.am._resolve_bgm_key("login")
        self.assertEqual(result, "login")

    def test_resolve_mode_select(self):
        """测试解析模式选择场景BGM键"""
        result = self.am._resolve_bgm_key("mode_select")
        self.assertEqual(result, "mode_select")

    def test_resolve_battle_mode1(self):
        """测试解析对战模式1 BGM键"""
        result = self.am._resolve_bgm_key("battle", mode=1)
        self.assertEqual(result, "battle_1")

    def test_resolve_battle_mode2(self):
        """测试解析对战模式2 BGM键"""
        result = self.am._resolve_bgm_key("battle", mode=2)
        self.assertEqual(result, "battle_2")

    def test_resolve_battle_mode3(self):
        """测试解析对战模式3 BGM键"""
        result = self.am._resolve_bgm_key("battle", mode=3)
        self.assertEqual(result, "battle_3")

    def test_resolve_battle_invalid_mode(self):
        """测试解析对战无效模式 - 返回None"""
        result = self.am._resolve_bgm_key("battle", mode=4)
        self.assertIsNone(result)

    def test_resolve_battle_no_mode(self):
        """测试解析对战无模式参数 - 返回None"""
        result = self.am._resolve_bgm_key("battle")
        self.assertIsNone(result)

    def test_resolve_settlement_normal_win(self):
        """测试解析普通模式胜利结算BGM键"""
        result = self.am._resolve_bgm_key("settlement", mode=1, result="win")
        self.assertEqual(result, "settlement_normal_win")

    def test_resolve_settlement_normal_lose(self):
        """测试解析普通模式失败结算BGM键"""
        result = self.am._resolve_bgm_key("settlement", mode=2, result="lose")
        self.assertEqual(result, "settlement_normal_lose")

    def test_resolve_settlement_survival_win(self):
        """测试解析连战模式胜利结算BGM键"""
        result = self.am._resolve_bgm_key("settlement", mode=3, result="win")
        self.assertEqual(result, "survival_win")

    def test_resolve_settlement_survival_lose(self):
        """测试解析连战模式失败结算BGM键"""
        result = self.am._resolve_bgm_key("settlement", mode=3, result="lose")
        self.assertEqual(result, "survival_lose")

    def test_resolve_settlement_no_result(self):
        """测试解析结算无结果参数 - 返回None"""
        result = self.am._resolve_bgm_key("settlement", mode=1)
        self.assertIsNone(result)

    def test_resolve_settlement_invalid_result(self):
        """测试解析结算无效结果 - 返回None"""
        result = self.am._resolve_bgm_key("settlement", mode=1, result="draw")
        self.assertIsNone(result)

    def test_resolve_unknown_scene(self):
        """测试解析未知场景 - 返回None"""
        result = self.am._resolve_bgm_key("unknown_scene")
        self.assertIsNone(result)


class TestDuckingMechanism(unittest.TestCase):
    """
    测试Ducking机制
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()

    def tearDown(self):
        """每个测试方法后执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def test_duck_bgm_reduces_volume(self):
        """测试Ducking降低BGM音量"""
        self.am.duck_bgm()
        self.assertTrue(self.am._is_ducking)
        # 验证音量被设置为_duck_volume（浮点精度容差）
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._duck_volume, places=1)

    def test_restore_bgm_increases_volume(self):
        """测试恢复BGM音量"""
        self.am.duck_bgm()
        self.am.restore_bgm()
        self.assertFalse(self.am._is_ducking)
        # 验证音量恢复为_normal_volume（浮点精度容差）
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._normal_volume, places=1)

    def test_duck_idempotent(self):
        """测试重复Ducking不会重复降低音量"""
        self.am.duck_bgm()
        volume_after_first = self.am._bgm_output.volume()
        self.am.duck_bgm()
        volume_after_second = self.am._bgm_output.volume()
        self.assertAlmostEqual(volume_after_first, volume_after_second, places=2)

    def test_restore_without_duck(self):
        """测试未Ducking时恢复音量无效"""
        self.assertFalse(self.am._is_ducking)
        self.am.restore_bgm()
        # 音量应保持_normal_volume不变（浮点精度容差）
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._normal_volume, places=1)

    def test_duck_restore_cycle(self):
        """测试完整的Ducking-恢复循环"""
        # 初始状态
        self.assertFalse(self.am._is_ducking)
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._normal_volume, places=1)

        # Ducking
        self.am.duck_bgm()
        self.assertTrue(self.am._is_ducking)
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._duck_volume, places=1)

        # 恢复
        self.am.restore_bgm()
        self.assertFalse(self.am._is_ducking)
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._normal_volume, places=1)

        # 再次Ducking
        self.am.duck_bgm()
        self.assertTrue(self.am._is_ducking)
        self.assertAlmostEqual(self.am._bgm_output.volume(), self.am._duck_volume, places=1)


class TestBGMPlaybackControl(unittest.TestCase):
    """
    测试BGM播放控制逻辑
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行 - 创建临时目录和测试音频文件"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager, AudioManager
        reset_audio_manager()
        self.am = get_audio_manager()

        # 创建临时目录和测试WAV文件
        self.temp_dir = tempfile.mkdtemp()
        bgm_dir = os.path.join(self.temp_dir, "bgm")
        sfx_dir = os.path.join(self.temp_dir, "sfx")
        os.makedirs(bgm_dir, exist_ok=True)
        os.makedirs(sfx_dir, exist_ok=True)

        # 为所有BGM创建测试文件
        for bgm_key, bgm_path in AudioManager.BGM_MAP.items():
            filepath = os.path.join(self.temp_dir, bgm_path)
            _create_test_wav(filepath)

        # 为所有SFX创建测试文件
        for sfx_key, sfx_path in AudioManager.SFX_MAP.items():
            filepath = os.path.join(self.temp_dir, sfx_path)
            _create_test_wav(filepath)

        self.am.set_sounds_dir(self.temp_dir)

    def tearDown(self):
        """每个测试方法后执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_set_sounds_dir(self):
        """测试设置音频资源目录"""
        self.assertIsNotNone(self.am._sounds_dir)
        self.assertTrue(self.am._sounds_dir.exists())

    def test_set_sounds_dir_nonexistent(self):
        """测试设置不存在的目录 - _sounds_dir应被设为None"""
        self.am.set_sounds_dir(self.temp_dir)
        self.assertTrue(len(self.am._sfx_cache) > 0)
        # 设置不存在的目录
        self.am.set_sounds_dir("/nonexistent/path")
        # _sounds_dir应被设为None
        self.assertIsNone(self.am._sounds_dir)

    def test_play_bgm_login(self):
        """测试播放登录BGM"""
        self.am.play_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")

    def test_play_bgm_same_key_no_repeat(self):
        """测试重复播放同一首BGM不重复"""
        self.am.play_bgm("login")
        first_key = self.am._current_bgm_key
        self.am.play_bgm("login")
        # 应该是同一首，不会重新设置source
        self.assertEqual(self.am._current_bgm_key, first_key)

    def test_play_bgm_invalid_scene(self):
        """测试播放无效场景BGM - 不应崩溃"""
        self.am.play_bgm("invalid_scene")
        self.assertIsNone(self.am._current_bgm_key)

    def test_stop_bgm(self):
        """测试停止BGM"""
        self.am.play_bgm("login")
        self.am.stop_bgm()
        self.assertIsNone(self.am._current_bgm_key)

    def test_switch_bgm(self):
        """测试切换BGM"""
        self.am.play_bgm("login")
        self.assertEqual(self.am._current_bgm_key, "login")
        self.am.switch_bgm("mode_select")
        self.assertEqual(self.am._current_bgm_key, "mode_select")

    def test_switch_bgm_to_battle(self):
        """测试切换到对战BGM"""
        self.am.switch_bgm("battle", mode=1)
        self.assertEqual(self.am._current_bgm_key, "battle_1")

    def test_switch_bgm_to_settlement(self):
        """测试切换到结算BGM"""
        self.am.switch_bgm("settlement", mode=1, result="win")
        self.assertEqual(self.am._current_bgm_key, "settlement_normal_win")

    def test_stop_all(self):
        """测试停止所有音频"""
        self.am.play_bgm("login")
        self.am.stop_all()
        self.assertIsNone(self.am._current_bgm_key)


class TestSFXPlayback(unittest.TestCase):
    """
    测试SFX播放逻辑
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager, AudioManager
        reset_audio_manager()
        self.am = get_audio_manager()

        # 创建临时目录和测试SFX文件
        self.temp_dir = tempfile.mkdtemp()
        sfx_dir = os.path.join(self.temp_dir, "sfx")
        os.makedirs(sfx_dir, exist_ok=True)

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

    def test_sfx_preloaded(self):
        """测试SFX预加载 - 所有SFX应被缓存"""
        from src.audio.audio_manager import AudioManager
        for sfx_key in AudioManager.SFX_MAP:
            self.assertIn(sfx_key, self.am._sfx_cache,
                          f"SFX '{sfx_key}' not found in cache")

    def test_play_sfx_valid(self):
        """测试播放有效SFX - 不应崩溃"""
        from src.audio.audio_manager import AudioManager
        for sfx_key in AudioManager.SFX_MAP:
            self.am.play_sfx(sfx_key)

    def test_play_sfx_invalid(self):
        """测试播放无效SFX - 不应崩溃"""
        self.am.play_sfx("invalid_sfx")

    def test_sfx_cache_empty_without_dir(self):
        """测试未设置目录时SFX缓存为空"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        am = get_audio_manager()
        self.assertEqual(am._sfx_cache, {})


class TestBGMMapCompleteness(unittest.TestCase):
    """
    测试BGM映射表完整性
    """

    def test_bgm_map_has_all_scenes(self):
        """测试BGM映射表包含所有必要场景"""
        from src.audio.audio_manager import AudioManager
        expected_keys = [
            "login", "mode_select",
            "battle_1", "battle_2", "battle_3",
            "settlement_normal_win", "settlement_normal_lose",
            "survival_win", "survival_lose"
        ]
        for key in expected_keys:
            self.assertIn(key, AudioManager.BGM_MAP,
                          f"Missing BGM key: {key}")

    def test_sfx_map_has_all_types(self):
        """测试SFX映射表包含所有必要类型"""
        from src.audio.audio_manager import AudioManager
        expected_keys = ["rock", "scissors", "paper", "win", "lose", "draw"]
        for key in expected_keys:
            self.assertIn(key, AudioManager.SFX_MAP,
                          f"Missing SFX key: {key}")


class TestAudioManagerNoSoundsDir(unittest.TestCase):
    """
    测试未设置音频目录时的行为
    """

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        _ensure_qapp()

    def setUp(self):
        """每个测试方法前执行"""
        from src.audio.audio_manager import get_audio_manager, reset_audio_manager
        reset_audio_manager()
        self.am = get_audio_manager()

    def tearDown(self):
        """每个测试方法后执行"""
        from src.audio.audio_manager import reset_audio_manager
        reset_audio_manager()

    def test_play_bgm_without_dir(self):
        """测试未设置目录时播放BGM - 不应崩溃"""
        self.am.play_bgm("login")
        self.assertIsNone(self.am._current_bgm_key)

    def test_play_sfx_without_dir(self):
        """测试未设置目录时播放SFX - 不应崩溃"""
        self.am.play_sfx("rock")

    def test_switch_bgm_without_dir(self):
        """测试未设置目录时切换BGM - 不应崩溃"""
        self.am.switch_bgm("mode_select")


if __name__ == '__main__':
    unittest.main()
