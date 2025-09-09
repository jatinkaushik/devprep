"""
Schemas for user list operations
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class UserListCreate(BaseModel):
    name: str
    list_type: str
    description: Optional[str] = None


class UserListResponse(BaseModel):
    id: int
    user_id: int
    name: str
    list_type: str
    description: Optional[str]
    is_default: bool
    item_count: int
    created_at: datetime


class ListItemCreate(BaseModel):
    question_id: Optional[int] = None
    user_question_id: Optional[int] = None
    status: str = "not_attempted"
    notes: Optional[str] = None


class ListItemResponse(BaseModel):
    id: int
    list_id: int
    question_id: Optional[int]
    user_question_id: Optional[int]
    status: str
    notes: Optional[str]
    title: str
    difficulty: str
    question_type: str
    created_at: datetime


class ListItemUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class QuickAddRequest(BaseModel):
    question_id: Optional[int] = None
    user_question_id: Optional[int] = None
    list_type: str  # 'favorites', 'todo', 'solved'


class UserListsResponse(BaseModel):
    lists: List[UserListResponse]
