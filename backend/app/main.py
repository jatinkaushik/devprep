"""
FastAPI application with class-based architecture
"""
import os
from fastapi import FastAPI, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import config
from app.utils.logging import logger
from app.controllers.question_controller import QuestionController
from app.controllers.company_controller import CompanyController
from app.controllers.user_controller import UserController
from app.controllers.user_question_controller import UserQuestionController
from app.schemas.user_schemas import UserCreate, LoginRequest, UserResponse, LoginResponse
from app.schemas.question_schemas import QuestionResponse
from app.schemas.user_question_schemas import (
    UserQuestionCreate, UserQuestionUpdate, UserQuestionResponse,
    QuestionReferenceCreate, QuestionReferenceResponse,
    UserQuestionCompanyCreate, QuestionListResponse, ApprovalRequestUpdate, CompanyCreate, CompanyResponse
)
from app.utils.auth import get_current_active_user, get_admin_user, get_current_user_optional
from app.models.user_models import User
from typing import Optional, List


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    logger.info("Starting FastAPI application initialization")
    
    # Ensure logs directory exists
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(backend_dir, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        logger.info(f"Created logs directory at {logs_dir}")
    
    app = FastAPI(
        title=config.title,
        version=config.version,
        description=config.description
    )
    
    logger.info(f"Created FastAPI application: {config.title} v{config.version}")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize controllers
    question_controller = QuestionController()
    company_controller = CompanyController()
    user_controller = UserController()
    user_question_controller = UserQuestionController()
    
    # Register routes
    @app.get("/")
    async def root():
        return {"message": config.title}
    
    @app.get("/api/companies", response_model=list)
    async def get_companies():
        """Get all companies"""
        return company_controller.get_companies()
    
    @app.get("/api/difficulties")
    async def get_difficulties():
        """Get all difficulty levels"""
        return question_controller.get_difficulties()
    
    @app.get("/api/time-periods")
    async def get_time_periods():
        """Get all time periods"""
        return question_controller.get_time_periods()
    
    @app.get("/api/topics")
    async def get_topics():
        """Get all unique topics"""
        return question_controller.get_topics()
    
    @app.get("/api/questions", response_model=QuestionResponse)
    async def get_questions(
        companies: str = None,
        company_logic: str = "OR",
        difficulties: str = None,
        time_periods: str = None,
        time_period_logic: str = "OR",
        topics: str = None,
        search: str = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "frequency",
        sort_order: str = "desc",
        authorization: Optional[str] = Header(None, convert_underscores=False)
    ):
        """Get questions with filters"""
        # Convert string parameters to enums
        from app.schemas.question_schemas import LogicEnum, SortByEnum, SortOrderEnum
        
        company_logic_enum = LogicEnum.AND if company_logic == "AND" else LogicEnum.OR
        time_period_logic_enum = LogicEnum.AND if time_period_logic == "AND" else LogicEnum.OR
        sort_by_enum = SortByEnum.TITLE if sort_by == "title" else SortByEnum.DIFFICULTY if sort_by == "difficulty" else SortByEnum.FREQUENCY
        sort_order_enum = SortOrderEnum.ASC if sort_order == "asc" else SortOrderEnum.DESC
        
        return question_controller.get_questions(
            companies=companies,
            company_logic=company_logic_enum,
            difficulties=difficulties,
            time_periods=time_periods,
            time_period_logic=time_period_logic_enum,
            topics=topics,
            search=search,
            page=page,
            per_page=per_page,
            sort_by=sort_by_enum,
            sort_order=sort_order_enum,
            authorization=authorization
        )
    
    @app.get("/api/random-questions", response_model=QuestionResponse)
    async def get_random_questions(
        count: int = Query(5, ge=1, le=20, description="Number of random questions to return"),
        companies: str = None,
        company_logic: str = "OR",
        difficulties: str = None,
        time_periods: str = None,
        time_period_logic: str = "OR", 
        topics: str = None,
        authorization: Optional[str] = Header(None, convert_underscores=False)
    ):
        """Get random questions with optional filters"""
        # Convert string parameters to enums
        from app.schemas.question_schemas import LogicEnum
        
        company_logic_enum = LogicEnum.AND if company_logic == "AND" else LogicEnum.OR
        time_period_logic_enum = LogicEnum.AND if time_period_logic == "AND" else LogicEnum.OR
        
        return question_controller.get_random_questions(
            count=count,
            companies=companies,
            company_logic=company_logic_enum,
            difficulties=difficulties,
            time_periods=time_periods,
            time_period_logic=time_period_logic_enum,
            topics=topics,
            authorization=authorization
        )
    
    @app.get("/api/stats")
    async def get_stats():
        """Get overall statistics"""
        return question_controller.get_stats()
    
    # Authentication routes
    @app.post("/api/auth/register", response_model=UserResponse)
    async def register(user_data: UserCreate):
        """Register a new user"""
        return user_controller.register(user_data)
    
    @app.post("/api/auth/login", response_model=LoginResponse)
    async def login(login_data: LoginRequest):
        """Login user"""
        return user_controller.login(login_data)
    
    @app.get("/api/auth/me", response_model=UserResponse)
    async def get_profile(current_user: User = Depends(get_current_active_user)):
        """Get current user profile"""
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at
        )
    
    # User Questions routes
    @app.post("/api/user-questions", response_model=UserQuestionResponse)
    async def create_user_question(
        question_data: UserQuestionCreate,
        current_user: User = Depends(get_current_active_user)
    ):
        """Create a new user question"""
        return user_question_controller.create_question(question_data, current_user.id)
    
    @app.get("/api/user-questions", response_model=QuestionListResponse)
    async def get_user_questions(
        is_public_only: bool = False,
        is_approved_only: bool = False,
        created_by: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        current_user: Optional[User] = Depends(get_current_user_optional)
    ):
        """Get user questions with filtering"""
        user_id = current_user.id if current_user else None
        return user_question_controller.get_questions(
            user_id=user_id,
            is_public_only=is_public_only,
            is_approved_only=is_approved_only,
            created_by=created_by,
            page=page,
            per_page=per_page
        )
    
    @app.get("/api/user-questions/{question_id}", response_model=UserQuestionResponse)
    async def get_user_question(
        question_id: int,
        current_user: Optional[User] = Depends(get_current_user_optional)
    ):
        """Get user question by ID"""
        user_id = current_user.id if current_user else None
        return user_question_controller.get_question(question_id, user_id)
    
    @app.put("/api/user-questions/{question_id}", response_model=UserQuestionResponse)
    async def update_user_question(
        question_id: int,
        question_data: UserQuestionUpdate,
        current_user: User = Depends(get_current_active_user)
    ):
        """Update user question"""
        return user_question_controller.update_question(question_id, question_data, current_user.id)
    
    @app.delete("/api/user-questions/{question_id}")
    async def delete_user_question(
        question_id: int,
        current_user: User = Depends(get_current_active_user)
    ):
        """Delete user question"""
        return user_question_controller.delete_question(question_id, current_user.id)
    
    @app.post("/api/user-questions/{question_id}/request-public")
    async def request_question_public(
        question_id: int,
        current_user: User = Depends(get_current_active_user)
    ):
        """Request approval to make question public"""
        return user_question_controller.request_public_approval(question_id, current_user.id)
    
    # Question References routes
    @app.post("/api/question-references", response_model=QuestionReferenceResponse)
    async def create_question_reference(
        reference_data: QuestionReferenceCreate,
        current_user: User = Depends(get_current_active_user)
    ):
        """Create a question reference"""
        return user_question_controller.create_reference(reference_data, current_user.id)
    
    @app.get("/api/question-references", response_model=List[QuestionReferenceResponse])
    async def get_question_references(
        question_id: Optional[int] = None,
        user_question_id: Optional[int] = None,
        current_user: Optional[User] = Depends(get_current_user_optional)
    ):
        """Get question references"""
        user_id = current_user.id if current_user else None
        return user_question_controller.get_references(question_id, user_question_id, user_id)
    
    # Company Association routes
    @app.post("/api/user-questions/{question_id}/companies")
    async def create_company_association(
        question_id: int,
        company_data: UserQuestionCompanyCreate,
        current_user: User = Depends(get_current_active_user)
    ):
        """Create a company association for user question"""
        return user_question_controller.create_company_association(question_id, company_data, current_user.id)
    
    # Favorites routes
    @app.post("/api/favorites/toggle")
    async def toggle_favorite(
        question_id: Optional[int] = None,
        user_question_id: Optional[int] = None,
        current_user: User = Depends(get_current_active_user)
    ):
        """Toggle question favorite status"""
        return user_question_controller.toggle_favorite(current_user.id, question_id, user_question_id)
    
    @app.get("/api/favorites")
    async def get_user_favorites(current_user: User = Depends(get_current_active_user)):
        """Get user's favorite questions"""
        return user_question_controller.get_user_favorites(current_user.id)
    
    # Admin routes
    @app.get("/api/admin/pending-approvals")
    async def get_pending_approvals(admin_user: User = Depends(get_admin_user)):
        """Get pending approval requests (admin only)"""
        return user_question_controller.get_pending_approvals(admin_user.id)
    
    @app.post("/api/admin/approve-question/{question_id}")
    async def approve_question_public(
        question_id: int,
        approval_data: ApprovalRequestUpdate,
        admin_user: User = Depends(get_admin_user)
    ):
        """Approve or reject question public request (admin only)"""
        return user_question_controller.approve_question_public(question_id, admin_user.id, approval_data)
    
    @app.post("/api/admin/approve-reference/{reference_id}")
    async def approve_reference(
        reference_id: int,
        approval_data: ApprovalRequestUpdate,
        admin_user: User = Depends(get_admin_user)
    ):
        """Approve question reference (admin only)"""
        return user_question_controller.approve_reference(reference_id, admin_user.id, approval_data)
    
    @app.get("/api/admin/stats")
    async def get_admin_stats(admin_user: User = Depends(get_admin_user)):
        """Get admin statistics"""
        return user_question_controller.get_admin_stats(admin_user.id)
    
    @app.post("/api/admin/companies", response_model=CompanyResponse)
    async def create_company(
        company_data: CompanyCreate,
        admin_user: User = Depends(get_admin_user)
    ):
        """Create a new company (admin only)"""
        # This would need to be implemented in the company controller
        pass
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Docker"""
        return {"status": "healthy", "message": "DevPrep Questions API is running"}
    
    return app


# Create the app instance
app = create_app()
