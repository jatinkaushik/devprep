"""
Question controller for API endpoints
"""
from typing import List, Optional
from fastapi import Depends, Query, Header
from app.controllers.base_controller import BaseController
from app.services.question_service import QuestionService
from app.utils.logging import logger, log_exception
from app.schemas.question_schemas import (
    QuestionResponse, QuestionFilters, OverallStats,
    LogicEnum, SortByEnum, SortOrderEnum
)
from app.utils.auth import AuthUtils


class QuestionController(BaseController):
    """Controller for question-related API endpoints"""
    
    def __init__(self):
        super().__init__()
        self.question_service = QuestionService()
        self.auth_utils = AuthUtils()
    
    def get_questions(
        self,
        companies: str = Query(None, description="Comma-separated company names"),
        company_logic: LogicEnum = Query(LogicEnum.OR, description="Logic for company filtering: AND or OR"),
        difficulties: str = Query(None, description="Comma-separated difficulties"),
        time_periods: str = Query(None, description="Comma-separated time periods"),
        time_period_logic: LogicEnum = Query(LogicEnum.OR, description="Logic for time period filtering: AND or OR"),
        topics: str = Query(None, description="Comma-separated topics"),
        search: str = Query(None, description="Search in question titles"),
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
        sort_by: SortByEnum = Query(SortByEnum.FREQUENCY, description="Sort by: frequency, title, difficulty"),
        sort_order: SortOrderEnum = Query(SortOrderEnum.DESC, description="Sort order: asc, desc"),
        authorization: Optional[str] = Header(None, convert_underscores=False)
    ) -> QuestionResponse:
        """Get questions with filters, including user questions if authenticated"""
        try:
            # Extract user_id from token if provided
            user_id = None
            
            if authorization and authorization.startswith("Bearer "):
                try:
                    token = authorization.split(" ")[1]
                    payload = self.auth_utils.verify_token(token)
                    user_id = payload.get("user_id") if payload else None
                    logger.info(f"Successfully extracted user_id: {user_id} from token")
                except Exception as e:
                    logger.warning(f"Token validation failed: {str(e)}")
                    pass  # Continue without user_id if token is invalid
            
            filters = QuestionFilters(
                companies=companies,
                company_logic=company_logic,
                difficulties=difficulties,
                time_periods=time_periods,
                time_period_logic=time_period_logic,
                topics=topics,
                search=search,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            logger.info(f"Controller: Getting filtered questions with parameters: page={page}, per_page={per_page}")
            logger.debug(f"Full filters: {filters}")
            logger.debug(f"User ID for request: {user_id}")
            
            # Call service and return results
            result = self.question_service.get_filtered_questions(filters, user_id)
            logger.debug(f"Successfully retrieved {len(result.questions)} questions out of {result.total}")
            return result
        
        except Exception as e:
            self.handle_error(e, "Error retrieving questions")
    
    def get_difficulties(self) -> List[str]:
        """Get all difficulty levels"""
        try:
            return self.question_service.get_all_difficulties()
        except Exception as e:
            self.handle_error(e, "Error retrieving difficulties")
    
    def get_time_periods(self) -> List[str]:
        """Get all time periods"""
        try:
            return self.question_service.get_all_time_periods()
        except Exception as e:
            self.handle_error(e, "Error retrieving time periods")
    
    def get_topics(self) -> List[str]:
        """Get all unique topics"""
        try:
            return self.question_service.get_all_topics()
        except Exception as e:
            self.handle_error(e, "Error retrieving topics")
    
    def get_stats(self) -> OverallStats:
        """Get overall statistics"""
        try:
            return self.question_service.get_overall_stats()
        except Exception as e:
            self.handle_error(e, "Error retrieving statistics")
            
    def get_random_questions(
        self,
        count: int = 5,
        companies: str = None,
        company_logic: LogicEnum = LogicEnum.OR,
        difficulties: str = None,
        time_periods: str = None,
        time_period_logic: LogicEnum = LogicEnum.OR,
        topics: str = None,
        authorization: Optional[str] = None
    ) -> QuestionResponse:
        """Get random questions with filters"""
        try:
            # Extract user_id from token if provided
            user_id = None
            
            if authorization and authorization.startswith("Bearer "):
                try:
                    token = authorization.split(" ")[1]
                    payload = self.auth_utils.verify_token(token)
                    user_id = payload.get("user_id") if payload else None
                    logger.info(f"Successfully extracted user_id: {user_id} from token")
                except Exception as e:
                    logger.warning(f"Token validation failed: {str(e)}")
                    pass  # Continue without user_id if token is invalid
            
            filters = QuestionFilters(
                companies=companies,
                company_logic=company_logic,
                difficulties=difficulties,
                time_periods=time_periods,
                time_period_logic=time_period_logic,
                topics=topics,
                page=1,
                per_page=count,
                sort_by=SortByEnum.FREQUENCY,
                sort_order=SortOrderEnum.DESC
            )
            
            logger.info(f"Controller: Getting random questions with count: {count}")
            logger.debug(f"Full filters: {filters}")
            logger.debug(f"User ID for request: {user_id}")
            
            # Call service and return results
            result = self.question_service.get_random_questions(filters, count, user_id)
            logger.debug(f"Successfully retrieved {len(result.questions)} random questions")
            return result
        
        except Exception as e:
            self.handle_error(e, "Error retrieving random questions")
