from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ..schemas.unified_question_schemas import (
    QuestionCreate, QuestionUpdate, QuestionResponse, 
    QuestionListResponse, CompanyAssociation
)
from ..services.question_service_unified import UnifiedQuestionService
from ..utils.auth import get_current_user_optional, get_current_user
from ..models.user_models import User

router = APIRouter(prefix="/api/questions", tags=["questions"])
question_service = UnifiedQuestionService()

@router.post("/", response_model=dict)
async def create_question(
    question: QuestionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new question"""
    question_data = question.dict()
    result = question_service.create_question(question_data, current_user.id)
    
    if result['success']:
        return result
    else:
        raise HTTPException(status_code=400, detail=result['error'])

@router.get("/", response_model=QuestionListResponse)
async def get_questions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    my_questions: bool = Query(False),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get paginated list of questions"""
    user_id = current_user.id if current_user else None
    
    result = question_service.get_questions(
        page=page, per_page=per_page, search=search,
        difficulty=difficulty, topic=topic, user_id=user_id,
        my_questions=my_questions
    )
    
    return QuestionListResponse(**result)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get a specific question by ID"""
    user_id = current_user.id if current_user else None
    question = question_service.get_question_by_id(question_id, user_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionResponse(**question)

@router.put("/{question_id}", response_model=dict)
async def update_question(
    question_id: int,
    question: QuestionUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a question"""
    question_data = question.dict(exclude_unset=True)
    result = question_service.update_question(question_id, question_data, current_user.id)
    
    if result['success']:
        return result
    else:
        raise HTTPException(status_code=400, detail=result['error'])

@router.delete("/{question_id}", response_model=dict)
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a question"""
    result = question_service.delete_question(question_id, current_user.id)
    
    if result['success']:
        return result
    else:
        raise HTTPException(status_code=400, detail=result['error'])

@router.post("/{question_id}/companies", response_model=dict)
async def add_company_association(
    question_id: int,
    company_data: CompanyAssociation,
    current_user: dict = Depends(get_current_user)
):
    """Add company association to a question"""
    try:
        success = question_service.repository.add_company_association(
            question_id, company_data.dict()
        )
        
        if success:
            return {'success': True, 'message': 'Company association added'}
        else:
            raise HTTPException(status_code=400, detail="Failed to add company association")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{question_id}/approve", response_model=dict)
async def approve_question(
    question_id: int,
    current_user: User = Depends(get_current_user)
):
    """Approve a question (admin only)"""
    result = question_service.approve_question(question_id, current_user.id)
    
    if result['success']:
        return result
    else:
        raise HTTPException(status_code=403, detail=result['error'])

# Helper endpoints for dropdowns
@router.get("/meta/topics", response_model=List[str])
async def get_all_topics():
    """Get all available topics"""
    return question_service.get_all_topics()

@router.get("/meta/companies", response_model=List[dict])
async def get_all_companies():
    """Get all available companies"""
    return question_service.get_all_companies()

@router.get("/meta/time-periods", response_model=List[str])
async def get_time_periods():
    """Get all available time periods"""
    return question_service.get_time_periods()

@router.get("/meta/difficulties", response_model=List[str])
async def get_difficulties():
    """Get all available difficulty levels"""
    return question_service.get_difficulties()
