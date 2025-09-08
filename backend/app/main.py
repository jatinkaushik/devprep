"""
FastAPI application with class-based architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import config
from app.controllers.question_controller import QuestionController
from app.controllers.company_controller import CompanyController
from app.controllers.user_controller import UserController
from app.schemas.user_schemas import UserCreate, LoginRequest, UserResponse, LoginResponse


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=config.title,
        version=config.version,
        description=config.description
    )
    
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
        sort_order: str = "desc"
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
            sort_order=sort_order
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
    async def get_profile():
        """Get current user profile"""
        return user_controller.get_profile()
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Docker"""
        return {"status": "healthy", "message": "DevPrep Questions API is running"}
    
    return app


# Create the app instance
app = create_app()
