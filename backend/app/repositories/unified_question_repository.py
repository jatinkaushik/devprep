"""
Unified Question repository for database operations using single questions table
"""
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from app.repositories.base_repository import BaseRepository
from app.utils.logging import logger
from app.schemas.question_schemas import QuestionFilters


class UnifiedQuestionRepository(BaseRepository):
    """Repository for unified question database operations"""
    
    def get_filtered_questions(self, filters: QuestionFilters, user_id: Optional[int] = None) -> Tuple[List[Dict], int]:
        """Get filtered questions with pagination"""
        try:
            where_conditions = []
            params = []
            
            # Base condition: show approved questions, or user's own questions
            if user_id:
                where_conditions.append("(q.is_approved = 1 OR q.added_by = ?)")
                params.append(user_id)
            else:
                where_conditions.append("q.is_approved = 1")
            
            # Public visibility filter
            if user_id:
                where_conditions.append("(q.is_public = 1 OR q.added_by = ?)")
                params.append(user_id)
            else:
                where_conditions.append("q.is_public = 1")
            
            # Search filter
            if filters.search:
                where_conditions.append("q.title LIKE ?")
                params.append(f"%{filters.search}%")
            
            # Difficulty filter
            if filters.difficulties:
                difficulties = [d.strip() for d in filters.difficulties.split(',')]
                difficulty_placeholders = ','.join(['?' for _ in difficulties])
                where_conditions.append(f"q.difficulty IN ({difficulty_placeholders})")
                params.extend(difficulties)
            
            # Topics filter
            if filters.topics:
                topics = [t.strip() for t in filters.topics.split(',')]
                topic_conditions = []
                for topic in topics:
                    topic_conditions.append("q.topics LIKE ?")
                    params.append(f"%{topic}%")
                where_conditions.append(f"({' OR '.join(topic_conditions)})")
            
            # Build company and time period filters
            company_where = ""
            if filters.companies or filters.time_periods:
                company_conditions = []
                
                if filters.companies:
                    companies = [c.strip() for c in filters.companies.split(',')]
                    company_placeholders = ','.join(['?' for _ in companies])
                    company_conditions.append(f"c.name IN ({company_placeholders})")
                    params.extend(companies)
                
                if filters.time_periods:
                    time_periods = [tp.strip() for tp in filters.time_periods.split(',')]
                    tp_placeholders = ','.join(['?' for _ in time_periods])
                    company_conditions.append(f"cq.time_period IN ({tp_placeholders})")
                    params.extend(time_periods)
                
                if company_conditions:
                    logic_op = " AND " if filters.company_logic.value == "AND" else " OR "
                    company_where = f"AND EXISTS (SELECT 1 FROM company_questions cq JOIN companies c ON cq.company_id = c.id WHERE cq.question_id = q.id AND ({logic_op.join(company_conditions)}))"
            
            where_clause = "WHERE " + " AND ".join(where_conditions) + company_where
            
            # Count total results
            count_query = f"""
                SELECT COUNT(DISTINCT q.id) 
                FROM questions q 
                {where_clause}
            """
            
            total = self.execute_query(count_query, params, fetch_one=True)[0]
            
            # Main query with pagination
            offset = (filters.page - 1) * filters.per_page
            
            # Determine sort order
            sort_column = "q.title"
            if filters.sort_by.value == "difficulty":
                sort_column = "CASE q.difficulty WHEN 'Easy' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Hard' THEN 3 END"
            elif filters.sort_by.value == "frequency":
                sort_column = "COALESCE(MAX(cq.frequency), 0)"
            
            sort_order = "ASC" if filters.sort_order.value == "asc" else "DESC"
            
            query = f"""
                SELECT DISTINCT q.id, q.title, q.difficulty, q.acceptance_rate, 
                       q.link, q.topics, q.description, q.added_by, 
                       q.is_approved, q.is_public, q.created_at
                FROM questions q
                LEFT JOIN company_questions cq ON q.id = cq.question_id
                LEFT JOIN companies c ON cq.company_id = c.id
                {where_clause}
                GROUP BY q.id, q.title, q.difficulty, q.acceptance_rate, 
                         q.link, q.topics, q.description, q.added_by, 
                         q.is_approved, q.is_public, q.created_at
                ORDER BY {sort_column} {sort_order}
                LIMIT ? OFFSET ?
            """
            
            params.extend([filters.per_page, offset])
            results = self.execute_query(query, params)
            
            questions = []
            for row in results:
                questions.append({
                    'id': row[0],
                    'title': row[1],
                    'difficulty': row[2],
                    'acceptance_rate': row[3],
                    'link': row[4],
                    'topics': row[5],
                    'description': row[6],
                    'added_by': row[7],
                    'is_approved': row[8],
                    'is_public': row[9],
                    'created_at': row[10]
                })
            
            logger.info(f"Retrieved {len(questions)} questions out of {total} total")
            return questions, total
            
        except Exception as e:
            logger.error(f"Error in get_filtered_questions: {e}")
            raise

    def get_company_data_for_questions(self, question_ids: List[int]) -> Dict[int, List[Dict]]:
        """Get company associations for a list of questions"""
        try:
            if not question_ids:
                return {}
            
            placeholders = ','.join(['?' for _ in question_ids])
            query = f"""
                SELECT cq.question_id, c.id as company_id, c.name as company_name, 
                       cq.time_period, cq.frequency
                FROM company_questions cq
                JOIN companies c ON cq.company_id = c.id
                WHERE cq.question_id IN ({placeholders})
                ORDER BY cq.question_id, c.name
            """
            
            results = self.execute_query(query, question_ids)
            
            company_data = {}
            for row in results:
                question_id = row[0]
                if question_id not in company_data:
                    company_data[question_id] = []
                
                company_data[question_id].append({
                    'company_id': row[1],
                    'company_name': row[2],
                    'time_period': row[3],
                    'frequency': row[4]
                })
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error getting company data: {e}")
            return {}

    def create_question(self, question_data: Dict[str, Any]) -> int:
        """Create a new question"""
        try:
            query = """
                INSERT INTO questions (title, difficulty, link, topics, description, 
                                     added_by, is_approved, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = [
                question_data['title'],
                question_data['difficulty'],
                question_data['link'],
                question_data.get('topics'),
                question_data.get('description'),
                question_data['added_by'],
                question_data.get('is_approved', False),
                question_data.get('is_public', False)
            ]
            
            return self.execute_insert(query, params)
            
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            raise

    def get_user_questions(self, user_id: int, page: int = 1, per_page: int = 20) -> Tuple[List[Dict], int]:
        """Get questions created by a specific user"""
        try:
            # Count total user questions
            count_query = "SELECT COUNT(*) FROM questions WHERE added_by = ?"
            total = self.execute_query(count_query, [user_id], fetch_one=True)[0]
            
            # Get paginated user questions
            offset = (page - 1) * per_page
            query = """
                SELECT id, title, difficulty, acceptance_rate, link, topics, 
                       description, added_by, is_approved, is_public, created_at
                FROM questions 
                WHERE added_by = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            
            results = self.execute_query(query, [user_id, per_page, offset])
            
            questions = []
            for row in results:
                questions.append({
                    'id': row[0],
                    'title': row[1],
                    'difficulty': row[2],
                    'acceptance_rate': row[3],
                    'link': row[4],
                    'topics': row[5],
                    'description': row[6],
                    'added_by': row[7],
                    'is_approved': row[8],
                    'is_public': row[9],
                    'created_at': row[10]
                })
            
            return questions, total
            
        except Exception as e:
            logger.error(f"Error getting user questions: {e}")
            raise

    def get_question_by_id(self, question_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a specific question by ID"""
        try:
            query = """
                SELECT id, title, difficulty, acceptance_rate, link, topics, 
                       description, added_by, is_approved, is_public, created_at
                FROM questions 
                WHERE id = ?
            """
            
            result = self.execute_query(query, [question_id], fetch_one=True)
            
            if not result:
                return None
            
            question = {
                'id': result[0],
                'title': result[1],
                'difficulty': result[2],
                'acceptance_rate': result[3],
                'link': result[4],
                'topics': result[5],
                'description': result[6],
                'added_by': result[7],
                'is_approved': result[8],
                'is_public': result[9],
                'created_at': result[10]
            }
            
            # Check visibility permissions
            if not question['is_approved'] and question['added_by'] != user_id:
                return None
            
            if not question['is_public'] and question['added_by'] != user_id:
                return None
            
            return question
            
        except Exception as e:
            logger.error(f"Error getting question by ID: {e}")
            raise

    def update_question(self, question_id: int, question_data: Dict[str, Any]) -> bool:
        """Update a question"""
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            
            for key, value in question_data.items():
                if key in ['title', 'difficulty', 'link', 'topics', 'description', 'is_public']:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            params.append(question_id)
            
            query = f"""
                UPDATE questions 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """
            
            return self.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Error updating question: {e}")
            raise

    def delete_question(self, question_id: int) -> bool:
        """Delete a question"""
        try:
            query = "DELETE FROM questions WHERE id = ?"
            return self.execute_update(query, [question_id])
            
        except Exception as e:
            logger.error(f"Error deleting question: {e}")
            raise

    def get_all_topics(self) -> List[str]:
        """Get all unique topics from questions"""
        try:
            query = "SELECT DISTINCT topics FROM questions WHERE topics IS NOT NULL AND topics != ''"
            results = self.execute_query(query)
            
            topics = set()
            for row in results:
                if row[0]:
                    try:
                        topic_list = json.loads(row[0])
                        topics.update(topic_list)
                    except:
                        # Handle legacy comma-separated topics
                        topic_list = row[0].split(',')
                        topics.update([t.strip() for t in topic_list if t.strip()])
            
            return sorted(list(topics))
            
        except Exception as e:
            logger.error(f"Error getting all topics: {e}")
            return []

    def get_all_time_periods(self) -> List[str]:
        """Get all time periods from company associations"""
        try:
            query = "SELECT DISTINCT time_period FROM company_questions ORDER BY time_period DESC"
            results = self.execute_query(query)
            
            return [row[0] for row in results if row[0]]
            
        except Exception as e:
            logger.error(f"Error getting all time periods: {e}")
            return []

    def add_company_association(self, question_id: int, company_id: int, time_period: str, frequency: float = 1.0) -> int:
        """Add a company association to a question"""
        try:
            query = """
                INSERT INTO company_questions (question_id, company_id, time_period, frequency)
                VALUES (?, ?, ?, ?)
            """
            
            return self.execute_insert(query, [question_id, company_id, time_period, frequency])
            
        except Exception as e:
            logger.error(f"Error adding company association: {e}")
            raise

    def remove_company_association(self, question_id: int, company_id: int, time_period: str) -> bool:
        """Remove a company association from a question"""
        try:
            query = """
                DELETE FROM company_questions 
                WHERE question_id = ? AND company_id = ? AND time_period = ?
            """
            
            return self.execute_update(query, [question_id, company_id, time_period])
            
        except Exception as e:
            logger.error(f"Error removing company association: {e}")
            raise

    def get_company_associations(self, question_id: int) -> List[Dict[str, Any]]:
        """Get all company associations for a question"""
        try:
            query = """
                SELECT cq.id, cq.company_id, c.name as company_name, 
                       cq.time_period, cq.frequency
                FROM company_questions cq
                JOIN companies c ON cq.company_id = c.id
                WHERE cq.question_id = ?
                ORDER BY c.name, cq.time_period
            """
            
            results = self.execute_query(query, [question_id])
            
            associations = []
            for row in results:
                associations.append({
                    'id': row[0],
                    'company_id': row[1],
                    'company_name': row[2],
                    'time_period': row[3],
                    'frequency': row[4]
                })
            
            return associations
            
        except Exception as e:
            logger.error(f"Error getting company associations: {e}")
            return []
