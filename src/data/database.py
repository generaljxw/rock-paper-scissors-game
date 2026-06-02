# src/data/database.py
"""
数据层数据库管理模块

本模块负责数据库的初始化连接管理，
采用单例模式确保全局只有一个数据库连接实例。
"""

import sqlite3
import os
import sys
from pathlib import Path
from typing import Optional


class Database:
    """
    数据库管理类（单例模式）
    负责数据库的初始化和连接管理
    """

    _instance: Optional['Database'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.db_path = self._get_database_path()

        self._initialized = True
        self._init_database()

    def _get_database_path(self) -> Path:
        """
        获取数据库文件路径，包含多种回退机制
        """
        possible_paths = []

        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包环境 - 使用AppData目录确保持久化
            appdata_roaming = Path(os.getenv('APPDATA', '')) / "RockPaperScissors"
            appdata_local = Path(os.getenv('LOCALAPPDATA', '')) / "RockPaperScissors"
            user_home = Path.home() / "RockPaperScissors"
            exe_dir = Path(sys.executable).parent / "RockPaperScissors"

            possible_paths.extend([
                appdata_roaming,
                appdata_local,
                user_home,
                exe_dir
            ])
        else:
            # 开发环境
            dev_path = Path(__file__).parent.parent.parent / "data"
            possible_paths.append(dev_path)

        # 尝试创建目录并返回有效路径
        for path in possible_paths:
            try:
                if path.exists():
                    if path.is_dir():
                        return path / "game.db"
                    else:
                        continue

                # 尝试创建目录
                path.mkdir(parents=True, exist_ok=True)

                # 验证目录可写
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()

                return path / "game.db"
            except (PermissionError, OSError, IOError):
                continue
            except Exception:
                continue

        # 所有路径都失败，使用临时目录作为最后手段
        import tempfile
        fallback = Path(tempfile.gettempdir()) / "RockPaperScissors_fallback"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback / "game.db"

    def _init_database(self):
        """
        初始化数据库表结构
        创建用户表、对战记录表和积分表
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS battle_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    mode INTEGER NOT NULL,
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

            self._migrate_battle_records(cursor)

            conn.commit()
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """
        获取数据库连接
        返回配置了Row Factory的连接对象，便于通过列名访问数据
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"获取数据库连接失败: {e}")
            raise

    def close_connection(self, conn: sqlite3.Connection):
        """
        关闭数据库连接
        """
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"关闭数据库连接失败: {e}")

    def _migrate_battle_records(self, cursor):
        """
        迁移battle_records表：移除player_choice和ai_choice字段
        如果表中存在这两个字段，则重建表结构
        """
        cursor.execute("PRAGMA table_info(battle_records)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'player_choice' in columns or 'ai_choice' in columns:
            cursor.execute("ALTER TABLE battle_records RENAME TO battle_records_old")

            cursor.execute("""
                CREATE TABLE battle_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    mode INTEGER NOT NULL,
                    result TEXT NOT NULL,
                    score_change INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            cursor.execute("""
                INSERT INTO battle_records (id, user_id, mode, result, score_change, created_at)
                SELECT id, user_id, mode, result, score_change, created_at
                FROM battle_records_old
            """)

            cursor.execute("DROP TABLE battle_records_old")

    def get_db_path(self) -> str:
        """
        获取数据库文件路径（用于调试和日志）
        返回:
            数据库文件的绝对路径字符串
        """
        return str(self.db_path)