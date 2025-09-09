"""
Controller for user question management
"""
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, status
from app.services.user_question_service import UserQuestionService
from app.schemas.user_question_schemas import (
    UserQuestionCreate, UserQuestionUpdate, UserQuestionResponse,
    QuestionReferenceCreate, QuestionReferenceResponse,
    UserQuestionCompanyCreate, QuestionListResponse, ApprovalRequestUpdate
)


class UserQuestionController:
    
    def __init__(self):
        self.service = UserQuestionService()
    
    def create_question(self, question_data: UserQuestionCreate, user_id: int) -> UserQuestionResponse:
        """Create a new user question"""
        try:
            from app.utils.logging import logger
            logger.debug(f"Creating question with data: {question_data}")
            logger.debug(f"User ID: {user_id}")
            return self.service.create_user_question(question_data, user_id)
        except Exception as e:
            from app.utils.logging import logger
            logger.error(f"Failed to create question: {str(e)}")
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create question: {str(e)}"
            )
    
    def get_question(self, question_id: int, user_id: Optional[int] = None) -> UserQuestionResponse:
        """Get user question by ID"""
        question = self.service.get_user_question(question_id, user_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found or access denied"
            )
        return question
    
    def get_questions(self, user_id: Optional[int] = None, is_public_only: bool = False,
                     is_approved_only: bool = False, created_by: Optional[int] = None,
                     page: int = 1, per_page: int = 20) -> QuestionListResponse:
        """Get user questions with filtering"""
        if per_page > 100:
            per_page = 100  # Limit max per page
        
        return self.service.get_user_questions(
            user_id=user_id,
            is_public_only=is_public_only,
            is_approved_only=is_approved_only,
            created_by=created_by,
            page=page,
            per_page=per_page
        )
    
    def update_question(self, question_id: int, question_data: UserQuestionUpdate,
                       user_id: int) -> UserQuestionResponse:
        """Update user question"""
        question = self.service.update_user_question(question_id, question_data, user_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found or access denied"
            )
        return question
    
    def delete_question(self, question_id: int, user_id: int) -> Dict[str, str]:
        """Delete user question"""
        success = self.service.delete_user_question(question_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found or access denied"
            )
        return {"message": "Question deleted successfully"}
    
    def request_public_approval(self, question_id: int, user_id: int) -> Dict[str, str]:
        """Request approval to make question public"""
        success = self.service.request_public_approval(question_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to request public approval. Question may not exist, already be public, or request may already exist"
            )
        return {"message": "Public approval request submitted successfully"}
    
    def approve_question_public(self, question_id: int, admin_id: int,
                               approval_data: ApprovalRequestUpdate) -> Dict[str, str]:
        """Approve question to be public (admin only)"""
        if approval_data.status.value == "approved":
            success = self.service.approve_question_public(
                question_id, admin_id, approval_data.admin_notes
            )
        else:
            success = self.service.reject_question_public(
                question_id, admin_id, approval_data.admin_notes
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process approval request"
            )
        
        action = "approved" if approval_data.status.value == "approved" else "rejected"
        return {"message": f"Question public request {action} successfully"}
    
    def create_reference(self, reference_data: QuestionReferenceCreate,
                        user_id: int) -> QuestionReferenceResponse:
        """Create a question reference"""
        try:
            return self.service.create_question_reference(reference_data, user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create reference: {str(e)}"
            )
    
    def get_references(self, question_id: Optional[int] = None,
                      user_question_id: Optional[int] = None,
                      user_id: Optional[int] = None) -> List[QuestionReferenceResponse]:
        """Get question references"""
        return self.service.get_question_references(question_id, user_question_id, user_id)
    
    def approve_reference(self, reference_id: int, admin_id: int,
                         approval_data: ApprovalRequestUpdate) -> Dict[str, str]:
        """Approve question reference (admin only)"""
        success = self.service.approve_question_reference(
            reference_id, admin_id, approval_data.admin_notes
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to approve reference"
            )
        return {"message": "Reference approved successfully"}
    
    def create_company_association(self, question_id: int, company_data, user_id: int):
        """Create a company association for user question"""
        try:
            return self.service.create_company_association(question_id, company_data, user_id)
        except Exception as e:
            from app.utils.logging import logger
            logger.error(f"Failed to create company association: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create company association: {str(e)}"
            )
    
    def toggle_favorite(self, user_id: int, question_id: Optional[int] = None,
                       user_question_id: Optional[int] = None) -> Dict[str, str]:
        """Toggle question favorite status"""
        if not question_id and not user_question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either question_id or user_question_id must be provided"
            )
        
        success = self.service.toggle_favorite(user_id, question_id, user_question_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to toggle favorite status"
            )
        return {"message": "Favorite status updated successfully"}
    
    def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's favorite questions"""
        return self.service.get_user_favorites(user_id)
    
    def get_pending_approvals(self, admin_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get pending approval requests (admin only)"""
        approvals = self.service.get_pending_approvals(admin_id)
        if approvals is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return approvals
    
    def get_admin_stats(self, admin_id: int) -> Dict[str, int]:
        """Get admin statistics"""
        stats = self.service.get_admin_stats(admin_id)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return stats
