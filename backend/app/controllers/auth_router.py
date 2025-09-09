from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from app.services.user_service import UserService
from app.schemas.user_schemas import LoginRequest, LoginResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
user_service = UserService()

@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """User login"""
    try:
        result = user_service.authenticate_user(login_request)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return result
    except Exception as e:
        # add tracback for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """User registration"""
    try:
        result = user_service.create_user(user_data.dict())
        return result
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
