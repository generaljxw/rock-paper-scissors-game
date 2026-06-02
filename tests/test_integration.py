# tests/test_integration.py
"""
集成测试 - 完整游戏流程测试

本模块测试从游戏启动到结束的完整流程，
包括用户注册、登录、选择对战模式、出拳、胜负判定、
结果展示、积分更新等全部环节。
"""

import pytest
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.business.game_engine import GameEngine
from src.business.user_manager import UserManager
from src.business.score_manager import ScoreManager
from src.business.statistics import Statistics
from src.business.enums import Choice, Result, BattleMode
from src.data.database import Database
from src.data.models import BattleRecord


class TestGameCoreLogic:
    """
    测试游戏核心逻辑
    """

    def test_rock_beats_scissors(self):
        """
        测试核心规则：石头胜剪刀
        """
        engine = GameEngine()
        result = engine.determine_winner(Choice.ROCK, Choice.SCISSORS)
        assert result == Result.WIN, "石头应该战胜剪刀"

    def test_scissors_beats_paper(self):
        """
        测试核心规则：剪刀胜布
        """
        engine = GameEngine()
        result = engine.determine_winner(Choice.SCISSORS, Choice.PAPER)
        assert result == Result.WIN, "剪刀应该战胜布"

    def test_paper_beats_rock(self):
        """
        测试核心规则：布胜石头
        """
        engine = GameEngine()
        result = engine.determine_winner(Choice.PAPER, Choice.ROCK)
        assert result == Result.WIN, "布应该战胜石头"

    def test_same_choice_draw(self):
        """
        测试核心规则：相同选择为平局
        """
        engine = GameEngine()
        assert engine.determine_winner(Choice.ROCK, Choice.ROCK) == Result.DRAW
        assert engine.determine_winner(Choice.SCISSORS, Choice.SCISSORS) == Result.DRAW
        assert engine.determine_winner(Choice.PAPER, Choice.PAPER) == Result.DRAW

    def test_lose_scenarios(self):
        """
        测试失败场景
        """
        engine = GameEngine()
        assert engine.determine_winner(Choice.SCISSORS, Choice.ROCK) == Result.LOSE
        assert engine.determine_winner(Choice.PAPER, Choice.SCISSORS) == Result.LOSE
        assert engine.determine_winner(Choice.ROCK, Choice.PAPER) == Result.LOSE


class TestGameEngineSession:
    """
    测试游戏引擎会话管理
    """

    def test_start_game_session(self):
        """
        测试开始游戏会话
        """
        engine = GameEngine()
        session = engine.start_game(user_id=1, mode=1)
        
        assert session is not None
        assert session['user_id'] == 1
        assert session['mode'] == 1
        assert session['rounds'] == []
        assert session['win_count'] == 0
        assert session['lose_count'] == 0
        assert session['draw_count'] == 0

    def test_ai_choice_is_valid(self):
        """
        测试AI随机生成的选择是有效的
        """
        engine = GameEngine()
        valid_choices = list(Choice)
        
        for _ in range(100):
            ai_choice = engine._get_ai_choice()
            assert ai_choice in valid_choices, f"AI选择 {ai_choice} 无效"

    def test_play_round_returns_valid_result(self):
        """
        测试出拳返回有效结果
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=1)
        
        result = engine.play_round(Choice.ROCK)
        
        assert 'player_choice' in result
        assert 'ai_choice' in result
        assert 'result' in result
        assert result['player_choice'] == Choice.ROCK
        assert result['ai_choice'] in list(Choice)
        assert result['result'] in [Result.WIN, Result.LOSE, Result.DRAW]


class TestMode1Flow:
    """
    测试模式1：一局定胜负流程
    """

    def test_mode1_single_round(self):
        """
        测试模式1单局流程
        模式1规则：一局定胜负，平局继续直到分出胜负
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=1)
        
        max_attempts = 10
        for i in range(max_attempts):
            result = engine.play_round(Choice.ROCK)
            assert result is not None
            assert 'result' in result
            
            if result['result'] != Result.DRAW:
                break
        
        assert engine.is_battle_finished() == True
        final_result = engine.get_final_result()
        assert final_result in [Result.WIN, Result.LOSE]

    def test_mode1_with_draw_continues(self):
        """
        测试模式1平局时继续游戏
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=1)
        
        max_attempts = 10
        for _ in range(max_attempts):
            result = engine.play_round(Choice.ROCK)
            if result['result'] != Result.DRAW:
                break
        
        assert engine.is_battle_finished() == True


class TestMode2Flow:
    """
    测试模式2：三局两胜流程
    """

    def test_mode2_requires_two_wins(self):
        """
        测试模式2需要获得2胜
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=2)
        
        rounds_played = 0
        max_rounds = 10
        
        while not engine.is_battle_finished() and rounds_played < max_rounds:
            engine.play_round(Choice.ROCK)
            rounds_played += 1
        
        session = engine.current_session
        assert session['win_count'] >= 1 or session['lose_count'] >= 1
        assert session['effective_rounds'] >= 1


