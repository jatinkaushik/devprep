"""
Unified Question service for business logic using single questions table
"""
import json
from typing import List, Dict, Any, Optional
from app.services.base_service import BaseService
from app.repositories.unified_question_repository import UnifiedQuestionRepository
from app.repositories.company_repository import CompanyRepository
from app.utils.logging import logger, log_exception
from app.schemas.question_schemas import (
    QuestionFilters, QuestionResponse, Question, GroupedCompanyQuestion,
    FilterStats, CompanyData, OverallStats, QuestionCreate
)


class UnifiedQuestionService(BaseService):
    """Service for unified question-related business logic"""
    
    def __init__(self):
        super().__init__()
        self.question_repo = UnifiedQuestionRepository()
        self.company_repo = CompanyRepository()
    
    def get_filtered_questions(self, filters: QuestionFilters, user_id: Optional[int] = None) -> QuestionResponse:
        """Get filtered and paginated questions"""
        logger.info(f"Service: Getting filtered questions with filters: {filters}, user_id: {user_id}")
        
        try:
            # Get questions with company data
            questions_data, total = self.question_repo.get_filtered_questions(filters, user_id)
            logger.debug(f"Retrieved {len(questions_data)} questions out of {total} total")
            
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
            
            # Get company data for questions
            question_ids = [q['id'] for q in questions_data]
            company_data = self.question_repo.get_company_data_for_questions(question_ids)
            
            # Transform to grouped format
            grouped_questions = []
            for q_data in questions_data:
                # Normalize difficulty values for consistency
                if 'difficulty' in q_data:
                    if q_data['difficulty'] == 'Easy':
                        q_data['difficulty'] = 'EASY'
                    elif q_data['difficulty'] == 'Medium':
                        q_data['difficulty'] = 'MEDIUM'  
                    elif q_data['difficulty'] == 'Hard':
                        q_data['difficulty'] = 'HARD'
                
                question = Question(**q_data)
                
                # Get company associations for this question
                question_company_data = company_data.get(q_data['id'], [])
                
                # Group by company name
                companies = {}
                for comp_data in question_company_data:
                    company_name = comp_data['company_name']
                    if company_name not in companies:
                        companies[company_name] = CompanyData(
                            frequency=comp_data.get('frequency'),
                            time_periods=[]
                        )
                    companies[company_name].time_periods.append(comp_data['time_period'])
                
                grouped_questions.append(GroupedCompanyQuestion(
                    question=question,
                    companies=companies
                ))
            
            # Calculate statistics
            total_pages = (total + filters.per_page - 1) // filters.per_page
            
            # Get filter statistics
            stats = self._calculate_filter_stats(questions_data, company_data)
            
            return QuestionResponse(
                questions=grouped_questions,
                total=total,
                page=filters.page,
                per_page=filters.per_page,
                total_pages=total_pages,
                stats=stats
            )
            
        except Exception as e:
            logger.error(f"Error in get_filtered_questions: {e}")
            log_exception(e)
            raise

    def create_question(self, question_data: QuestionCreate, user_id: int) -> Dict[str, Any]:
        """Create a new question"""
        try:
            logger.info(f"Creating question for user {user_id}: {question_data.title}")
            
            # Convert topics list to JSON string if provided
            topics_json = None
            if question_data.topics:
                topics_json = json.dumps(question_data.topics)
            
            question_dict = {
                'title': question_data.title,
                'difficulty': question_data.difficulty,
                'link': question_data.link,
                'topics': topics_json,
                'description': question_data.description,
                'added_by': user_id,
                'is_approved': False,  # User questions need approval
                'is_public': question_data.is_public
            }
            
            question_id = self.question_repo.create_question(question_dict)
            
            logger.info(f"Created question with ID {question_id}")
            return {'id': question_id, 'message': 'Question created successfully'}
            
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            log_exception(e)
            raise

    def get_user_questions(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get questions created by a specific user"""
        try:
            questions, total = self.question_repo.get_user_questions(user_id, page, per_page)
            
            # Get company data for user questions
            question_ids = [q['id'] for q in questions]
            company_data = self.question_repo.get_company_data_for_questions(question_ids)
            
            # Add company information to questions
            for question in questions:
                question_companies = company_data.get(question['id'], [])
                question['companies'] = []
                for comp_data in question_companies:
                    question['companies'].append({
                        'company_id': comp_data.get('company_id'),
                        'company_name': comp_data['company_name'],
                        'time_period': comp_data['time_period'],
                        'frequency': comp_data.get('frequency', 1.0)
                    })
                
                # Parse topics JSON if available
                if question.get('topics'):
                    try:
                        question['topics'] = json.loads(question['topics'])
                    except:
                        question['topics'] = []
                else:
                    question['topics'] = []
            
            total_pages = (total + per_page - 1) // per_page
            
            return {
                'questions': questions,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting user questions: {e}")
            log_exception(e)
            raise

    def get_question_details(self, question_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get detailed information about a specific question"""
        try:
            question = self.question_repo.get_question_by_id(question_id, user_id)
            if not question:
                raise ValueError("Question not found")
            
            # Get company data for this question
            company_data = self.question_repo.get_company_data_for_questions([question_id])
            question_companies = company_data.get(question_id, [])
            
            question['companies'] = []
            for comp_data in question_companies:
                question['companies'].append({
                    'company_id': comp_data.get('company_id'),
                    'company_name': comp_data['company_name'],
                    'time_period': comp_data['time_period'],
                    'frequency': comp_data.get('frequency', 1.0)
                })
            
            # Parse topics JSON if available
            if question.get('topics'):
                try:
                    question['topics'] = json.loads(question['topics'])
                except:
                    question['topics'] = []
            else:
                question['topics'] = []
            
            return question
            
        except Exception as e:
            logger.error(f"Error getting question details: {e}")
            log_exception(e)
            raise

    def update_question(self, question_id: int, question_data: QuestionCreate, user_id: int) -> Dict[str, Any]:
        """Update a question"""
        try:
            # Check if user owns the question or is admin
            question = self.question_repo.get_question_by_id(question_id)
            if not question:
                raise ValueError("Question not found")
            
            if question['added_by'] != user_id:
                # TODO: Add admin check here
                raise ValueError("Permission denied")
            
            # Convert topics list to JSON string if provided
            topics_json = None
            if question_data.topics:
                topics_json = json.dumps(question_data.topics)
            
            question_dict = {
                'title': question_data.title,
                'difficulty': question_data.difficulty,
                'link': question_data.link,
                'topics': topics_json,
                'description': question_data.description,
                'is_public': question_data.is_public
            }
            
            success = self.question_repo.update_question(question_id, question_dict)
            
            if success:
                return {'message': 'Question updated successfully'}
            else:
                raise ValueError("Failed to update question")
                
        except Exception as e:
            logger.error(f"Error updating question: {e}")
            log_exception(e)
            raise

    def delete_question(self, question_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a question"""
        try:
            # Check if user owns the question or is admin
            question = self.question_repo.get_question_by_id(question_id)
            if not question:
                raise ValueError("Question not found")
            
            if question['added_by'] != user_id:
                # TODO: Add admin check here
                raise ValueError("Permission denied")
            
            success = self.question_repo.delete_question(question_id)
            
            if success:
                return {'message': 'Question deleted successfully'}
            else:
                raise ValueError("Failed to delete question")
                
        except Exception as e:
            logger.error(f"Error deleting question: {e}")
            log_exception(e)
            raise

    def request_public_approval(self, question_id: int, user_id: int) -> Dict[str, Any]:
        """Request public approval for a question"""
        try:
            # Check if user owns the question
            question = self.question_repo.get_question_by_id(question_id)
            if not question:
                raise ValueError("Question not found")
            
            if question['added_by'] != user_id:
                raise ValueError("Permission denied")
            
            # Update is_public flag (subject to admin approval)
            success = self.question_repo.update_question(question_id, {'is_public': True})
            
            if success:
                return {'message': 'Public approval requested successfully'}
            else:
                raise ValueError("Failed to request public approval")
                
        except Exception as e:
            logger.error(f"Error requesting public approval: {e}")
            log_exception(e)
            raise

    def get_all_topics(self) -> List[str]:
        """Get all unique topics from questions"""
        try:
            return self.question_repo.get_all_topics()
        except Exception as e:
            logger.error(f"Error getting all topics: {e}")
            log_exception(e)
            raise

    def get_all_difficulties(self) -> List[str]:
        """Get all difficulty levels"""
        return ['Easy', 'Medium', 'Hard']

    def get_all_time_periods(self) -> List[str]:
        """Get all time periods from company associations"""
        try:
            return self.question_repo.get_all_time_periods()
        except Exception as e:
            logger.error(f"Error getting all time periods: {e}")
            log_exception(e)
            raise

    def _calculate_filter_stats(self, questions_data: List[Dict], company_data: Dict) -> FilterStats:
        """Calculate statistics for the current filter results"""
        try:
            total_questions = len(questions_data)
            easy_count = sum(1 for q in questions_data if q.get('difficulty') in ['Easy', 'EASY'])
            medium_count = sum(1 for q in questions_data if q.get('difficulty') in ['Medium', 'MEDIUM'])
            hard_count = sum(1 for q in questions_data if q.get('difficulty') in ['Hard', 'HARD'])
            
            # Count unique companies
            companies = set()
            time_periods = set()
            for comp_list in company_data.values():
                for comp_data in comp_list:
                    companies.add(comp_data['company_name'])
                    time_periods.add(comp_data['time_period'])
            
            # Extract unique topics
            topics = set()
            for q in questions_data:
                if q.get('topics'):
                    try:
                        q_topics = json.loads(q['topics']) if isinstance(q['topics'], str) else q['topics']
                        topics.update(q_topics)
                    except:
                        pass
            
            return FilterStats(
                total_questions=total_questions,
                easy_count=easy_count,
                medium_count=medium_count,
                hard_count=hard_count,
                companies_count=len(companies),
                time_periods=sorted(list(time_periods)),
                topics=sorted(list(topics))
            )
            
        except Exception as e:
            logger.error(f"Error calculating filter stats: {e}")
            return FilterStats(
                total_questions=0,
                easy_count=0,
                medium_count=0,
                hard_count=0,
                companies_count=0,
                time_periods=[],
                topics=[]
            )
