"""
Unified Question controller for API endpoints using single questions table
"""
from typing import List, Optional
from fastapi import Depends, Query, Header, HTTPException
from app.controllers.base_controller import BaseController
from app.services.unified_question_service import UnifiedQuestionService
from app.utils.logging import logger, log_exception
from app.schemas.question_schemas import (
    QuestionResponse, QuestionFilters, OverallStats, QuestionCreate,
    LogicEnum, SortByEnum, SortOrderEnum
)
from app.utils.auth import AuthUtils


class UnifiedQuestionController(BaseController):
    """Controller for unified question-related API endpoints"""
    
    def __init__(self):
        super().__init__()
        self.question_service = UnifiedQuestionService()
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
        """Get questions with filters"""
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
                    logger.warning(f"Failed to extract user_id from token: {e}")

            # Create filters object
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
            
            logger.info(f"Getting questions with filters: {filters}")
            
            return self.question_service.get_filtered_questions(filters, user_id)
            
        except Exception as e:
            logger.error(f"Error in get_questions: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def create_question(
        self,
        question_data: QuestionCreate,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Create a new question"""
        try:
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = authorization.split(" ")[1]
            payload = self.auth_utils.verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            
            return self.question_service.create_question(question_data, user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in create_question: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_user_questions(
        self,
        authorization: str = Header(..., convert_underscores=False),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
    ):
        """Get user's own questions"""
        try:
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = authorization.split(" ")[1]
            payload = self.auth_utils.verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            
            return self.question_service.get_user_questions(user_id, page, per_page)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_user_questions: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_question_details(
        self,
        question_id: int,
        authorization: Optional[str] = Header(None, convert_underscores=False)
    ):
        """Get detailed information about a specific question"""
        try:
            user_id = None
            if authorization and authorization.startswith("Bearer "):
                try:
                    token = authorization.split(" ")[1]
                    payload = self.auth_utils.verify_token(token)
                    user_id = payload.get("user_id") if payload else None
                except Exception as e:
                    logger.warning(f"Failed to extract user_id from token: {e}")
            
            return self.question_service.get_question_details(question_id, user_id)
            
        except Exception as e:
            logger.error(f"Error in get_question_details: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_question(
        self,
        question_id: int,
        question_data: QuestionCreate,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Update a question"""
        try:
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = authorization.split(" ")[1]
            payload = self.auth_utils.verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            
            return self.question_service.update_question(question_id, question_data, user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in update_question: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete_question(
        self,
        question_id: int,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Delete a question"""
        try:
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = authorization.split(" ")[1]
            payload = self.auth_utils.verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            
            return self.question_service.delete_question(question_id, user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in delete_question: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def request_public_approval(
        self,
        question_id: int,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Request public approval for a question"""
        try:
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header")
            
            token = authorization.split(" ")[1]
            payload = self.auth_utils.verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            
            return self.question_service.request_public_approval(question_id, user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in request_public_approval: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_all_topics(self):
        """Get all unique topics from questions"""
        try:
            return self.question_service.get_all_topics()
        except Exception as e:
            logger.error(f"Error in get_all_topics: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_all_difficulties(self):
        """Get all difficulty levels"""
        try:
            return self.question_service.get_all_difficulties()
        except Exception as e:
            logger.error(f"Error in get_all_difficulties: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_all_time_periods(self):
        """Get all time periods from company associations"""
        try:
            return self.question_service.get_all_time_periods()
        except Exception as e:
            logger.error(f"Error in get_all_time_periods: {e}")
            log_exception(e)
            raise HTTPException(status_code=500, detail="Internal server error")
