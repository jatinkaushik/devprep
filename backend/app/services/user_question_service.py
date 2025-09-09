"""
Service layer for user question management
"""
from typing import List, Optional, Tuple, Dict, Any
from app.repositories.user_question_repository import UserQuestionRepository
from app.repositories.user_repository import UserRepository
from app.models.user_models import UserQuestion, QuestionReference, UserRole, QuestionDifficulty
from app.schemas.user_question_schemas import (
    UserQuestionCreate, UserQuestionUpdate, UserQuestionResponse,
    QuestionReferenceCreate, QuestionReferenceResponse,
    UserQuestionCompanyCreate, UserQuestionCompanyResponse,
    QuestionListResponse
)


class UserQuestionService:
    
    def __init__(self):
        self.user_question_repo = UserQuestionRepository()
        self.user_repo = UserRepository()
    
    def create_user_question(self, question_data: UserQuestionCreate, user_id: int) -> UserQuestionResponse:
        """Create a new user question"""
        user_question = self.user_question_repo.create_user_question(
            title=question_data.title,
            created_by=user_id,
            difficulty=question_data.difficulty,
            description=question_data.description,
            topics=question_data.topics,
            solution=question_data.solution,
            link=question_data.link
        )
        
        # Request public approval if requested
        if question_data.request_public:
            self.user_question_repo.request_public_approval(user_question.id, user_id)
        
        return self._convert_to_response(user_question)
    
    def get_user_question(self, question_id: int, user_id: Optional[int] = None) -> Optional[UserQuestionResponse]:
        """Get user question by ID"""
        user_question = self.user_question_repo.get_user_question_by_id(question_id, user_id)
        if not user_question:
            return None
        
        # Check permissions
        if not user_question.is_public and user_question.created_by != user_id:
            user = self.user_repo.get_user_by_id(user_id) if user_id else None
            if not user or user.role != UserRole.ADMIN:
                return None
        
        return self._convert_to_response(user_question, user_id)
    
    def get_user_questions(self, user_id: Optional[int] = None, is_public_only: bool = False,
                          is_approved_only: bool = False, created_by: Optional[int] = None,
                          page: int = 1, per_page: int = 20) -> QuestionListResponse:
        """Get user questions with filtering"""
        questions, total = self.user_question_repo.get_user_questions(
            user_id=user_id,
            is_public_only=is_public_only,
            is_approved_only=is_approved_only,
            created_by=created_by,
            page=page,
            per_page=per_page
        )
        
        question_responses = [self._convert_to_response(q, user_id) for q in questions]
        total_pages = (total + per_page - 1) // per_page
        
        return QuestionListResponse(
            questions=question_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    def update_user_question(self, question_id: int, question_data: UserQuestionUpdate,
                            user_id: int) -> Optional[UserQuestionResponse]:
        """Update user question"""
        user_question = self.user_question_repo.get_user_question_by_id(question_id)
        if not user_question:
            return None
        
        # Check permissions
        if user_question.created_by != user_id:
            user = self.user_repo.get_user_by_id(user_id)
            if not user or user.role != UserRole.ADMIN:
                return None
        
        update_data = question_data.dict(exclude_unset=True)
        updated_question = self.user_question_repo.update_user_question(question_id, **update_data)
        
        if updated_question:
            return self._convert_to_response(updated_question, user_id)
        return None
    
    def delete_user_question(self, question_id: int, user_id: int) -> bool:
        """Delete user question"""
        user_question = self.user_question_repo.get_user_question_by_id(question_id)
        if not user_question:
            return False
        
        # Check permissions
        if user_question.created_by != user_id:
            user = self.user_repo.get_user_by_id(user_id)
            if not user or user.role != UserRole.ADMIN:
                return False
        
        return self.user_question_repo.delete_user_question(question_id)
    
    def request_public_approval(self, question_id: int, user_id: int) -> bool:
        """Request approval to make question public"""
        user_question = self.user_question_repo.get_user_question_by_id(question_id)
        if not user_question or user_question.created_by != user_id:
            return False
        
        if user_question.is_public:
            return False  # Already public
        
        return self.user_question_repo.request_public_approval(question_id, user_id)
    
    def approve_question_public(self, question_id: int, admin_id: int,
                               admin_notes: Optional[str] = None) -> bool:
        """Approve question to be public (admin only)"""
        admin = self.user_repo.get_user_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return False
        
        return self.user_question_repo.approve_question_public(question_id, admin_id, admin_notes)
    
    def reject_question_public(self, question_id: int, admin_id: int,
                              admin_notes: Optional[str] = None) -> bool:
        """Reject question public request (admin only)"""
        admin = self.user_repo.get_user_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return False
        
        return self.user_question_repo.reject_question_public(question_id, admin_id, admin_notes)
    
    def create_question_reference(self, reference_data: QuestionReferenceCreate,
                                 user_id: int) -> QuestionReferenceResponse:
        """Create a question reference"""
        user = self.user_repo.get_user_by_id(user_id)
        auto_approve = user and user.role == UserRole.ADMIN
        
        reference = self.user_question_repo.create_question_reference(
            url=reference_data.url,
            created_by=user_id,
            title=reference_data.title,
            description=reference_data.description,
            question_id=reference_data.question_id,
            user_question_id=reference_data.user_question_id,
            auto_approve_admin=auto_approve
        )
        
        return self._convert_reference_to_response(reference)
    
    def get_question_references(self, question_id: Optional[int] = None,
                               user_question_id: Optional[int] = None,
                               user_id: Optional[int] = None) -> List[QuestionReferenceResponse]:
        """Get question references"""
        user = self.user_repo.get_user_by_id(user_id) if user_id else None
        is_admin = user and user.role == UserRole.ADMIN
        
        # Only show approved references to non-admin users
        is_approved_only = not is_admin
        
        references = self.user_question_repo.get_question_references(
            question_id=question_id,
            user_question_id=user_question_id,
            is_approved_only=is_approved_only
        )
        
        return [self._convert_reference_to_response(ref) for ref in references]
    
    def approve_question_reference(self, reference_id: int, admin_id: int,
                                  admin_notes: Optional[str] = None) -> bool:
        """Approve question reference (admin only)"""
        admin = self.user_repo.get_user_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return False
        
        return self.user_question_repo.approve_question_reference(reference_id, admin_id, admin_notes)
    
    def toggle_favorite(self, user_id: int, question_id: Optional[int] = None,
                       user_question_id: Optional[int] = None) -> bool:
        """Toggle question favorite status"""
        favorites = self.user_question_repo.get_user_favorites(user_id)
        
        # Check if already favorited
        is_favorited = any(
            (fav['question_id'] == question_id and question_id is not None) or
            (fav['user_question_id'] == user_question_id and user_question_id is not None)
            for fav in favorites
        )
        
        if is_favorited:
            return self.user_question_repo.remove_favorite(user_id, question_id, user_question_id)
        else:
            return self.user_question_repo.add_favorite(user_id, question_id, user_question_id)
    
    def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's favorite questions"""
        return self.user_question_repo.get_user_favorites(user_id)
    
    def get_pending_approvals(self, admin_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get pending approval requests (admin only)"""
        admin = self.user_repo.get_user_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return {}
        
        requests = self.user_question_repo.get_pending_approval_requests()
        
        # Group by request type
        grouped = {
            'question_public': [],
            'reference': [],
            'company_association': []
        }
        
        for request in requests:
            grouped[request['request_type']].append(request)
        
        return grouped
    
    def get_admin_stats(self, admin_id: int) -> Optional[Dict[str, int]]:
        """Get admin statistics"""
        admin = self.user_repo.get_user_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            return None
        
        # This would need additional repository methods
        # For now, return basic stats
        return {
            'total_user_questions': 0,
            'pending_question_approvals': 0,
            'pending_reference_approvals': 0,
            'questions_approved_today': 0,
            'references_approved_today': 0
        }
    
    def create_company_association(self, question_id: int, company_data: UserQuestionCompanyCreate, 
                                 user_id: int) -> UserQuestionCompanyResponse:
        """Create a company association for user question"""
        # Verify the question exists and user has permission
        question = self.user_question_repo.get_user_question_by_id(question_id, user_id)
        if not question:
            raise ValueError("Question not found or access denied")
        
        # Verify user owns the question or is admin
        if question.created_by != user_id:
            user = self.user_repo.get_user_by_id(user_id)
            if not user or user.role != UserRole.ADMIN:
                raise ValueError("Permission denied")
        
        # Create the company association
        association = self.user_question_repo.create_company_association(
            question_id=question_id,
            company_id=company_data.company_id,
            time_period=company_data.time_period,
            frequency=company_data.frequency,
            created_by=user_id
        )
        
        # Return a simple dict instead of full schema validation for now
        return {
            "id": association.id,
            "company_id": association.company_id,
            "company_name": getattr(association, 'company_name', None),
            "time_period": association.time_period,
            "frequency": association.frequency,
            "is_approved": association.is_approved,
            "created_by": association.created_by,
            "creator_username": getattr(association, 'creator_username', None),
            "approved_by": association.approved_by,
            "approver_username": getattr(association, 'approver_username', None),
            "created_at": association.created_at.isoformat() if association.created_at else None,
            "approved_at": association.approved_at.isoformat() if association.approved_at else None
        }
    
    def get_user_question_companies(self, question_id: int, user_id: Optional[int] = None) -> List[UserQuestionCompanyResponse]:
        """Get company associations for a user question"""
        user = self.user_repo.get_user_by_id(user_id) if user_id else None
        is_admin = user and user.role == UserRole.ADMIN
        
        # Show all associations to the creator or admin, only approved to others
        question = self.user_question_repo.get_user_question_by_id(question_id)
        is_creator = question and question.created_by == user_id
        
        # Temporarily show all associations (not filtering by approval)
        is_approved_only = False  # not (is_admin or is_creator)
        
        associations = self.user_question_repo.get_company_associations(
            question_id=question_id,
            is_approved_only=is_approved_only
        )
        
        company_responses = []
        for assoc in associations:
            company_responses.append(UserQuestionCompanyResponse(
                id=assoc.id,
                company_id=assoc.company_id,
                company_name=getattr(assoc, 'company_name', None),
                time_period=assoc.time_period,
                frequency=assoc.frequency,
                is_approved=assoc.is_approved,
                created_by=assoc.created_by,
                creator_username=getattr(assoc, 'creator_username', None),
                approved_by=assoc.approved_by,
                approver_username=getattr(assoc, 'approver_username', None),
                created_at=assoc.created_at,
                approved_at=assoc.approved_at
            ))
        
        return company_responses
    
    def _convert_to_response(self, user_question: UserQuestion, 
                           current_user_id: Optional[int] = None) -> UserQuestionResponse:
        """Convert UserQuestion model to response schema"""
        # Get additional data
        references = self.get_question_references(user_question_id=user_question.id, 
                                                 user_id=current_user_id)
        
        # Get company associations
        companies = self.get_user_question_companies(user_question.id, current_user_id)
        
        return UserQuestionResponse(
            id=user_question.id,
            title=user_question.title,
            description=user_question.description,
            difficulty=user_question.difficulty,
            topics=user_question.topics,
            solution=user_question.solution,
            link=user_question.link,
            is_public=user_question.is_public,
            is_approved=user_question.is_approved,
            created_by=user_question.created_by,
            creator_username=getattr(user_question, 'creator_username', None),
            approved_by=user_question.approved_by,
            approver_username=getattr(user_question, 'approver_username', None),
            created_at=user_question.created_at,
            updated_at=user_question.updated_at,
            approved_at=user_question.approved_at,
            references=references,
            companies=companies,
            is_favorited=getattr(user_question, 'is_favorited', False)
        )
    
    def _convert_reference_to_response(self, reference: QuestionReference) -> QuestionReferenceResponse:
        """Convert QuestionReference model to response schema"""
        return QuestionReferenceResponse(
            id=reference.id,
            url=reference.url,
            title=reference.title,
            description=reference.description,
            is_approved=reference.is_approved,
            created_by=reference.created_by,
            creator_username=getattr(reference, 'creator_username', None),
            approved_by=reference.approved_by,
            approver_username=getattr(reference, 'approver_username', None),
            created_at=reference.created_at,
            approved_at=reference.approved_at
        )
