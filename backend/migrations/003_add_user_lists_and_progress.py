#!/usr/bin/env python3

import sqlite3
import os

def run_migration():
    """Add user lists and progress tracking tables"""
    
    # Get database path
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(backend_dir, 'devprep_problems.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding user lists and progress tracking tables...")
        
        # Create user_lists table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                list_type TEXT NOT NULL CHECK (list_type IN ('favorites', 'todo', 'solved', 'custom')),
                description TEXT,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, name)
            )
        """)
        
        # Create user_list_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_list_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                question_id INTEGER,
                user_question_id INTEGER,
                status TEXT DEFAULT 'not_attempted' CHECK (status IN ('not_attempted', 'in_progress', 'solved')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (list_id) REFERENCES user_lists (id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
                FOREIGN KEY (user_question_id) REFERENCES user_questions (id) ON DELETE CASCADE,
                CHECK ((question_id IS NOT NULL AND user_question_id IS NULL) OR 
                       (question_id IS NULL AND user_question_id IS NOT NULL))
            )
        """)
        
        # Create user_question_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_question_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER,
                user_question_id INTEGER,
                status TEXT DEFAULT 'not_attempted' CHECK (status IN ('not_attempted', 'in_progress', 'solved')),
                attempts INTEGER DEFAULT 0,
                time_spent_minutes INTEGER DEFAULT 0,
                notes TEXT,
                last_attempted TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
                FOREIGN KEY (user_question_id) REFERENCES user_questions (id) ON DELETE CASCADE,
                CHECK ((question_id IS NOT NULL AND user_question_id IS NULL) OR 
                       (question_id IS NULL AND user_question_id IS NOT NULL)),
                UNIQUE(user_id, question_id, user_question_id)
            )
        """)
        
        # Check if is_public column exists, add if not
        cursor.execute("PRAGMA table_info(user_questions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'is_public' not in columns:
            cursor.execute("""
                ALTER TABLE user_questions 
                ADD COLUMN is_public BOOLEAN DEFAULT TRUE
            """)
            print("✅ Added is_public column to user_questions")
        
        print("✅ Successfully added user lists and progress tracking tables")
        
        # Create default lists for existing users
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        
        for user_row in users:
            user_id = user_row[0]
            
            # Create default lists
            default_lists = [
                ('Favorites', 'favorites', 'Questions you want to revisit'),
                ('Todo', 'todo', 'Questions you plan to solve'),
                ('Solved', 'solved', 'Questions you have completed')
            ]
            
            for name, list_type, description in default_lists:
                cursor.execute("""
                    INSERT OR IGNORE INTO user_lists (user_id, name, list_type, description, is_default)
                    VALUES (?, ?, ?, ?, TRUE)
                """, (user_id, name, list_type, description))
        
        print(f"✅ Created default lists for {len(users)} users")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
