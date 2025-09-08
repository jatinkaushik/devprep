"""
Question repository for database operations
"""
from typing import List, Dict, Any, Optional, Tuple
from app.repositories.base_repository import BaseRepository
from app.schemas.question_schemas import QuestionFilters


class QuestionRepository(BaseRepository):
    """Repository for question-related database operations"""
    
    def find_all(self, **kwargs) -> List[Any]:
        """Find all questions"""
        query = "SELECT * FROM questions"
        return self.execute_query(query)
    
    def find_by_id(self, id: int) -> Optional[Any]:
        """Find question by ID"""
        query = "SELECT * FROM questions WHERE id = ?"
        return self.execute_query_one(query, (id,))
    
    def get_filtered_questions(self, filters: QuestionFilters) -> Tuple[List[Dict[str, Any]], int]:
        """Get filtered and paginated questions with total count"""
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        # Company filtering
        if filters.companies:
            company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
            if company_list:
                if filters.company_logic == "AND" and len(company_list) > 1:
                    # AND logic: question must appear with ALL selected companies
                    placeholders = ','.join(['?' for _ in company_list])
                    where_conditions.append(f"c.name IN ({placeholders})")
                    params.extend(company_list)
                else:
                    # OR logic: question appears with ANY of the selected companies
                    placeholders = ','.join(['?' for _ in company_list])
                    where_conditions.append(f"c.name IN ({placeholders})")
                    params.extend(company_list)
        
        # Difficulty filtering
        if filters.difficulties:
            difficulty_list = [x.strip() for x in filters.difficulties.split(',') if x.strip()]
            if difficulty_list:
                placeholders = ','.join(['?' for _ in difficulty_list])
                where_conditions.append(f"q.difficulty IN ({placeholders})")
                params.extend(difficulty_list)
        
        # Time period filtering
        if filters.time_periods:
            time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
            if time_period_list:
                if filters.time_period_logic == "AND" and len(time_period_list) > 1:
                    # AND logic: question must appear with ALL selected time periods
                    placeholders = ','.join(['?' for _ in time_period_list])
                    where_conditions.append(f"cq.time_period IN ({placeholders})")
                    params.extend(time_period_list)
                else:
                    # OR logic: question appears in ANY of the selected time periods
                    placeholders = ','.join(['?' for _ in time_period_list])
                    where_conditions.append(f"cq.time_period IN ({placeholders})")
                    params.extend(time_period_list)
        
        # Topic filtering
        if filters.topics:
            topic_list = [x.strip() for x in filters.topics.split(',') if x.strip()]
            for topic in topic_list:
                where_conditions.append("q.topics LIKE ?")
                params.append(f"%{topic}%")
        
        # Search filtering
        if filters.search:
            where_conditions.append("q.title LIKE ?")
            params.append(f"%{filters.search}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Handle AND logic for companies and time periods if specified
        having_conditions = []
        
        if filters.companies and filters.company_logic == "AND":
            company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
            if len(company_list) > 1:
                having_conditions.append(f"COUNT(DISTINCT c.name) = {len(company_list)}")
        
        if filters.time_periods and filters.time_period_logic == "AND":
            time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
            if len(time_period_list) > 1:
                having_conditions.append(f"COUNT(DISTINCT cq.time_period) = {len(time_period_list)}")
        
        having_clause = f"HAVING {' AND '.join(having_conditions)}" if having_conditions else ""
        
        # Sort clause
        if having_clause:
            # When using GROUP BY, we need to use aggregate functions for non-grouped columns
            sort_columns = {
                "frequency": "MAX(cq.frequency)",
                "title": "q.title",
                "difficulty": "q.difficulty"
            }
        else:
            sort_columns = {
                "frequency": "cq.frequency",
                "title": "q.title",
                "difficulty": "q.difficulty"
            }
        sort_column = sort_columns.get(filters.sort_by, sort_columns["frequency"])
        sort_direction = "ASC" if filters.sort_order == "asc" else "DESC"
        
        # Count total results
        if having_clause:
            count_query = f"""
                SELECT COUNT(*) as total FROM (
                    SELECT q.id
                    FROM questions q
                    JOIN company_questions cq ON q.id = cq.question_id
                    JOIN companies c ON cq.company_id = c.id
                    WHERE {where_clause}
                    GROUP BY q.id
                    {having_clause}
                )
            """
        else:
            count_query = f"""
                SELECT COUNT(DISTINCT q.id) as total
                FROM questions q
                JOIN company_questions cq ON q.id = cq.question_id
                JOIN companies c ON cq.company_id = c.id
                WHERE {where_clause}
            """
        
        total_result = self.execute_query_one(count_query, params)
        total = total_result['total'] if total_result else 0
        
        # Get paginated results
        offset = (filters.page - 1) * filters.per_page
        
        if having_clause:
            questions_query = f"""
                SELECT q.id, q.title, q.difficulty, q.acceptance_rate, q.link, q.topics
                FROM questions q
                JOIN company_questions cq ON q.id = cq.question_id
                JOIN companies c ON cq.company_id = c.id
                WHERE {where_clause}
                GROUP BY q.id, q.title, q.difficulty, q.acceptance_rate, q.link, q.topics
                {having_clause}
                ORDER BY {sort_column} {sort_direction}, q.title
                LIMIT ? OFFSET ?
            """
        else:
            questions_query = f"""
                SELECT DISTINCT q.id, q.title, q.difficulty, q.acceptance_rate, q.link, q.topics
                FROM questions q
                JOIN company_questions cq ON q.id = cq.question_id
                JOIN companies c ON cq.company_id = c.id
                WHERE {where_clause}
                ORDER BY {sort_column} {sort_direction}, q.title
                LIMIT ? OFFSET ?
            """
        
        questions = self.execute_query(questions_query, params + [filters.per_page, offset])
        
        return questions, total
    
    def get_company_data_for_questions(self, question_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        """Get company data for specific questions"""
        if not question_ids:
            return {}
        
        placeholders = ','.join(['?' for _ in question_ids])
        query = f"""
            SELECT cq.question_id, c.name as company_name, cq.frequency, cq.time_period
            FROM company_questions cq
            JOIN companies c ON cq.company_id = c.id
            WHERE cq.question_id IN ({placeholders})
            ORDER BY cq.frequency DESC
        """
        
        results = self.execute_query(query, question_ids)
        
        # Group by question_id
        company_data = {}
        for row in results:
            question_id = row['question_id']
            if question_id not in company_data:
                company_data[question_id] = []
            company_data[question_id].append(row)
        
        return company_data
    
    def get_filter_stats(self, filters: QuestionFilters) -> Dict[str, Any]:
        """Get statistics for current filters"""
        # Use same filtering logic as get_filtered_questions but without pagination
        where_conditions = []
        params = []
        
        # Apply same filters as in get_filtered_questions
        if filters.companies:
            company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
            if company_list:
                placeholders = ','.join(['?' for _ in company_list])
                where_conditions.append(f"c.name IN ({placeholders})")
                params.extend(company_list)
        
        if filters.difficulties:
            difficulty_list = [x.strip() for x in filters.difficulties.split(',') if x.strip()]
            if difficulty_list:
                placeholders = ','.join(['?' for _ in difficulty_list])
                where_conditions.append(f"q.difficulty IN ({placeholders})")
                params.extend(difficulty_list)
        
        if filters.time_periods:
            time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
            if time_period_list:
                placeholders = ','.join(['?' for _ in time_period_list])
                where_conditions.append(f"cq.time_period IN ({placeholders})")
                params.extend(time_period_list)
        
        if filters.topics:
            topic_list = [x.strip() for x in filters.topics.split(',') if x.strip()]
            for topic in topic_list:
                where_conditions.append("q.topics LIKE ?")
                params.append(f"%{topic}%")
        
        if filters.search:
            where_conditions.append("q.title LIKE ?")
            params.append(f"%{filters.search}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Handle AND logic
        having_conditions = []
        
        if filters.companies and filters.company_logic == "AND":
            company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
            if len(company_list) > 1:
                having_conditions.append(f"COUNT(DISTINCT c.name) = {len(company_list)}")
        
        if filters.time_periods and filters.time_period_logic == "AND":
            time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
            if len(time_period_list) > 1:
                having_conditions.append(f"COUNT(DISTINCT cq.time_period) = {len(time_period_list)}")
        
        having_clause = f"HAVING {' AND '.join(having_conditions)}" if having_conditions else ""
        
        if having_clause:
            stats_query = f"""
                SELECT 
                    COUNT(*) as total_questions,
                    SUM(CASE WHEN filtered_questions.difficulty = 'EASY' THEN 1 ELSE 0 END) as easy_count,
                    SUM(CASE WHEN filtered_questions.difficulty = 'MEDIUM' THEN 1 ELSE 0 END) as medium_count,
                    SUM(CASE WHEN filtered_questions.difficulty = 'HARD' THEN 1 ELSE 0 END) as hard_count
                FROM (
                    SELECT DISTINCT q.id, q.difficulty
                    FROM questions q
                    JOIN company_questions cq ON q.id = cq.question_id
                    JOIN companies c ON cq.company_id = c.id
                    WHERE {where_clause}
                    GROUP BY q.id, q.difficulty
                    {having_clause}
                ) AS filtered_questions
            """
        else:
            stats_query = f"""
                SELECT 
                    COUNT(DISTINCT id) as total_questions,
                    SUM(CASE WHEN difficulty = 'EASY' THEN 1 ELSE 0 END) as easy_count,
                    SUM(CASE WHEN difficulty = 'MEDIUM' THEN 1 ELSE 0 END) as medium_count,
                    SUM(CASE WHEN difficulty = 'HARD' THEN 1 ELSE 0 END) as hard_count
                FROM (
                    SELECT DISTINCT q.id, q.difficulty
                    FROM questions q
                    JOIN company_questions cq ON q.id = cq.question_id
                    JOIN companies c ON cq.company_id = c.id
                    WHERE {where_clause}
                ) AS unique_questions
            """
        
        stats = self.execute_query_one(stats_query, params)
        
        # Get companies count
        companies_query = f"""
            SELECT COUNT(DISTINCT c.name) as companies_count
            FROM questions q
            JOIN company_questions cq ON q.id = cq.question_id
            JOIN companies c ON cq.company_id = c.id
            WHERE {where_clause}
        """
        
        companies_result = self.execute_query_one(companies_query, params)
        
        # Get unique time periods
        time_periods_query = f"""
            SELECT DISTINCT cq.time_period
            FROM questions q
            JOIN company_questions cq ON q.id = cq.question_id
            JOIN companies c ON cq.company_id = c.id
            WHERE {where_clause}
            ORDER BY cq.time_period
        """
        
        time_periods_results = self.execute_query(time_periods_query, params)
        unique_time_periods = [row['time_period'] for row in time_periods_results]
        
        # Get unique topics
        topics_query = f"""
            SELECT DISTINCT q.topics
            FROM questions q
            JOIN company_questions cq ON q.id = cq.question_id
            JOIN companies c ON cq.company_id = c.id
            WHERE {where_clause} AND q.topics IS NOT NULL AND q.topics != ''
        """
        
        topics_results = self.execute_query(topics_query, params)
        topics_set = set()
        for row in topics_results:
            if row['topics']:
                topic_list = [topic.strip() for topic in row['topics'].split(',')]
                topics_set.update(topic_list)
        
        return {
            'total_questions': stats['total_questions'] or 0,
            'easy_count': stats['easy_count'] or 0,
            'medium_count': stats['medium_count'] or 0,
            'hard_count': stats['hard_count'] or 0,
            'companies_count': companies_result['companies_count'] or 0,
            'time_periods': unique_time_periods,
            'topics': sorted(list(topics_set))
        }
