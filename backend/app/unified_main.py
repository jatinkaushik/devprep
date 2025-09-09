"""
FastAPI application with unified question architecture
"""
import os
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import config
from app.utils.logging import logger
from app.controllers.unified_question_controller import UnifiedQuestionController
from app.controllers.company_controller import CompanyController
from app.controllers.user_controller import UserController
from app.schemas.user_schemas import UserCreate, LoginRequest, UserResponse, LoginResponse
from app.schemas.question_schemas import QuestionCreate
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
    question_controller = UnifiedQuestionController()
    company_controller = CompanyController()
    user_controller = UserController()
    
    # Register routes
    @app.get("/")
    async def root():
        return {"message": config.title}
    
    # Company routes
    @app.get("/api/companies", response_model=list)
    async def get_companies():
        """Get all companies"""
        return company_controller.get_companies()
    
    # Metadata routes
    @app.get("/api/difficulties")
    async def get_difficulties():
        """Get all difficulty levels"""
        return question_controller.get_all_difficulties()
    
    @app.get("/api/time-periods")
    async def get_time_periods():
        """Get all time periods"""
        return question_controller.get_all_time_periods()
    
    @app.get("/api/topics")
    async def get_topics():
        """Get all unique topics"""
        return question_controller.get_all_topics()
    
    # Question routes
    @app.get("/api/questions")
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
        return question_controller.get_questions(
            companies=companies,
            company_logic=company_logic,
            difficulties=difficulties,
            time_periods=time_periods,
            time_period_logic=time_period_logic,
            topics=topics,
            search=search,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            authorization=authorization
        )
    
    @app.post("/api/questions")
    async def create_question(
        question_data: QuestionCreate,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Create a new question"""
        return question_controller.create_question(question_data, authorization)
    
    @app.get("/api/questions/{question_id}")
    async def get_question_details(
        question_id: int,
        authorization: Optional[str] = Header(None, convert_underscores=False)
    ):
        """Get detailed information about a specific question"""
        return question_controller.get_question_details(question_id, authorization)
    
    @app.put("/api/questions/{question_id}")
    async def update_question(
        question_id: int,
        question_data: QuestionCreate,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Update a question"""
        return question_controller.update_question(question_id, question_data, authorization)
    
    @app.delete("/api/questions/{question_id}")
    async def delete_question(
        question_id: int,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Delete a question"""
        return question_controller.delete_question(question_id, authorization)
    
    @app.get("/api/questions/user")
    async def get_user_questions(
        authorization: str = Header(..., convert_underscores=False),
        page: int = 1,
        per_page: int = 20
    ):
        """Get user's own questions"""
        return question_controller.get_user_questions(authorization, page, per_page)
    
    @app.post("/api/questions/{question_id}/request-public")
    async def request_public_approval(
        question_id: int,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Request public approval for a question"""
        return question_controller.request_public_approval(question_id, authorization)
    
    # Company association routes
    @app.post("/api/questions/{question_id}/companies")
    async def add_company_association(
        question_id: int,
        company_id: int,
        time_period: str,
        frequency: float = 1.0,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Add a company association to a question"""
        try:
            # For now, this is a simple implementation
            # In a full implementation, you'd want proper validation and user authorization
            from app.repositories.unified_question_repository import UnifiedQuestionRepository
            repo = UnifiedQuestionRepository()
            repo.add_company_association(question_id, company_id, time_period, frequency)
            return {"message": "Company association added successfully"}
        except Exception as e:
            logger.error(f"Error adding company association: {e}")
            raise HTTPException(status_code=500, detail="Failed to add company association")
    
    @app.delete("/api/questions/{question_id}/companies/{company_id}")
    async def remove_company_association(
        question_id: int,
        company_id: int,
        time_period: str,
        authorization: str = Header(..., convert_underscores=False)
    ):
        """Remove a company association from a question"""
        try:
            from app.repositories.unified_question_repository import UnifiedQuestionRepository
            repo = UnifiedQuestionRepository()
            repo.remove_company_association(question_id, company_id, time_period)
            return {"message": "Company association removed successfully"}
        except Exception as e:
            logger.error(f"Error removing company association: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove company association")
    
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
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Docker"""
        return {"status": "healthy", "message": "DevPrep Questions API is running"}
    
    return app


# Create the app instance
app = create_app()
