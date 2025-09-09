"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class DifficultyEnum(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class LogicEnum(str, Enum):
    AND = "AND"
    OR = "OR"


class SortByEnum(str, Enum):
    FREQUENCY = "frequency"
    TITLE = "title"
    DIFFICULTY = "difficulty"


class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"


class QuestionBase(BaseModel):
    """Base question model"""
    id: int
    title: str
    difficulty: DifficultyEnum
    acceptance_rate: Optional[float] = None
    link: str
    topics: Optional[str] = None
    description: Optional[str] = None
    added_by: int
    is_approved: bool = True
    is_public: bool = False


class Question(QuestionBase):
    """Question model for API responses"""
    pass


class QuestionCreate(BaseModel):
    """Question creation model"""
    title: str
    difficulty: str
    link: str
    topics: Optional[List[str]] = None
    description: Optional[str] = None
    is_public: bool = False


class CompanyBase(BaseModel):
    """Base company model"""
    id: int
    name: str


class Company(CompanyBase):
    """Company model for API responses"""
    pass


class CompanyData(BaseModel):
    """Company data associated with a question"""
    frequency: Optional[float] = None
    time_periods: List[str] = []


class GroupedCompanyQuestion(BaseModel):
    """Grouped question with company data"""
    question: Question
    companies: Dict[str, CompanyData]


class FilterStats(BaseModel):
    """Statistics for current filters"""
    total_questions: int
    easy_count: int
    medium_count: int
    hard_count: int
    companies_count: int
    time_periods: List[str]
    topics: List[str]


class QuestionResponse(BaseModel):
    """Paginated questions response"""
    questions: List[GroupedCompanyQuestion]
    total: int
    page: int
    per_page: int
    total_pages: int
    stats: FilterStats


class QuestionFilters(BaseModel):
    """Question filtering parameters"""
    companies: Optional[str] = Field(None, description="Comma-separated company names")
    company_logic: LogicEnum = Field(LogicEnum.OR, description="Logic for company filtering")
    difficulties: Optional[str] = Field(None, description="Comma-separated difficulties")
    time_periods: Optional[str] = Field(None, description="Comma-separated time periods")
    time_period_logic: LogicEnum = Field(LogicEnum.OR, description="Logic for time period filtering")
    topics: Optional[str] = Field(None, description="Comma-separated topics")
    search: Optional[str] = Field(None, description="Search in question titles")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: SortByEnum = Field(SortByEnum.FREQUENCY, description="Sort field")
    sort_order: SortOrderEnum = Field(SortOrderEnum.DESC, description="Sort order")


class OverallStats(BaseModel):
    """Overall application statistics"""
    total_questions: int
    total_companies: int
    total_relationships: int
    difficulty_distribution: Dict[str, int]
    top_companies: List[Dict[str, Any]]
    popular_questions: List[Dict[str, Any]]
