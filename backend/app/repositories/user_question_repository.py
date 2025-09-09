"""
Repository for user question management and related operations
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from app.config.database import get_db_connection
from app.models.user_models import (
    UserQuestion, QuestionReference, UserQuestionCompany, 
    ApprovalRequest, UserFavorite, QuestionDifficulty, 
    ApprovalStatus, RequestType, EntityType
)


class UserQuestionRepository:
    
    def create_user_question(self, title: str, created_by: int, difficulty: QuestionDifficulty,
                            description: Optional[str] = None, topics: Optional[List[str]] = None,
                            solution: Optional[str] = None, link: Optional[str] = None) -> UserQuestion:
        """Create a new user question"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            topics_json = json.dumps(topics) if topics else None
            
            cursor.execute("""
                INSERT INTO user_questions (title, description, difficulty, topics, solution, link, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, difficulty.value, topics_json, solution, link, created_by))
            
            question_id = cursor.lastrowid
            conn.commit()
            
            return self.get_user_question_by_id(question_id)
    
    def get_user_question_by_id(self, question_id: int, user_id: Optional[int] = None) -> Optional[UserQuestion]:
        """Get user question by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uq.*, u.username as creator_username,
                       au.username as approver_username,
                       CASE WHEN uf.id IS NOT NULL THEN 1 ELSE 0 END as is_favorited
                FROM user_questions uq
                JOIN users u ON uq.created_by = u.id
                LEFT JOIN users au ON uq.approved_by = au.id
                LEFT JOIN user_favorites uf ON uf.user_question_id = uq.id AND uf.user_id = ?
                WHERE uq.id = ?
            """, (user_id, question_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_user_question(row)
    
    def get_user_questions(self, user_id: Optional[int] = None, is_public_only: bool = False,
                          is_approved_only: bool = False, created_by: Optional[int] = None,
                          page: int = 1, per_page: int = 20) -> Tuple[List[UserQuestion], int]:
        """Get user questions with filtering"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if is_public_only:
                conditions.append("uq.is_public = 1")
            
            if is_approved_only:
                conditions.append("uq.is_approved = 1")
            
            if created_by:
                conditions.append("uq.created_by = ?")
                params.append(created_by)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Get total count
            cursor.execute(f"""
                SELECT COUNT(*) FROM user_questions uq WHERE {where_clause}
            """, params)
            total = cursor.fetchone()[0]
            
            # Get questions with pagination
            offset = (page - 1) * per_page
            cursor.execute(f"""
                SELECT uq.*, u.username as creator_username,
                       au.username as approver_username,
                       CASE WHEN uf.id IS NOT NULL THEN 1 ELSE 0 END as is_favorited
                FROM user_questions uq
                JOIN users u ON uq.created_by = u.id
                LEFT JOIN users au ON uq.approved_by = au.id
                LEFT JOIN user_favorites uf ON uf.user_question_id = uq.id AND uf.user_id = ?
                WHERE {where_clause}
                ORDER BY uq.created_at DESC
                LIMIT ? OFFSET ?
            """, [user_id] + params + [per_page, offset])
            
            questions = [self._row_to_user_question(row) for row in cursor.fetchall()]
            return questions, total
    
    def update_user_question(self, question_id: int, **kwargs) -> Optional[UserQuestion]:
        """Update user question"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            for field, value in kwargs.items():
                if field == 'topics' and value is not None:
                    value = json.dumps(value)
                update_fields.append(f"{field} = ?")
                params.append(value)
            
            if not update_fields:
                return self.get_user_question_by_id(question_id)
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(question_id)
            
            cursor.execute(f"""
                UPDATE user_questions 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            return self.get_user_question_by_id(question_id)
    
    def delete_user_question(self, question_id: int) -> bool:
        """Delete user question"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_questions WHERE id = ?", (question_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def request_public_approval(self, question_id: int, user_id: int) -> bool:
        """Request approval to make question public"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if request already exists
            cursor.execute("""
                SELECT id FROM approval_requests 
                WHERE entity_id = ? AND entity_type = 'user_question' 
                AND request_type = 'question_public' AND status = 'pending'
            """, (question_id,))
            
            if cursor.fetchone():
                return False  # Request already exists
            
            cursor.execute("""
                INSERT INTO approval_requests (request_type, entity_id, entity_type, requested_by)
                VALUES ('question_public', ?, 'user_question', ?)
            """, (question_id, user_id))
            
            conn.commit()
            return True
    
    def approve_question_public(self, question_id: int, admin_id: int, 
                               admin_notes: Optional[str] = None) -> bool:
        """Approve question to be public"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update question
            cursor.execute("""
                UPDATE user_questions 
                SET is_public = 1, is_approved = 1, approved_by = ?, approved_at = ?
                WHERE id = ?
            """, (admin_id, datetime.now().isoformat(), question_id))
            
            # Update approval request
            cursor.execute("""
                UPDATE approval_requests 
                SET status = 'approved', processed_by = ?, processed_at = ?, admin_notes = ?
                WHERE entity_id = ? AND entity_type = 'user_question' 
                AND request_type = 'question_public' AND status = 'pending'
            """, (admin_id, datetime.now().isoformat(), admin_notes, question_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def reject_question_public(self, question_id: int, admin_id: int, 
                              admin_notes: Optional[str] = None) -> bool:
        """Reject question public request"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE approval_requests 
                SET status = 'rejected', processed_by = ?, processed_at = ?, admin_notes = ?
                WHERE entity_id = ? AND entity_type = 'user_question' 
                AND request_type = 'question_public' AND status = 'pending'
            """, (admin_id, datetime.now().isoformat(), admin_notes, question_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Question References
    def create_question_reference(self, url: str, created_by: int, title: Optional[str] = None,
                                 description: Optional[str] = None, question_id: Optional[int] = None,
                                 user_question_id: Optional[int] = None, 
                                 auto_approve_admin: bool = False) -> QuestionReference:
        """Create a question reference"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            is_approved = auto_approve_admin
            approved_by = created_by if auto_approve_admin else None
            approved_at = datetime.now().isoformat() if auto_approve_admin else None
            
            cursor.execute("""
                INSERT INTO question_references 
                (question_id, user_question_id, url, title, description, 
                 is_approved, created_by, approved_by, approved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (question_id, user_question_id, url, title, description,
                  is_approved, created_by, approved_by, approved_at))
            
            reference_id = cursor.lastrowid
            
            # Create approval request if not auto-approved
            if not auto_approve_admin:
                cursor.execute("""
                    INSERT INTO approval_requests (request_type, entity_id, entity_type, requested_by)
                    VALUES ('reference', ?, 'question_reference', ?)
                """, (reference_id, created_by))
            
            conn.commit()
            return self.get_question_reference_by_id(reference_id)
    
    def get_question_reference_by_id(self, reference_id: int) -> Optional[QuestionReference]:
        """Get question reference by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT qr.*, u.username as creator_username, au.username as approver_username
                FROM question_references qr
                JOIN users u ON qr.created_by = u.id
                LEFT JOIN users au ON qr.approved_by = au.id
                WHERE qr.id = ?
            """, (reference_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_question_reference(row)
    
    def get_question_references(self, question_id: Optional[int] = None,
                               user_question_id: Optional[int] = None,
                               is_approved_only: bool = False) -> List[QuestionReference]:
        """Get question references"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if question_id:
                conditions.append("qr.question_id = ?")
                params.append(question_id)
            
            if user_question_id:
                conditions.append("qr.user_question_id = ?")
                params.append(user_question_id)
            
            if is_approved_only:
                conditions.append("qr.is_approved = 1")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor.execute(f"""
                SELECT qr.*, u.username as creator_username, au.username as approver_username
                FROM question_references qr
                JOIN users u ON qr.created_by = u.id
                LEFT JOIN users au ON qr.approved_by = au.id
                WHERE {where_clause}
                ORDER BY qr.created_at DESC
            """, params)
            
            return [self._row_to_question_reference(row) for row in cursor.fetchall()]
    
    def approve_question_reference(self, reference_id: int, admin_id: int,
                                  admin_notes: Optional[str] = None) -> bool:
        """Approve question reference"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update reference
            cursor.execute("""
                UPDATE question_references 
                SET is_approved = 1, approved_by = ?, approved_at = ?
                WHERE id = ?
            """, (admin_id, datetime.now().isoformat(), reference_id))
            
            # Update approval request
            cursor.execute("""
                UPDATE approval_requests 
                SET status = 'approved', processed_by = ?, processed_at = ?, admin_notes = ?
                WHERE entity_id = ? AND entity_type = 'question_reference' 
                AND request_type = 'reference' AND status = 'pending'
            """, (admin_id, datetime.now().isoformat(), admin_notes, reference_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Company Associations
    def create_company_association(self, question_id: int, company_id: int, 
                                 time_period: str, frequency: float, 
                                 created_by: int) -> UserQuestionCompany:
        """Create a company association for user question"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_question_companies 
                (user_question_id, company_id, time_period, frequency, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (question_id, company_id, time_period, frequency, created_by))
            
            association_id = cursor.lastrowid
            conn.commit()
            
            # Get the created association with company name
            cursor.execute("""
                SELECT uqc.*, c.name as company_name, u.username as creator_username
                FROM user_question_companies uqc
                JOIN companies c ON uqc.company_id = c.id
                JOIN users u ON uqc.created_by = u.id
                WHERE uqc.id = ?
            """, (association_id,))
            
            row = cursor.fetchone()
            if row:
                from app.utils.logging import logger
                logger.info(f"Company association row data: {dict(row)}")
                return UserQuestionCompany(
                    id=row['id'],
                    user_question_id=row['user_question_id'],
                    company_id=row['company_id'],
                    time_period=row['time_period'],
                    frequency=row['frequency'],
                    is_approved=bool(row['is_approved']),
                    created_by=row['created_by'],
                    approved_by=row['approved_by'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    approved_at=datetime.fromisoformat(row['approved_at']) if row['approved_at'] else None
                )
            return None
    
    def get_company_associations(self, question_id: int, is_approved_only: bool = False) -> List[UserQuestionCompany]:
        """Get company associations for a user question"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT uqc.*, c.name as company_name, u.username as creator_username,
                       au.username as approver_username
                FROM user_question_companies uqc
                JOIN companies c ON uqc.company_id = c.id
                LEFT JOIN users u ON uqc.created_by = u.id
                LEFT JOIN users au ON uqc.approved_by = au.id
                WHERE uqc.user_question_id = ?
            """
            
            params = [question_id]
            
            if is_approved_only:
                query += " AND uqc.is_approved = 1"
            
            query += " ORDER BY uqc.created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            associations = []
            for row in rows:
                # Create the association with the company_name attribute
                assoc = UserQuestionCompany(
                    id=row['id'],
                    user_question_id=row['user_question_id'],
                    company_id=row['company_id'],
                    time_period=row['time_period'],
                    frequency=row['frequency'],
                    is_approved=bool(row['is_approved']),
                    created_by=row['created_by'],
                    approved_by=row['approved_by'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    approved_at=datetime.fromisoformat(row['approved_at']) if row['approved_at'] else None
                )
                # Add the company_name as an attribute
                setattr(assoc, 'company_name', row['company_name'])
                setattr(assoc, 'creator_username', row['creator_username'])
                setattr(assoc, 'approver_username', row['approver_username'])
                associations.append(assoc)
            
            return associations
    
    # Favorites
    def add_favorite(self, user_id: int, question_id: Optional[int] = None,
                    user_question_id: Optional[int] = None) -> bool:
        """Add question to favorites"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO user_favorites (user_id, question_id, user_question_id)
                    VALUES (?, ?, ?)
                """, (user_id, question_id, user_question_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Already favorited
    
    def remove_favorite(self, user_id: int, question_id: Optional[int] = None,
                       user_question_id: Optional[int] = None) -> bool:
        """Remove question from favorites"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if question_id:
                cursor.execute("""
                    DELETE FROM user_favorites 
                    WHERE user_id = ? AND question_id = ?
                """, (user_id, question_id))
            else:
                cursor.execute("""
                    DELETE FROM user_favorites 
                    WHERE user_id = ? AND user_question_id = ?
                """, (user_id, user_question_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's favorite questions"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uf.*, 
                       q.title as question_title, q.difficulty as question_difficulty,
                       uq.title as user_question_title, uq.difficulty as user_question_difficulty
                FROM user_favorites uf
                LEFT JOIN questions q ON uf.question_id = q.id
                LEFT JOIN user_questions uq ON uf.user_question_id = uq.id
                WHERE uf.user_id = ?
                ORDER BY uf.created_at DESC
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Approval Requests
    def get_pending_approval_requests(self, request_type: Optional[RequestType] = None) -> List[Dict[str, Any]]:
        """Get pending approval requests"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            where_clause = "ar.status = 'pending'"
            params = []
            
            if request_type:
                where_clause += " AND ar.request_type = ?"
                params.append(request_type.value)
            
            cursor.execute(f"""
                SELECT ar.*, u.username as requester_username
                FROM approval_requests ar
                JOIN users u ON ar.requested_by = u.id
                WHERE {where_clause}
                ORDER BY ar.created_at ASC
            """, params)
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Helper methods
    def _row_to_user_question(self, row) -> UserQuestion:
        """Convert database row to UserQuestion object"""
        topics = json.loads(row['topics']) if row['topics'] else None
        
        return UserQuestion(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            difficulty=QuestionDifficulty(row['difficulty']),
            topics=topics,
            solution=row['solution'],
            link=row['link'],
            is_public=bool(row['is_public']),
            is_approved=bool(row['is_approved']),
            created_by=row['created_by'],
            approved_by=row['approved_by'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            approved_at=datetime.fromisoformat(row['approved_at']) if row['approved_at'] else None
        )
    
    def _row_to_question_reference(self, row) -> QuestionReference:
        """Convert database row to QuestionReference object"""
        return QuestionReference(
            id=row['id'],
            question_id=row['question_id'],
            user_question_id=row['user_question_id'],
            url=row['url'],
            title=row['title'],
            description=row['description'],
            is_approved=bool(row['is_approved']),
            created_by=row['created_by'],
            approved_by=row['approved_by'],
            created_at=datetime.fromisoformat(row['created_at']),
            approved_at=datetime.fromisoformat(row['approved_at']) if row['approved_at'] else None
        )
