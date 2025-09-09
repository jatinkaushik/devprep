"""
Pydantic schemas for user management and question features
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from app.models.user_models import UserRole, QuestionDifficulty, ApprovalStatus, RequestType, EntityType


# User schemas
class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    password: str = Field(..., min_length=6, description="Password")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# User Question schemas
class UserQuestionCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500, description="Question title")
    description: Optional[str] = Field(None, max_length=5000, description="Question description")
    difficulty: QuestionDifficulty
    topics: Optional[List[str]] = Field(None, description="List of topics")
    solution: Optional[str] = Field(None, max_length=10000, description="Solution explanation")
    link: Optional[str] = Field(None, max_length=500, description="External link to the question")
    request_public: bool = Field(False, description="Request to make question public")

    @validator('topics')
    def validate_topics(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 topics allowed')
        return v


class UserQuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    difficulty: Optional[QuestionDifficulty] = None
    topics: Optional[List[str]] = None
    solution: Optional[str] = Field(None, max_length=10000)
    link: Optional[str] = Field(None, max_length=500)


class UserQuestionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    difficulty: QuestionDifficulty
    topics: Optional[List[str]]
    solution: Optional[str]
    link: Optional[str]
    is_public: bool
    is_approved: bool
    created_by: int
    creator_username: Optional[str]
    approved_by: Optional[int]
    approver_username: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    references: Optional[List['QuestionReferenceResponse']] = []
    companies: Optional[List['UserQuestionCompanyResponse']] = []
    is_favorited: Optional[bool] = False


# Question Reference schemas
class QuestionReferenceCreate(BaseModel):
    url: str = Field(..., description="Reference URL")
    title: Optional[str] = Field(None, max_length=200, description="Reference title")
    description: Optional[str] = Field(None, max_length=1000, description="Reference description")
    question_id: Optional[int] = Field(None, description="Original question ID")
    user_question_id: Optional[int] = Field(None, description="User question ID")

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class QuestionReferenceResponse(BaseModel):
    id: int
    url: str
    title: Optional[str]
    description: Optional[str]
    is_approved: bool
    created_by: int
    creator_username: Optional[str]
    approved_by: Optional[int]
    approver_username: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]


# Company Association schemas
class UserQuestionCompanyCreate(BaseModel):
    company_id: int
    time_period: str = Field(..., description="Time period when question appeared")
    frequency: float = Field(1.0, ge=0.1, le=10.0, description="Question frequency")


class UserQuestionCompanyResponse(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str]
    time_period: str
    frequency: float
    is_approved: bool
    created_by: int
    creator_username: Optional[str]
    approved_by: Optional[int]
    approver_username: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]


# Approval Request schemas
class ApprovalRequestResponse(BaseModel):
    id: int
    request_type: RequestType
    entity_id: int
    entity_type: EntityType
    requested_by: int
    requester_username: Optional[str]
    status: ApprovalStatus
    admin_notes: Optional[str]
    processed_by: Optional[int]
    processor_username: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    # Additional fields based on entity type
    entity_details: Optional[dict] = {}


class ApprovalRequestUpdate(BaseModel):
    status: ApprovalStatus
    admin_notes: Optional[str] = Field(None, max_length=1000)


# Company schemas
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Company name")


class CompanyResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


# Admin statistics
class AdminStats(BaseModel):
    total_users: int
    total_user_questions: int
    pending_question_approvals: int
    pending_reference_approvals: int
    pending_company_associations: int
    questions_approved_today: int
    references_approved_today: int


# Question list with pagination
class QuestionListResponse(BaseModel):
    questions: List[UserQuestionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Update forward references
UserQuestionResponse.update_forward_refs()
