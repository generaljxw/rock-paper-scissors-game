# src/data/migrations/0001_initial_schema.py
"""
迁移脚本: 创建初始数据库表结构
迁移编号: 0001
迁移名称: initial_schema
创建日期: 2026-06-01
描述: 创建用户表、对战记录表和积分表
"""

def upgrade(conn):
    """执行迁移"""
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
    print("[OK] 迁移 0001_initial_schema 执行成功")


def downgrade(conn):
    """回滚迁移"""
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS scores")
    cursor.execute("DROP TABLE IF EXISTS battle_records")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    conn.commit()
    print("[OK] 迁移 0001_initial_schema 回滚成功")
