"""
Question controller for API endpoints
"""
from typing import List
from fastapi import Depends, Query
from app.controllers.base_controller import BaseController
from app.services.question_service import QuestionService
from app.schemas.question_schemas import (
    QuestionResponse, QuestionFilters, OverallStats,
    LogicEnum, SortByEnum, SortOrderEnum
)


class QuestionController(BaseController):
    """Controller for question-related API endpoints"""
    
    def __init__(self):
        super().__init__()
        self.question_service = QuestionService()
    
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
        sort_order: SortOrderEnum = Query(SortOrderEnum.DESC, description="Sort order: asc, desc")
    ) -> QuestionResponse:
        """Get questions with filters"""
        try:
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
            
            return self.question_service.get_filtered_questions(filters)
        
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
