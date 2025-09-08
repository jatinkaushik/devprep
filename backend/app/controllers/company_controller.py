"""
Company controller for API endpoints
"""
from typing import List
from app.controllers.base_controller import BaseController
from app.services.company_service import CompanyService
from app.schemas.question_schemas import Company


class CompanyController(BaseController):
    """Controller for company-related API endpoints"""
    
    def __init__(self):
        super().__init__()
        self.company_service = CompanyService()
    
    def get_companies(self) -> List[Company]:
        """Get all companies"""
        try:
            return self.company_service.get_all_companies()
        except Exception as e:
            self.handle_error(e, "Error retrieving companies")
