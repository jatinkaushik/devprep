"""
Database models for user management and question features
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class QuestionDifficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RequestType(str, Enum):
    QUESTION_PUBLIC = "question_public"
    REFERENCE = "reference"
    COMPANY_ASSOCIATION = "company_association"


class EntityType(str, Enum):
    USER_QUESTION = "user_question"
    QUESTION_REFERENCE = "question_reference"
    USER_QUESTION_COMPANY = "user_question_company"


class ListType(str, Enum):
    FAVORITES = "favorites"
    TODO = "todo"
    SOLVED = "solved"
    CUSTOM = "custom"


class QuestionStatus(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"


class User:
    def __init__(self, id: int, email: str, username: str, full_name: Optional[str], 
                 password_hash: str, role: UserRole = UserRole.USER, is_active: bool = True,
                 created_at: datetime = None):
        self.id = id
        self.email = email
        self.username = username
        self.full_name = full_name
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now()


class UserQuestion:
    def __init__(self, id: int, title: str, created_by: int, difficulty: QuestionDifficulty,
                 description: Optional[str] = None, topics: Optional[str] = None,
                 solution: Optional[str] = None, link: Optional[str] = None, is_public: bool = False,
                 is_approved: bool = False, approved_by: Optional[int] = None, 
                 created_at: datetime = None, updated_at: datetime = None, 
                 approved_at: Optional[datetime] = None):
        self.id = id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.topics = topics
        self.solution = solution
        self.link = link
        self.is_public = is_public
        self.is_approved = is_approved
        self.created_by = created_by
        self.approved_by = approved_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.approved_at = approved_at


class QuestionReference:
    def __init__(self, id: int, url: str, created_by: int, title: Optional[str] = None,
                 description: Optional[str] = None, is_approved: bool = False,
                 approved_by: Optional[int] = None, question_id: Optional[int] = None, 
                 user_question_id: Optional[int] = None, created_at: datetime = None, 
                 approved_at: Optional[datetime] = None):
        self.id = id
        self.question_id = question_id
        self.user_question_id = user_question_id
        self.url = url
        self.title = title
        self.description = description
        self.is_approved = is_approved
        self.created_by = created_by
        self.approved_by = approved_by
        self.created_at = created_at or datetime.now()
        self.approved_at = approved_at


class UserQuestionCompany:
    def __init__(self, id: int, user_question_id: int, company_id: int,
                 time_period: str, created_by: int, frequency: float = 1.0,
                 is_approved: bool = False, approved_by: Optional[int] = None,
                 created_at: datetime = None, approved_at: Optional[datetime] = None):
        self.id = id
        self.user_question_id = user_question_id
        self.company_id = company_id
        self.time_period = time_period
        self.frequency = frequency
        self.is_approved = is_approved
        self.created_by = created_by
        self.approved_by = approved_by
        self.created_at = created_at or datetime.now()
        self.approved_at = approved_at


class ApprovalRequest:
    def __init__(self, id: int, request_type: RequestType, entity_id: int,
                 entity_type: EntityType, requested_by: int,
                 status: ApprovalStatus = ApprovalStatus.PENDING,
                 admin_notes: Optional[str] = None, processed_by: Optional[int] = None,
                 created_at: datetime = None, processed_at: Optional[datetime] = None):
        self.id = id
        self.request_type = request_type
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.requested_by = requested_by
        self.status = status
        self.admin_notes = admin_notes
        self.processed_by = processed_by
        self.created_at = created_at or datetime.now()
        self.processed_at = processed_at


class UserFavorite:
    def __init__(self, id: int, user_id: int, question_id: Optional[int] = None,
                 user_question_id: Optional[int] = None, created_at: datetime = None):
        self.id = id
        self.user_id = user_id
        self.question_id = question_id
        self.user_question_id = user_question_id
        self.created_at = created_at or datetime.now()


class UserList:
    def __init__(self, id: int, user_id: int, name: str, list_type: ListType,
                 description: Optional[str] = None, is_default: bool = False,
                 created_at: datetime = None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.list_type = list_type
        self.description = description
        self.is_default = is_default  # True for favorites, todo, solved
        self.created_at = created_at or datetime.now()


class UserListItem:
    def __init__(self, id: int, list_id: int, question_id: Optional[int] = None,
                 user_question_id: Optional[int] = None, status: QuestionStatus = QuestionStatus.NOT_ATTEMPTED,
                 notes: Optional[str] = None, created_at: datetime = None):
        self.id = id
        self.list_id = list_id
        self.question_id = question_id
        self.user_question_id = user_question_id
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.now()


class UserQuestionProgress:
    def __init__(self, id: int, user_id: int, question_id: Optional[int] = None,
                 user_question_id: Optional[int] = None, status: QuestionStatus = QuestionStatus.NOT_ATTEMPTED,
                 attempts: int = 0, time_spent_minutes: int = 0,
                 notes: Optional[str] = None, last_attempted: Optional[datetime] = None,
                 completed_at: Optional[datetime] = None, created_at: datetime = None):
        self.id = id
        self.user_id = user_id
        self.question_id = question_id
        self.user_question_id = user_question_id
        self.status = status
        self.attempts = attempts
        self.time_spent_minutes = time_spent_minutes
        self.notes = notes
        self.last_attempted = last_attempted
        self.completed_at = completed_at
        self.created_at = created_at or datetime.now()
