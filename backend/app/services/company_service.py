"""
Company service for business logic
"""
from typing import List
from app.services.base_service import BaseService
from app.repositories.company_repository import CompanyRepository
from app.schemas.question_schemas import Company


class CompanyService(BaseService):
    """Service for company-related business logic"""
    
    def __init__(self):
        super().__init__()
        self.company_repo = CompanyRepository()
    
    def get_all_companies(self) -> List[Company]:
        """Get all companies"""
        companies_data = self.company_repo.find_all()
        return [Company(**company) for company in companies_data]
    
    def get_company_by_id(self, company_id: int) -> Company:
        """Get company by ID"""
        company_data = self.company_repo.find_by_id(company_id)
        if not company_data:
            raise ValueError(f"Company with ID {company_id} not found")
        return Company(**company_data)
    
    def get_company_by_name(self, name: str) -> Company:
        """Get company by name"""
        company_data = self.company_repo.find_by_name(name)
        if not company_data:
            raise ValueError(f"Company with name {name} not found")
        return Company(**company_data)
