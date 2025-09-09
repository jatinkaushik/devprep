from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    difficulty: str = Field(..., pattern="^(Easy|Medium|Hard)$")
    link: Optional[str] = None
    topics: Optional[List[str]] = []
    is_public: bool = False

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    link: Optional[str] = None
    topics: Optional[List[str]] = None
    is_public: Optional[bool] = None

class CompanyAssociation(BaseModel):
    company_id: int
    time_period: str
    frequency: float = 1.0

class QuestionResponse(QuestionBase):
    id: int
    added_by: int
    is_approved: bool
    acceptance_rate: Optional[float] = None
    created_at: datetime
    companies: Optional[List[dict]] = []
    
    class Config:
        from_attributes = True

class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class QuestionWithUserInfo(QuestionResponse):
    added_by_username: Optional[str] = None
    can_edit: bool = False
    can_delete: bool = False
