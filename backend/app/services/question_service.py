"""
Question service for business logic
"""
from typing import List, Dict, Any
from app.services.base_service import BaseService
from app.repositories.question_repository import QuestionRepository
from app.repositories.company_repository import CompanyRepository
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
    
    def get_filtered_questions(self, filters: QuestionFilters) -> QuestionResponse:
        """Get filtered and paginated questions"""
        
        # Get questions and total count
        questions_data, total = self.question_repo.get_filtered_questions(filters)
        
        if not questions_data:
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
        
        # Get company data for the questions
        question_ids = [q['id'] for q in questions_data]
        company_data = self.question_repo.get_company_data_for_questions(question_ids)
        
        # Transform to grouped format
        grouped_questions = []
        for q_data in questions_data:
            question = Question(**q_data)
            
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
    
    def get_all_difficulties(self) -> List[str]:
        """Get all available difficulty levels"""
        return ["EASY", "MEDIUM", "HARD"]
    
    def get_all_time_periods(self) -> List[str]:
        """Get all available time periods"""
        return ["30_days", "3_months", "6_months", "more_than_6_months", "all_time"]
    
    def get_all_topics(self) -> List[str]:
        """Get all unique topics"""
        query = "SELECT DISTINCT topics FROM questions WHERE topics IS NOT NULL AND topics != ''"
        topics_raw = self.question_repo.execute_query(query)
        
        # Extract individual topics from comma-separated strings
        topics_set = set()
        for row in topics_raw:
            if row['topics']:
                # Split by comma and clean up
                topic_list = [topic.strip() for topic in row['topics'].split(',')]
                topics_set.update(topic_list)
        
        return sorted(list(topics_set))
    
    def get_overall_stats(self) -> OverallStats:
        """Get overall application statistics"""
        
        # Total questions
        total_questions_query = "SELECT COUNT(*) as count FROM questions"
        total_questions = self.question_repo.execute_query_one(total_questions_query)['count']
        
        # Total companies
        total_companies_query = "SELECT COUNT(*) as count FROM companies"
        total_companies = self.question_repo.execute_query_one(total_companies_query)['count']
        
        # Total relationships
        total_relationships_query = "SELECT COUNT(*) as count FROM company_questions"
        total_relationships = self.question_repo.execute_query_one(total_relationships_query)['count']
        
        # Difficulty distribution
        difficulty_query = """
            SELECT difficulty, COUNT(*) as count 
            FROM questions 
            GROUP BY difficulty
        """
        difficulty_results = self.question_repo.execute_query(difficulty_query)
        difficulty_distribution = {row['difficulty']: row['count'] for row in difficulty_results}
        
        # Top companies by question count
        top_companies_query = """
            SELECT c.name, COUNT(DISTINCT cq.question_id) as count
            FROM companies c
            JOIN company_questions cq ON c.id = cq.company_id
            GROUP BY c.id, c.name
            ORDER BY count DESC
            LIMIT 10
        """
        top_companies = self.question_repo.execute_query(top_companies_query)
        
        # Popular questions by company count
        popular_questions_query = """
            SELECT q.title, q.difficulty, COUNT(DISTINCT cq.company_id) as count
            FROM questions q
            JOIN company_questions cq ON q.id = cq.question_id
            GROUP BY q.id, q.title, q.difficulty
            ORDER BY count DESC
            LIMIT 10
        """
        popular_questions = self.question_repo.execute_query(popular_questions_query)
        
        return OverallStats(
            total_questions=total_questions,
            total_companies=total_companies,
            total_relationships=total_relationships,
            difficulty_distribution=difficulty_distribution,
            top_companies=top_companies,
            popular_questions=popular_questions
        )
