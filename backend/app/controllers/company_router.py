from fastapi import APIRouter, HTTPException
from app.services.company_service import CompanyService

router = APIRouter(prefix="/api/companies", tags=["companies"])
company_service = CompanyService()

@router.get("/")
async def get_companies():
    """Get all companies"""
    try:
        return company_service.get_all_companies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
