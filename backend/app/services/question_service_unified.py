from typing import List, Optional, Dict, Any
from ..repositories.question_repo import UnifiedQuestionRepository
from ..repositories.company_repository import CompanyRepository

class UnifiedQuestionService:
    def __init__(self):
        self.repository = UnifiedQuestionRepository()
        self.company_repo = CompanyRepository()
    
    def create_question(self, question_data: dict, user_id: int) -> Dict[str, Any]:
        """Create a new question"""
        try:
            question_id = self.repository.create_question(question_data, user_id)
            
            # Add company associations if provided
            if question_data.get('companies'):
                for company_data in question_data['companies']:
                    self.repository.add_company_association(question_id, company_data)
            
            return {
                'success': True,
                'question_id': question_id,
                'message': 'Question created successfully. It will be visible after admin approval.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_question_by_id(self, question_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a question by ID with user permissions"""
        question = self.repository.get_question_by_id(question_id)
        if not question:
            return None
        
        # Add user permissions
        if user_id:
            question['can_edit'] = (question['added_by'] == user_id or 
                                  self._is_admin(user_id))
            question['can_delete'] = question['can_edit']
        else:
            question['can_edit'] = False
            question['can_delete'] = False
        
        return question
    
    def get_questions(self, page: int = 1, per_page: int = 20, search: str = None,
                     difficulty: str = None, topic: str = None, user_id: Optional[int] = None,
                     my_questions: bool = False) -> Dict[str, Any]:
        """Get paginated questions with filters"""
        
        # If requesting user's questions, filter by user_id and show unapproved
        if my_questions and user_id:
            result = self.repository.get_questions(
                page=page, per_page=per_page, search=search,
                difficulty=difficulty, topic=topic, user_id=user_id,
                show_unapproved=True
            )
        else:
            # Public questions - only show approved
            result = self.repository.get_questions(
                page=page, per_page=per_page, search=search,
                difficulty=difficulty, topic=topic,
                show_unapproved=False
            )
        
        # Add user permissions to each question
        if user_id:
            for question in result['questions']:
                question['can_edit'] = (question['added_by'] == user_id or 
                                      self._is_admin(user_id))
                question['can_delete'] = question['can_edit']
        
        return result
    
    def update_question(self, question_id: int, question_data: dict, user_id: int) -> Dict[str, Any]:
        """Update a question"""
        try:
            success = self.repository.update_question(question_id, question_data, user_id)
            
            if success:
                # Update company associations if provided
                if 'companies' in question_data:
                    # Remove existing associations (simple approach)
                    # Add new associations
                    for company_data in question_data['companies']:
                        self.repository.add_company_association(question_id, company_data)
                
                return {
                    'success': True,
                    'message': 'Question updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Question not found or permission denied'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_question(self, question_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a question"""
        try:
            success = self.repository.delete_question(question_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Question deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Question not found or permission denied'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def approve_question(self, question_id: int, admin_id: int) -> Dict[str, Any]:
        """Approve a question (admin only)"""
        if not self._is_admin(admin_id):
            return {
                'success': False,
                'error': 'Permission denied'
            }
        
        try:
            success = self.repository.approve_question(question_id, admin_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Question approved successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Question not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_topics(self) -> List[str]:
        """Get all unique topics"""
        return self.repository.get_all_topics()
    
    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies"""
        return self.company_repo.get_all_companies()
    
    def get_time_periods(self) -> List[str]:
        """Get available time periods"""
        return [
            '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015',
            'Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024',
            'Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023'
        ]
    
    def get_difficulties(self) -> List[str]:
        """Get available difficulty levels"""
        return ['Easy', 'Medium', 'Hard']
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        import sqlite3
        conn = sqlite3.connect("devprep_problems.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return row and row[0] == 'admin'
        finally:
            conn.close()
