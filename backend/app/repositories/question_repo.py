import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

class UnifiedQuestionRepository:
    def __init__(self, db_path: str = "devprep_problems.db"):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def create_question(self, question_data: dict, user_id: int) -> int:
        """Create a new question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            topics_json = json.dumps(question_data.get('topics', []))
            
            cursor.execute("""
                INSERT INTO questions (title, description, difficulty, link, topics, 
                                     added_by, is_approved, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                question_data['title'],
                question_data.get('description'),
                question_data['difficulty'],
                question_data.get('link'),
                topics_json,
                user_id,
                False,  # New questions need approval
                question_data.get('is_public', False)
            ))
            
            question_id = cursor.lastrowid
            conn.commit()
            return question_id
            
        finally:
            conn.close()
    
    def get_question_by_id(self, question_id: int) -> Optional[dict]:
        """Get a question by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT q.*, u.username as added_by_username
                FROM questions q
                LEFT JOIN users u ON q.added_by = u.id
                WHERE q.id = ?
            """, (question_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            question = dict(zip(columns, row))
            
            # Parse topics JSON
            if question['topics']:
                try:
                    question['topics'] = json.loads(question['topics'])
                except:
                    question['topics'] = []
            else:
                question['topics'] = []
            
            # Get company associations
            question['companies'] = self.get_question_companies(question_id)
            
            return question
            
        finally:
            conn.close()
    
    def get_questions(self, page: int = 1, per_page: int = 20, search: str = None, 
                     difficulty: str = None, topic: str = None, user_id: int = None,
                     show_unapproved: bool = False) -> Dict[str, Any]:
        """Get paginated list of questions with filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build WHERE conditions
            where_conditions = []
            params = []
            
            if not show_unapproved:
                where_conditions.append("q.is_approved = 1")
            
            if search:
                where_conditions.append("(q.title LIKE ? OR q.description LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if difficulty:
                where_conditions.append("q.difficulty = ?")
                params.append(difficulty)
            
            if topic:
                where_conditions.append("q.topics LIKE ?")
                params.append(f"%{topic}%")
            
            if user_id:
                where_conditions.append("q.added_by = ?")
                params.append(user_id)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Count total questions
            count_query = f"""
                SELECT COUNT(*) 
                FROM questions q 
                WHERE {where_clause}
            """
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Get questions with pagination
            offset = (page - 1) * per_page
            query = f"""
                SELECT q.*, u.username as added_by_username
                FROM questions q
                LEFT JOIN users u ON q.added_by = u.id
                WHERE {where_clause}
                ORDER BY q.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [per_page, offset])
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            questions = []
            
            for row in rows:
                question = dict(zip(columns, row))
                
                # Parse topics JSON
                if question['topics']:
                    try:
                        question['topics'] = json.loads(question['topics'])
                    except:
                        question['topics'] = []
                else:
                    question['topics'] = []
                
                # Get company associations
                question['companies'] = self.get_question_companies(question['id'])
                
                questions.append(question)
            
            total_pages = (total + per_page - 1) // per_page
            
            return {
                'questions': questions,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
        finally:
            conn.close()
    
    def update_question(self, question_id: int, question_data: dict, user_id: int) -> bool:
        """Update a question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user can edit this question
            cursor.execute("SELECT added_by FROM questions WHERE id = ?", (question_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            # Only allow editing by owner or admin
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            user_role = cursor.fetchone()
            if row[0] != user_id and (not user_role or user_role[0] != 'admin'):
                return False
            
            # Update question
            topics_json = json.dumps(question_data.get('topics', []))
            
            cursor.execute("""
                UPDATE questions 
                SET title = ?, description = ?, difficulty = ?, link = ?, 
                    topics = ?, is_public = ?
                WHERE id = ?
            """, (
                question_data['title'],
                question_data.get('description'),
                question_data['difficulty'],
                question_data.get('link'),
                topics_json,
                question_data.get('is_public', False),
                question_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    def delete_question(self, question_id: int, user_id: int) -> bool:
        """Delete a question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user can delete this question
            cursor.execute("SELECT added_by FROM questions WHERE id = ?", (question_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            # Only allow deletion by owner or admin
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            user_role = cursor.fetchone()
            if row[0] != user_id and (not user_role or user_role[0] != 'admin'):
                return False
            
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    def get_question_companies(self, question_id: int) -> List[dict]:
        """Get company associations for a question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT cq.*, c.name as company_name
                FROM company_questions cq
                JOIN companies c ON cq.company_id = c.id
                WHERE cq.question_id = ?
                ORDER BY cq.frequency DESC
            """, (question_id,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
            
        finally:
            conn.close()
    
    def add_company_association(self, question_id: int, company_data: dict) -> bool:
        """Add company association to a question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO company_questions 
                (company_id, question_id, time_period, frequency)
                VALUES (?, ?, ?, ?)
            """, (
                company_data['company_id'],
                question_id,
                company_data['time_period'],
                company_data.get('frequency', 1.0)
            ))
            
            conn.commit()
            return True
            
        finally:
            conn.close()
    
    def approve_question(self, question_id: int, admin_id: int) -> bool:
        """Approve a question for public visibility"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE questions 
                SET is_approved = 1, is_public = 1
                WHERE id = ?
            """, (question_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    def get_all_topics(self) -> List[str]:
        """Get all unique topics from questions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT topics FROM questions WHERE topics IS NOT NULL")
            rows = cursor.fetchall()
            
            all_topics = set()
            for row in rows:
                if row[0]:
                    try:
                        topics = json.loads(row[0])
                        all_topics.update(topics)
                    except:
                        pass
            
            return sorted(list(all_topics))
            
        finally:
            conn.close()
