"""
Question service for business logic
"""
from typing import List, Dict, Any, Optional
from app.services.base_service import BaseService
from app.repositories.question_repository import QuestionRepository
from app.repositories.company_repository import CompanyRepository
from app.utils.logging import logger, log_exception
from app.schemas.question_schemas import (
    QuestionFilters, QuestionResponse, Question, GroupedCompanyQuestion,
    FilterStats, CompanyData, OverallStats
)


class QuestionService(BaseService):
    """Service for question-related business logic"""
    
    def __init__(self):
        super().__init__()
        self.question_repo = QuestionRepository()
        self.company_repo = CompanyRepository()
    
    def get_filtered_questions(self, filters: QuestionFilters, user_id: Optional[int] = None) -> QuestionResponse:
        """Get filtered and paginated questions including user questions"""
        logger.info(f"Service: Getting filtered questions with filters: {filters}, user_id: {user_id}")
        
        try:
            # Get regular questions with company data
            logger.debug("Calling question_repo.get_filtered_questions")
            questions_data, regular_total = self.question_repo.get_filtered_questions(filters, user_id)
            logger.debug(f"Retrieved {len(questions_data)} regular questions out of {regular_total} total")
            
            # Get user questions that should be visible
            logger.debug("Calling question_repo.get_user_questions_for_display")
            user_questions_data, user_total = self.question_repo.get_user_questions_for_display(filters, user_id)
            logger.debug(f"Retrieved {len(user_questions_data)} user questions out of {user_total} total")
            
            # Combine the results
            all_questions_data = questions_data + user_questions_data
            total = regular_total + user_total
            
            if not all_questions_data:
                return QuestionResponse(
                    questions=[],
                    total=0,
                    page=filters.page,
                    per_page=filters.per_page,
                    total_pages=0,
                    stats=FilterStats(
                        total_questions=0,
                        easy_count=0,
                        medium_count=0,
                        hard_count=0,
                        companies_count=0,
                        time_periods=[],
                        topics=[]
                    )
                )
            
            # Get company data for the regular questions
            regular_question_ids = [q['id'] for q in questions_data]
            company_data = self.question_repo.get_company_data_for_questions(regular_question_ids)
            
            # Get user question company associations
            user_question_ids = [q['id'] for q in user_questions_data]
            user_company_data = {}
            if user_question_ids:
                print(f"DEBUG: Getting company data for user questions: {user_question_ids}")
                # Import here to avoid circular imports
                from app.repositories.user_question_repository import UserQuestionRepository
                user_repo = UserQuestionRepository()
                for user_q_id in user_question_ids:
                    # user_q_id is the original ID from user_questions table
                    # The combined ID in main questions is 1000000 + user_q_id
                    combined_id = 1000000 + user_q_id
                    associations = user_repo.get_company_associations(user_q_id, is_approved_only=True)
                    print(f"DEBUG: User question {user_q_id} (combined {combined_id}) has {len(associations)} approved associations")
                    if associations:
                        user_company_data[combined_id] = []
                        for assoc in associations:
                            print(f"DEBUG: Adding association: {getattr(assoc, 'company_name', 'Unknown')}")
                            user_company_data[combined_id].append({
                                'company_name': getattr(assoc, 'company_name', 'Unknown'),
                                'frequency': assoc.frequency,
                                'time_period': assoc.time_period
                            })
                print(f"DEBUG: Final user_company_data: {user_company_data}")
        
            # Transform to grouped format
            grouped_questions = []
            for q_data in all_questions_data:
                # Handle user questions explicitly to ensure all fields are correct
                if q_data['id'] >= 1000000:  # User question
                    # Create a clean dict with exactly the fields needed by Question model
                    clean_data = {
                        'id': q_data['id'],
                        'title': q_data['title'],
                        'difficulty': q_data['difficulty'].upper() if q_data['difficulty'] else 'MEDIUM',  # Convert to uppercase
                        'acceptance_rate': None if q_data.get('acceptance_rate') is None else q_data['acceptance_rate'],
                        'link': q_data['link'],
                        'topics': q_data.get('topics', ''),
                        'description': q_data.get('description', ''),
                        'added_by': q_data['added_by'],
                        'is_approved': bool(q_data['is_approved']),
                        'is_public': bool(q_data['is_public'])
                    }
                    question = Question(**clean_data)
                else:
                    question = Question(**q_data)
                
                # Only regular questions have company data
                if q_data['id'] < 1000000:  # Regular question
                    # Group company data by company name
                    companies_dict = {}
                    q_company_data = company_data.get(q_data['id'], [])
                    
                    for c_row in q_company_data:
                        company_name = c_row['company_name']
                        if company_name not in companies_dict:
                            companies_dict[company_name] = {
                                'frequency': c_row['frequency'],
                                'time_periods': []
                            }
                        companies_dict[company_name]['time_periods'].append(c_row['time_period'])
                    
                    # Convert to CompanyData objects
                    companies_formatted = {}
                    for company_name, data in companies_dict.items():
                        companies_formatted[company_name] = CompanyData(
                            frequency=data['frequency'],
                            time_periods=list(set(data['time_periods']))  # Remove duplicates
                        )
                else:  # User question - get company data if available
                    companies_formatted = {}
                    user_company_associations = user_company_data.get(q_data['id'], [])
                    
                    # Group user company data by company name
                    companies_dict = {}
                    for c_row in user_company_associations:
                        company_name = c_row['company_name']
                        if company_name not in companies_dict:
                            companies_dict[company_name] = {
                                'frequency': c_row['frequency'],
                                'time_periods': []
                            }
                        companies_dict[company_name]['time_periods'].append(c_row['time_period'])
                    
                    # Convert to CompanyData objects
                    for company_name, data in companies_dict.items():
                        companies_formatted[company_name] = CompanyData(
                            frequency=data['frequency'],
                            time_periods=list(set(data['time_periods']))  # Remove duplicates
                        )
                
                grouped_questions.append(GroupedCompanyQuestion(
                    question=question,
                    companies=companies_formatted
                ))
                
            # Get filter statistics
            stats_data = self.question_repo.get_filter_stats(filters)
            stats = FilterStats(**stats_data)
            
            # Calculate total pages
            total_pages = (total + filters.per_page - 1) // filters.per_page
            
            return QuestionResponse(
                questions=grouped_questions,
                total=total,
                page=filters.page,
                per_page=filters.per_page,
                total_pages=total_pages,
                stats=stats
            )
            
        except Exception as e:
            error_msg = log_exception(e, "Error processing questions data")
            logger.error(f"Failed to process questions for filters: {filters}")
            raise
    
    def get_random_questions(self, filters: QuestionFilters, count: int, user_id: Optional[int] = None) -> QuestionResponse:
        """Get random questions based on filters"""
        logger.info(f"Service: Getting random questions with count: {count}, filters: {filters}, user_id: {user_id}")
        
        try:
            # Get random questions with company data
            logger.debug("Calling question_repo.get_random_questions")
            questions_data, total = self.question_repo.get_random_questions(filters, count, user_id)
            logger.debug(f"Retrieved {len(questions_data)} random questions out of {total} possible")
            
            if not questions_data:
                return QuestionResponse(
                    questions=[],
                    total=0,
                    page=1,
                    per_page=count,
                    total_pages=0,
                    stats=FilterStats(
                        total_questions=0,
                        easy_count=0,
                        medium_count=0,
                        hard_count=0,
                        companies_count=0,
                        time_periods=[],
                        topics=[]
                    )
                )
            
            # Get all company data for these questions in one query
            regular_question_ids = [q['id'] for q in questions_data if q['id'] < 1000000]
            company_data = {}
            if regular_question_ids:
                company_data = self.question_repo.get_company_data_for_questions(regular_question_ids)
            
            # Get user company data for user questions
            user_question_ids = [q['id'] for q in questions_data if q['id'] >= 1000000]
            user_company_data = {}
            
            if user_question_ids:
                # Need to convert to original user_question_id
                original_user_q_ids = [q_id - 1000000 for q_id in user_question_ids]
                
                # Import here to avoid circular imports
                from app.repositories.user_question_repository import UserQuestionRepository
                user_repo = UserQuestionRepository()
                
                for user_q_id in original_user_q_ids:
                    combined_id = 1000000 + user_q_id
                    associations = user_repo.get_company_associations(user_q_id, is_approved_only=True)
                    
                    if associations:
                        user_company_data[combined_id] = []
                        for assoc in associations:
                            user_company_data[combined_id].append({
                                'company_name': getattr(assoc, 'company_name', 'Unknown'),
                                'frequency': assoc.frequency,
                                'time_period': assoc.time_period
                            })
            
            # Transform to grouped format
            grouped_questions = []
            for q_data in questions_data:
                # Handle user questions explicitly to ensure all fields are correct
                if q_data['id'] >= 1000000:  # User question
                    # Create a clean dict with exactly the fields needed by Question model
                    clean_data = {
                        'id': q_data['id'],
                        'title': q_data['title'],
                        'difficulty': q_data['difficulty'].upper() if q_data['difficulty'] else 'MEDIUM',  # Convert to uppercase
                        'acceptance_rate': None if q_data.get('acceptance_rate') is None else q_data['acceptance_rate'],
                        'link': q_data['link'],
                        'topics': q_data.get('topics', ''),
                        'description': q_data.get('description', ''),
                        'added_by': q_data['added_by'],
                        'is_approved': bool(q_data['is_approved']),
                        'is_public': bool(q_data['is_public'])
                    }
                    question = Question(**clean_data)
                else:
                    question = Question(**q_data)
                
                # Only regular questions have company data
                if q_data['id'] < 1000000:  # Regular question
                    # Group company data by company name
                    companies_dict = {}
                    q_company_data = company_data.get(q_data['id'], [])
                    
                    for c_row in q_company_data:
                        company_name = c_row['company_name']
                        if company_name not in companies_dict:
                            companies_dict[company_name] = {
                                'frequency': c_row['frequency'],
                                'time_periods': []
                            }
                        companies_dict[company_name]['time_periods'].append(c_row['time_period'])
                    
                    # Convert to CompanyData objects
                    companies_formatted = {}
                    for company_name, data in companies_dict.items():
                        companies_formatted[company_name] = CompanyData(
                            frequency=data['frequency'],
                            time_periods=list(set(data['time_periods']))  # Remove duplicates
                        )
                else:  # User question - get company data if available
                    companies_formatted = {}
                    user_company_associations = user_company_data.get(q_data['id'], [])
                    
                    # Group user company data by company name
                    companies_dict = {}
                    for c_row in user_company_associations:
                        company_name = c_row['company_name']
                        if company_name not in companies_dict:
                            companies_dict[company_name] = {
                                'frequency': c_row['frequency'],
                                'time_periods': []
                            }
                        companies_dict[company_name]['time_periods'].append(c_row['time_period'])
                    
                    # Convert to CompanyData objects
                    for company_name, data in companies_dict.items():
                        companies_formatted[company_name] = CompanyData(
                            frequency=data['frequency'],
                            time_periods=list(set(data['time_periods']))  # Remove duplicates
                        )
                
                grouped_questions.append(GroupedCompanyQuestion(
                    question=question,
                    companies=companies_formatted
                ))
            
            # Calculate filter stats
            total_count = len(grouped_questions)
            easy_count = sum(1 for q in grouped_questions if q.question.difficulty == 'EASY')
            medium_count = sum(1 for q in grouped_questions if q.question.difficulty == 'MEDIUM')
            hard_count = sum(1 for q in grouped_questions if q.question.difficulty == 'HARD')
            
            # Get unique companies and time periods
            companies_set = set()
            time_periods_set = set()
            for question in grouped_questions:
                for company_name, company_data in question.companies.items():
                    companies_set.add(company_name)
                    time_periods_set.update(company_data.time_periods)
            
            # Get unique topics
            topics_set = set()
            for question in grouped_questions:
                if question.question.topics:
                    topics_list = [t.strip() for t in question.question.topics.split(',') if t.strip()]
                    topics_set.update(topics_list)
            
            # Create filter stats
            stats = FilterStats(
                total_questions=total_count,
                easy_count=easy_count,
                medium_count=medium_count,
                hard_count=hard_count,
                companies_count=len(companies_set),
                time_periods=list(time_periods_set),
                topics=list(topics_set)
            )
            
            return QuestionResponse(
                questions=grouped_questions,
                total=total,
                page=1,
                per_page=count,
                total_pages=1,
                stats=stats
            )
        except Exception as e:
            error_msg = log_exception(e, "Error processing random questions data")
            logger.error(f"Failed to process random questions for filters: {filters}")
            raise
    
    def get_all_difficulties(self) -> List[str]:
        """Get all available difficulty levels"""
        return ["EASY", "MEDIUM", "HARD"]
    
    def get_all_time_periods(self) -> List[str]:
        """Get all available time periods"""
        return ["30_days", "3_months", "6_months", "more_than_6_months", "all_time"]
    
    def get_all_topics(self) -> List[str]:
        """Get all unique topics"""
        try:
            return self.question_repo.get_all_topics()
        except Exception as e:
            self.handle_error(e, "Error retrieving topics")
    
    def handle_error(self, error: Exception, message: str = "An error occurred"):
        """Handle and transform errors to HTTP exceptions"""
        from fastapi import HTTPException
        from app.utils.logging import logger, log_exception
        
        # Log the error
        log_exception(error, message)
        
        if isinstance(error, ValueError):
            logger.warning(f"Bad request: {str(error)}")
            raise HTTPException(status_code=400, detail=str(error))
        elif isinstance(error, FileNotFoundError):
            logger.warning(f"Not found: {str(error)}")
            raise HTTPException(status_code=404, detail=str(error))
        else:
            logger.error(f"Internal server error: {message} - {str(error)}")
            raise HTTPException(status_code=500, detail=message)
    
    def get_stats(self) -> OverallStats:
        """Get overall statistics"""
        logger.info("Getting overall statistics")
        
        try:
            # Get total questions, companies, and relationships
            stats_query = """
                SELECT 
                    (SELECT COUNT(*) FROM questions) as total_questions,
                    (SELECT COUNT(*) FROM companies) as total_companies,
                    (SELECT COUNT(*) FROM question_companies) as total_relationships
            """
            
            stats_row = self.question_repo.execute_query_one(stats_query)
            
            if not stats_row:
                return OverallStats(
                    total_questions=0,
                    total_companies=0,
                    total_relationships=0,
                    difficulty_distribution={},
                    top_companies=[],
                    popular_questions=[]
                )
            
            # Get difficulty distribution
            difficulty_query = "SELECT difficulty, COUNT(*) as count FROM questions GROUP BY difficulty"
            difficulty_rows = self.question_repo.execute_query(difficulty_query)
            difficulty_distribution = {row['difficulty']: row['count'] for row in difficulty_rows}
            
            # Get top companies
            top_companies_query = """
                SELECT c.name, COUNT(qc.question_id) as question_count, 
                       MIN(qc.frequency) as min_freq, MAX(qc.frequency) as max_freq,
                       AVG(qc.frequency) as avg_freq
                FROM companies c
                JOIN question_companies qc ON c.id = qc.company_id
                GROUP BY c.id
                ORDER BY question_count DESC
                LIMIT 10
            """
            top_companies = self.question_repo.execute_query(top_companies_query)
            top_companies_list = [
                {
                    'name': company['name'],
                    'question_count': company['question_count'],
                    'min_frequency': company['min_freq'],
                    'max_frequency': company['max_freq'],
                    'avg_frequency': company['avg_freq']
                }
                for company in top_companies
            ]
            
            # Get popular questions
            popular_questions_query = """
                SELECT q.id, q.title, q.difficulty, COUNT(qc.company_id) as company_count,
                       AVG(qc.frequency) as avg_frequency
                FROM questions q
                JOIN question_companies qc ON q.id = qc.question_id
                GROUP BY q.id
                ORDER BY company_count DESC, avg_frequency DESC
                LIMIT 10
            """
            popular_questions = self.question_repo.execute_query(popular_questions_query)
            popular_questions_list = [
                {
                    'id': q['id'],
                    'title': q['title'],
                    'difficulty': q['difficulty'],
                    'company_count': q['company_count'],
                    'avg_frequency': q['avg_frequency']
                }
                for q in popular_questions
            ]
            
            return OverallStats(
                total_questions=stats_row['total_questions'],
                total_companies=stats_row['total_companies'],
                total_relationships=stats_row['total_relationships'],
                difficulty_distribution=difficulty_distribution,
                top_companies=top_companies_list,
                popular_questions=popular_questions_list
            )
        except Exception as e:
            self.handle_error(e, "Error retrieving statistics")