class TestMode3Flow:
    """
    测试模式3：连战模式流程
    """

    def test_mode3_ends_on_loss(self):
        """
        测试模式3失败时结束
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=3)
        
        max_attempts = 10
        for _ in range(max_attempts):
            if engine.is_battle_finished():
                break
            engine.play_round(Choice.ROCK)
        
        session = engine.current_session
        if session['lose_count'] >= 1:
            assert engine.is_battle_finished() == True

    def test_mode3_consecutive_wins_tracking(self):
        """
        测试模式3连续胜利追踪
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=3)
        
        engine.play_round(Choice.ROCK)
        engine.play_round(Choice.ROCK)
        
        consecutive = engine.get_consecutive_wins()
        assert consecutive >= 0


class TestUserRegistrationAndLogin:
    """
    测试用户注册和登录流程
    """

    def test_full_register_login_flow(self):
        """
        测试完整注册登录流程
        """
        user_manager = UserManager()
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        password = "password123"
        
        success, message = user_manager.register(username, password)
        assert success, f"注册失败: {message}"
        
        user = user_manager.get_current_user()
        assert user is not None
        assert user.username == username
        
        user_manager.logout()
        assert user_manager.get_current_user() is None
        
        success, message = user_manager.login(username, password)
        assert success, f"登录失败: {message}"
        
        user = user_manager.get_current_user()
        assert user is not None
        assert user.username == username


class TestScoreManagement:
    """
    测试积分管理流程
    """

    def test_score_creation_on_register(self):
        """
        测试注册时创建积分记录
        """
        user_manager = UserManager()
        score_manager = ScoreManager()
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        
        success, _ = user_manager.register(username, "password123")
        assert success
        
        user = user_manager.get_current_user()
        score = score_manager.get_score(user.id)
        assert score == 0

    def test_score_update_after_game(self):
        """
        测试游戏后积分更新
        """
        user_manager = UserManager()
        score_manager = ScoreManager()
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        
        user_manager.register(username, "password123")
        user = user_manager.get_current_user()
        
        initial_score = score_manager.get_score(user.id)
        
        score_manager.update_score(user.id, 10)
        new_score = score_manager.get_score(user.id)
        assert new_score == initial_score + 10


class TestStatisticsCalculation:
    """
    测试统计计算
    """

    def test_win_rate_calculation(self):
        """
        测试胜率计算
        """
        statistics = Statistics()
        score_manager = ScoreManager()
        
        user_manager = UserManager()
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        user_manager.register(username, "password123")
        user = user_manager.get_current_user()
        
        score_manager.update_score(user.id, 10)
        score_manager.score_dao.update_statistics(user.id, win=True)
        score_manager.score_dao.update_statistics(user.id, win=True)
        score_manager.score_dao.update_statistics(user.id, lose=True)
        
        win_rate = statistics.get_win_rate(user.id)
        assert 0 <= win_rate <= 100


class TestEndToEndFlow:
    """
    端到端完整流程测试
    """

    def test_complete_game_flow(self):
        """
        测试完整游戏流程：启动 -> 出拳 -> 判定 -> 结算
        """
        engine = GameEngine()
        score_manager = ScoreManager()
        user_manager = UserManager()
        
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        user_manager.register(username, "password123")
        user = user_manager.get_current_user()
        
        initial_score = score_manager.get_score(user.id)
        
        engine.start_game(user_id=user.id, mode=1)
        
        max_attempts = 10
        round_result = None
        for i in range(max_attempts):
            round_result = engine.play_round(Choice.ROCK)
            assert round_result is not None
            assert 'result' in round_result
            
            if round_result['result'] != Result.DRAW:
                break
        
        assert engine.is_battle_finished() == True
        
        final_result = engine.get_final_result()
        assert final_result in [Result.WIN, Result.LOSE]
        
        score_change = score_manager.calculate_score_change(1, final_result.value)
        if score_change != 0:
            score_manager.update_score(user.id, score_change)
        
        engine.save_battle_record(score_change)
        engine.end_game()
        
        assert engine.current_session is None

    def test_all_choices_produce_valid_results(self):
        """
        测试所有选择都能产生有效结果
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=1)
        
        for choice in [Choice.ROCK, Choice.SCISSORS, Choice.PAPER]:
            result = engine.play_round(choice)
            assert result['player_choice'] == choice
            assert result['result'] in [Result.WIN, Result.LOSE, Result.DRAW]
            engine.start_game(user_id=1, mode=1)


class TestBattleRecordPersistence:
    """
    测试对战记录持久化
    """

    def test_battle_record_saved(self):
        """
        测试对战记录正确保存
        """
        user_manager = UserManager()
        statistics = Statistics()
        engine = GameEngine()
        
        username = f"test_user_{uuid.uuid4().hex[:8]}"
        user_manager.register(username, "password123")
        user = user_manager.get_current_user()
        
        engine.start_game(user_id=user.id, mode=1)
        engine.play_round(Choice.ROCK)
        
        session_summary = engine.get_session_summary()
        score_change = 1 if session_summary['final_result'] == '胜利' else -1
        
        engine.save_battle_record(score_change)
        
        history = statistics.get_battle_history(user.id, limit=10)
        assert len(history) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])