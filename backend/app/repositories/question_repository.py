"""
Question repository for database operations
"""
from typing import List, Dict, Any, Optional, Tuple
from app.repositories.base_repository import BaseRepository
from app.schemas.question_schemas import QuestionFilters
from app.utils.logging import logger, log_exception


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
    
    def get_all_questions_unified(self, filters: QuestionFilters, user_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
        """Get all questions (regular + user questions) with unified filtering"""
        logger.info(f"Getting all questions with filters: {filters}, user_id: {user_id}")
        
        try:
            # Build base filters for both question types
            where_conditions = []
            params = []
            
            # Difficulty filtering
            if filters.difficulties:
                difficulty_list = [x.strip() for x in filters.difficulties.split(',') if x.strip()]
                if difficulty_list:
                    placeholders = ','.join(['?' for _ in difficulty_list])
                    where_conditions.append(f"difficulty IN ({placeholders})")
                    params.extend(difficulty_list)
            
            # Topic filtering
            if filters.topics:
                topic_list = [x.strip() for x in filters.topics.split(',') if x.strip()]
                for topic in topic_list:
                    where_conditions.append("topics LIKE ?")
                    params.append(f"%{topic}%")
            
            # Search filtering
            if filters.search:
                where_conditions.append("title LIKE ?")
                params.append(f"%{filters.search}%")
            
            # User visibility conditions
            user_condition = ""
            if user_id:
                user_condition = f" OR (source = 'user' AND (is_public = 0 OR created_by = {user_id}))"
            
            base_where = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Create unified query
            unified_query = f"""
            WITH unified_questions AS (
                -- Regular questions
                SELECT 
                    q.id,
                    q.title,
                    q.difficulty,
                    q.acceptance_rate,
                    q.link,
                    q.topics,
                    q.created_at,
                    q.description,
                    q.solution,
                    q.added_by,
                    q.is_approved,
                    q.is_public,
                    0 as max_frequency,  -- Will be overridden with actual frequency data
                    'regular' as source,
                    'System' as author,
                    q.id as original_id,
                    NULL as user_question_id
                FROM questions q
                
                UNION ALL
                
                -- User questions
                SELECT 
                    1000000 + uq.id as id,  -- Offset to avoid ID conflicts
                    uq.title,
                    UPPER(uq.difficulty) as difficulty,
                    NULL as acceptance_rate,  -- User questions don't have acceptance rate
                    COALESCE(uq.link, '#') as link,  -- Use actual link or placeholder
                    uq.topics,
                    uq.created_at,
                    uq.description,
                    NULL as solution,  -- User questions don't have solutions
                    uq.created_by as added_by,
                    uq.is_approved,
                    uq.is_public,
                    0 as max_frequency,  -- User questions don't have frequency data
                    'user' as source,
                    u.username as author,
                    NULL as original_id,
                    uq.id as user_question_id
                FROM user_questions uq
                JOIN users u ON uq.created_by = u.id
                WHERE (uq.is_public = 1 AND uq.is_approved = 1){user_condition}
            )
            SELECT * FROM unified_questions 
            WHERE {base_where}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """
            
            # Add pagination params
            offset = (filters.page - 1) * filters.per_page
            query_params = params + [filters.per_page, offset]
            
            # Get questions
            questions = self.execute_query(unified_query, query_params)
            
            # Convert boolean fields
            for question in questions:
                if 'is_approved' in question:
                    question['is_approved'] = bool(question['is_approved'])
                if 'is_public' in question:
                    question['is_public'] = bool(question['is_public'])
        
            # Count total
            count_query = f"""
        WITH unified_questions AS (
            SELECT 
                q.id,
                q.title,
                q.difficulty,
                q.acceptance_rate,
                q.link,
                q.topics,
                'regular' as source,
                1 as is_public,
                1 as is_approved,
                NULL as created_by
            FROM questions q
            
            UNION ALL
            
            SELECT 
                1000000 + uq.id as id,
                uq.title,
                uq.difficulty,
                NULL as acceptance_rate,
                '#' as link,
                uq.topics,
                'user' as source,
                uq.is_public,
                uq.is_approved,
                uq.created_by
            FROM user_questions uq
            WHERE (uq.is_public = 1 AND uq.is_approved = 1){user_condition}
        )
        SELECT COUNT(*) as total FROM unified_questions 
        WHERE {base_where}
        """
            
            total_result = self.execute_query_one(count_query, params)
            total = total_result['total'] if total_result else 0
            
            return questions, total
        
        except Exception as e:
            error_msg = log_exception(e, "Failed to get all questions unified")
            logger.error(f"SQL Query params: {params}")
            raise
    
    def get_filtered_questions(self, filters: QuestionFilters, user_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
        """Get filtered and paginated questions with total count - original method"""
        logger.info(f"Repository: Getting filtered questions with filters: {filters}, user_id: {user_id}")
        
        try:
            # Build WHERE clause
            where_conditions = []
            params = []
            
            # Company filtering
            if filters.companies:
                logger.debug(f"Applying company filter: {filters.companies}")
                company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
                if company_list:
                    placeholders = ','.join(['?' for _ in company_list])
                    where_conditions.append(f"c.name IN ({placeholders})")
                    params.extend(company_list)
            
            # Difficulty filtering
            if filters.difficulties:
                logger.debug(f"Applying difficulty filter: {filters.difficulties}")
                difficulty_list = [x.strip() for x in filters.difficulties.split(',') if x.strip()]
                if difficulty_list:
                    placeholders = ','.join(['?' for _ in difficulty_list])
                    where_conditions.append(f"q.difficulty IN ({placeholders})")
                    params.extend(difficulty_list)
            
            # Time period filtering
            if filters.time_periods:
                logger.debug(f"Applying time period filter: {filters.time_periods}")
                time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
                if time_period_list:
                    placeholders = ','.join(['?' for _ in time_period_list])
                    where_conditions.append(f"cq.time_period IN ({placeholders})")
                    params.extend(time_period_list)
            
            # Topic filtering
            if filters.topics:
                logger.debug(f"Applying topic filter: {filters.topics}")
                topic_list = [x.strip() for x in filters.topics.split(',') if x.strip()]
                for topic in topic_list:
                    where_conditions.append("q.topics LIKE ?")
                    params.append(f"%{topic}%")
            
            # Search filtering
            if filters.search:
                logger.debug(f"Applying search filter: {filters.search}")
                where_conditions.append("q.title LIKE ?")
                params.append(f"%{filters.search}%")
                
            # Build the WHERE clause
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            logger.debug(f"Where clause: {where_clause}")
            
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
            logger.debug(f"Having clause: {having_clause}")
            
            # Sort field and order
            sort_field = {
                "FREQUENCY": "MAX(cq.frequency)",
                "TITLE": "q.title",
                "DIFFICULTY": "CASE q.difficulty WHEN 'EASY' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'HARD' THEN 3 END"
            }.get(filters.sort_by, "MAX(cq.frequency)")
            
            sort_direction = "ASC" if filters.sort_order == "ASC" else "DESC"
            
            # Main query to get questions
            query = f"""
            SELECT DISTINCT 
                q.id,
                q.title,
                q.difficulty,
                q.acceptance_rate,
                q.link,
                q.topics,
                q.created_at,
                q.added_by,
                q.is_approved,
                q.description,
                q.solution,
                q.is_public,
                MAX(cq.frequency) as max_frequency
            FROM 
                questions q
                JOIN company_questions cq ON q.id = cq.question_id
                JOIN companies c ON cq.company_id = c.id
            WHERE {where_clause}
            GROUP BY q.id
            {having_clause}
            ORDER BY {sort_field} {sort_direction}, q.id DESC
            LIMIT ? OFFSET ?
            """
            
            # Pagination
            offset = (filters.page - 1) * filters.per_page
            query_params = params + [filters.per_page, offset]
            
            logger.debug(f"Executing main query: {query}")
            logger.debug(f"Query params: {query_params}")
            
            questions = self.execute_query(query, query_params)
            logger.info(f"Retrieved {len(questions)} questions")
            
            # Convert boolean fields for main questions
            for question in questions:
                question['is_approved'] = bool(question['is_approved'])
                question['is_public'] = bool(question['is_public'])
            
            # Count total
            count_query = f"""
            SELECT COUNT(DISTINCT q.id) as total
            FROM 
                questions q
                JOIN company_questions cq ON q.id = cq.question_id
                JOIN companies c ON cq.company_id = c.id
            WHERE {where_clause}
            """
            
            if having_conditions:
                count_query = f"""
                SELECT COUNT(*) as total
                FROM (
                    SELECT q.id
                    FROM 
                        questions q
                        JOIN company_questions cq ON q.id = cq.question_id
                        JOIN companies c ON cq.company_id = c.id
                    WHERE {where_clause}
                    GROUP BY q.id
                    {having_clause}
                ) AS filtered_count
                """
            
            logger.debug(f"Executing count query: {count_query}")
            total_result = self.execute_query_one(count_query, params)
            total = total_result['total'] if total_result else 0
            logger.info(f"Total matching questions: {total}")
            
            return questions, total
            
        except Exception as e:
            error_msg = log_exception(e, "Failed to get filtered questions")
            logger.error(f"SQL Query params: {params}")
            raise
    
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
    
    def _build_base_question_conditions(self, filters: QuestionFilters) -> Tuple[List[str], List[Any]]:
        """Build base WHERE conditions for questions table"""
        conditions = []
        params = []
        
        # Difficulty filtering
        if filters.difficulties:
            difficulty_list = [x.strip() for x in filters.difficulties.split(',') if x.strip()]
            if difficulty_list:
                placeholders = ','.join(['?' for _ in difficulty_list])
                conditions.append(f"q.difficulty IN ({placeholders})")
                params.extend(difficulty_list)
        
        # Topic filtering
        if filters.topics:
            topic_list = [x.strip() for x in filters.topics.split(',') if x.strip()]
            topic_conditions = []
            for topic in topic_list:
                topic_conditions.append("q.topics LIKE ?")
                params.append(f"%{topic}%")
            if topic_conditions:
                conditions.append("(" + " OR ".join(topic_conditions) + ")")
        
        # Search filtering
        if filters.search:
            conditions.append("q.title LIKE ?")
            params.append(f"%{filters.search}%")
        
        return conditions, params
    
    def _build_company_conditions(self, filters: QuestionFilters) -> Tuple[List[str], List[Any]]:
        """Build company-related WHERE conditions"""
        conditions = []
        params = []
        
        # Company filtering
        if filters.companies:
            company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
            if company_list:
                company_conditions = []
                for company in company_list:
                    company_conditions.append("c.name = ?")
                    params.append(company)
                
                # Apply AND/OR logic for multiple companies
                if company_conditions:
                    logic_operator = " AND " if filters.company_logic == "AND" else " OR "
                    conditions.append("(" + logic_operator.join(company_conditions) + ")")
        
        # Time period filtering
        if filters.time_periods:
            time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
            if time_period_list:
                time_period_conditions = []
                for period in time_period_list:
                    time_period_conditions.append("qc.time_period = ?")
                    params.append(period)
                
                # Apply AND/OR logic for time periods
                if time_period_conditions:
                    logic_operator = " AND " if filters.time_period_logic == "AND" else " OR "
                    conditions.append("(" + logic_operator.join(time_period_conditions) + ")")
        
        return conditions, params
        
    def get_random_questions(self, filters: QuestionFilters, count: int, user_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
        """Get random questions based on filters"""
        logger.info(f"Getting random questions with count: {count}, filters: {filters}, user_id: {user_id}")
        
        # Build the query parts similar to get_filtered_questions but with random ordering
        base_conditions, base_params = self._build_base_question_conditions(filters)
        company_conditions, company_params = self._build_company_conditions(filters)
        
        # Main selection query
        select_query = """
            SELECT 
                q.id, q.title, q.difficulty, q.acceptance_rate, q.link, q.topics, 
                q.description, q.added_by, q.is_approved, q.is_public
            FROM 
                questions q
        """
        
        # Add company join if needed
        if company_conditions:
            select_query += """
                INNER JOIN question_companies qc ON q.id = qc.question_id
                INNER JOIN companies c ON qc.company_id = c.id
            """
        
        # Add WHERE clause
        where_clauses = []
        params = []
        
        # Add base conditions
        if base_conditions:
            where_clauses.extend(base_conditions)
            params.extend(base_params)
        
        # Add company conditions
        if company_conditions:
            where_clauses.extend(company_conditions)
            params.extend(company_params)
        
        # Combine all conditions
        if where_clauses:
            select_query += " WHERE " + " AND ".join(where_clauses)
        
        # Add GROUP BY if we're using company joins
        if company_conditions:
            select_query += " GROUP BY q.id"
        
        # Get total count before applying limit/random
        count_query = f"SELECT COUNT(*) FROM ({select_query}) as filtered_questions"
        
        try:
            total_row = self.execute_query_one(count_query, params)
            total = total_row['COUNT(*)'] if total_row else 0
            
            # Add random ordering and limit
            select_query += " ORDER BY RANDOM() LIMIT ?"
            params.append(count)
            
            # Execute the main query
            questions = self.execute_query(select_query, params)
            
            # Include user questions if logged in
            user_questions = []
            user_questions_total = 0
            
            if user_id is not None:
                user_questions, user_questions_total = self._get_random_user_questions(filters, count, user_id)
            
            # Return combined results
            return list(questions) + user_questions, total + user_questions_total
            
        except Exception as e:
            logger.error(f"Error getting random questions: {str(e)}")
            raise e
    
    def _get_random_user_questions(self, filters: QuestionFilters, count: int, user_id: int) -> Tuple[List[Dict[str, Any]], int]:
        """Helper method to get random user questions"""
        select_fields = """
            q.id, q.title, q.difficulty, NULL as acceptance_rate, q.link, q.topics, 
            q.description, q.created_by, q.is_approved, q.is_public, q.created_at
        """
        
        from_clause = """
            FROM user_questions q
        """
        
        # Build where conditions
        where_conditions = []
        params = []
        
        # Add visibility conditions (public or owned)
        where_conditions.append("(q.is_public = 1 OR (q.created_by = ? AND q.is_approved = 1))")
        params.append(user_id)
        
        # Add difficulty filter
        if filters.difficulties:
            difficulty_list = [x.strip() for x in filters.difficulties.split(',') if x.strip()]
            if difficulty_list:
                placeholders = ','.join(['?' for _ in difficulty_list])
                where_conditions.append(f"q.difficulty IN ({placeholders})")
                params.extend(difficulty_list)
        
        # Add topic filter
        if filters.topics:
            topic_list = [x.strip() for x in filters.topics.split(',') if x.strip()]
            topic_conditions = []
            for topic in topic_list:
                topic_conditions.append("q.topics LIKE ?")
                params.append(f"%{topic}%")
            where_conditions.append("(" + " OR ".join(topic_conditions) + ")")
        
        # Add search filter
        if filters.search:
            where_conditions.append("q.title LIKE ?")
            params.append(f"%{filters.search}%")
        
        # Combine conditions
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM user_questions q {where_clause}"
        
        try:
            total_row = self.execute_query_one(count_query, params)
            total = total_row['COUNT(*)'] if total_row else 0
            
            # Build final query with random order and limit
            query = f"SELECT {select_fields} {from_clause} {where_clause} ORDER BY RANDOM() LIMIT ?"
            params.append(count)
            
            # Execute query
            user_questions = self.execute_query(query, params)
            return list(user_questions), total
            
        except Exception as e:
            logger.error(f"Error getting random user questions: {str(e)}")
            raise e
            
    def get_user_questions_for_display(self, filters: QuestionFilters, user_id: Optional[int] = None) -> Tuple[List[Dict[str, Any]], int]:
        """Get user questions based on filtering for display in main question list"""
        # This returns user questions that should be displayed based on filter criteria
        # We also respect visibility rules - public and own questions
        logger.info(f"Getting filtered user questions for display with user_id: {user_id}")
        
        try:
            select_fields = """
                q.id + 1000000 as id, q.title, q.difficulty, NULL as acceptance_rate, q.link, q.topics, 
                q.description, q.created_by as added_by, q.is_approved, q.is_public, q.created_at
            """
            
            from_clause = """
                FROM user_questions q
                LEFT JOIN user_question_companies uqc ON q.id = uqc.user_question_id
                LEFT JOIN companies c ON uqc.company_id = c.id
            """
            
            where_conditions = []
            params = []
            
            # Visibility rules: show public questions or own questions
            if user_id:
                where_conditions.append("(q.is_public = 1 OR q.created_by = ?)")
                params.append(user_id)
            else:
                where_conditions.append("q.is_public = 1")
            
            # Apply filters
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
                    where_conditions.append(f"uqc.time_period IN ({placeholders})")
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
            
            # Handle AND logic for companies and time periods
            having_conditions = []
            
            if filters.companies and filters.company_logic == "AND":
                company_list = [x.strip() for x in filters.companies.split(',') if x.strip()]
                if len(company_list) > 1:
                    having_conditions.append(f"COUNT(DISTINCT c.name) = {len(company_list)}")
            
            if filters.time_periods and filters.time_period_logic == "AND":
                time_period_list = [x.strip() for x in filters.time_periods.split(',') if x.strip()]
                if len(time_period_list) > 1:
                    having_conditions.append(f"COUNT(DISTINCT uqc.time_period) = {len(time_period_list)}")
            
            having_clause = f"HAVING {' AND '.join(having_conditions)}" if having_conditions else ""
            
            # Build the main query
            if having_clause:
                query = f"""
                    SELECT DISTINCT {select_fields.strip()}
                    {from_clause.strip()}
                    WHERE {where_clause}
                    GROUP BY q.id, q.title, q.difficulty, q.link, q.topics, q.description, q.created_by, q.is_approved, q.is_public, q.created_at
                    {having_clause}
                    ORDER BY q.created_at DESC
                    LIMIT ? OFFSET ?
                """
            else:
                query = f"""
                    SELECT DISTINCT {select_fields.strip()}
                    {from_clause.strip()}
                    WHERE {where_clause}
                    ORDER BY q.created_at DESC
                    LIMIT ? OFFSET ?
                """
            
            # Add pagination parameters
            params.extend([filters.per_page, (filters.page - 1) * filters.per_page])
            
            user_questions = self.execute_query(query, params)
            
            # Get total count
            count_query = f"""
                SELECT COUNT(DISTINCT q.id) as total
                FROM user_questions q
                LEFT JOIN user_question_companies uqc ON q.id = uqc.user_question_id
                LEFT JOIN companies c ON uqc.company_id = c.id
                WHERE {where_clause}
            """
            
            # Remove pagination params for count query
            count_params = params[:-2]
            if having_clause:
                count_query += f" GROUP BY q.id {having_clause}"
                count_result = self.execute_query(count_query, count_params)
                total = len(count_result)
            else:
                count_result = self.execute_query_one(count_query, count_params)
                total = count_result['total'] if count_result else 0
            
            logger.debug(f"Retrieved {len(user_questions)} user questions out of {total} total")
            return user_questions, total
            
        except Exception as e:
            logger.error(f"Error getting user questions for display: {str(e)}")
            raise
    
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
    
    def get_all_topics(self) -> List[str]:
        """Get all unique topics from questions"""
        try:
            query = """
                SELECT DISTINCT topics
                FROM questions
                WHERE topics IS NOT NULL AND topics != ''
                UNION
                SELECT DISTINCT topics
                FROM user_questions
                WHERE topics IS NOT NULL AND topics != '' AND is_public = 1
            """
            
            results = self.execute_query(query)
            topics_set = set()
            
            for row in results:
                if row['topics']:
                    topic_list = [topic.strip() for topic in row['topics'].split(',') if topic.strip()]
                    topics_set.update(topic_list)
            
            return sorted(list(topics_set))
        except Exception as e:
            logger.error(f"Error getting all topics: {str(e)}")
            raise
