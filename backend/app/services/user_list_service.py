"""
User list service for business logic
"""
from typing import List, Dict, Any
from fastapi import HTTPException
from app.services.base_service import BaseService
from app.repositories.user_list_repository import UserListRepository
from app.schemas.user_list_schemas import (
    UserListCreate, UserListResponse, ListItemCreate, 
    ListItemResponse, ListItemUpdate, QuickAddRequest, UserListsResponse
)
from app.models.user_models import ListType


class UserListService(BaseService):
    """Service for user list operations"""
    
    def __init__(self):
        super().__init__()
        self.user_list_repo = UserListRepository()
    
    def get_user_lists(self, user_id: int) -> UserListsResponse:
        """Get all lists for a user"""
        try:
            lists_data = self.user_list_repo.get_user_lists(user_id)
            lists = [UserListResponse(**list_data) for list_data in lists_data]
            return UserListsResponse(lists=lists)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user lists: {str(e)}")
    
    def create_user_list(self, user_id: int, list_data: UserListCreate) -> UserListResponse:
        """Create a new user list"""
        try:
            # Validate list_type
            if list_data.list_type not in ['custom']:
                raise HTTPException(status_code=400, detail="Only custom lists can be created")
            
            created_list = self.user_list_repo.create_user_list(
                user_id=user_id,
                name=list_data.name,
                list_type=list_data.list_type,
                description=list_data.description
            )
            return UserListResponse(**created_list)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=400, detail="List name already exists")
            raise HTTPException(status_code=500, detail=f"Error creating list: {str(e)}")
    
    def delete_user_list(self, list_id: int, user_id: int) -> Dict[str, str]:
        """Delete a user list"""
        try:
            success = self.user_list_repo.delete_user_list(list_id, user_id)
            if not success:
                raise HTTPException(status_code=404, detail="List not found or cannot be deleted")
            return {"message": "List deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting list: {str(e)}")
    
    def add_item_to_list(self, list_id: int, item_data: ListItemCreate) -> ListItemResponse:
        """Add an item to a list"""
        try:
            if not item_data.question_id and not item_data.user_question_id:
                raise HTTPException(status_code=400, detail="Either question_id or user_question_id is required")
            
            result = self.user_list_repo.add_item_to_list(
                list_id=list_id,
                question_id=item_data.question_id,
                user_question_id=item_data.user_question_id,
                status=item_data.status,
                notes=item_data.notes
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return ListItemResponse(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding item to list: {str(e)}")
    
    def remove_item_from_list(self, list_id: int, question_id: int = None, user_question_id: int = None) -> Dict[str, str]:
        """Remove an item from a list"""
        try:
            success = self.user_list_repo.remove_item_from_list(list_id, question_id, user_question_id)
            if not success:
                raise HTTPException(status_code=404, detail="Item not found in list")
            return {"message": "Item removed from list"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error removing item from list: {str(e)}")
    
    def get_list_items(self, list_id: int, user_id: int) -> List[ListItemResponse]:
        """Get all items in a list"""
        try:
            # Verify list belongs to user
            list_data = self.user_list_repo.get_user_list_by_id(list_id)
            if not list_data or list_data['user_id'] != user_id:
                raise HTTPException(status_code=404, detail="List not found")
            
            items_data = self.user_list_repo.get_list_items(list_id)
            return [ListItemResponse(**item_data) for item_data in items_data]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving list items: {str(e)}")
    
    def update_item_status(self, item_id: int, user_id: int, update_data: ListItemUpdate) -> ListItemResponse:
        """Update a list item"""
        try:
            # Get item and verify ownership
            item = self.user_list_repo.get_list_item_by_id(item_id)
            if not item:
                raise HTTPException(status_code=404, detail="List item not found")
            
            # Verify list belongs to user
            list_data = self.user_list_repo.get_user_list_by_id(item['list_id'])
            if not list_data or list_data['user_id'] != user_id:
                raise HTTPException(status_code=404, detail="List not found")
            
            success = self.user_list_repo.update_item_status(
                item_id=item_id,
                status=update_data.status or item['status'],
                notes=update_data.notes
            )
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to update item")
            
            updated_item = self.user_list_repo.get_list_item_by_id(item_id)
            return ListItemResponse(**updated_item)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating list item: {str(e)}")
    
    def quick_add_to_default_list(self, user_id: int, quick_add_data: QuickAddRequest) -> Dict[str, str]:
        """Quickly add item to default lists (favorites, todo, solved)"""
        try:
            # Get user's default lists
            default_lists = self.user_list_repo.get_user_default_lists(user_id)
            
            if quick_add_data.list_type not in default_lists:
                raise HTTPException(status_code=400, detail=f"Default {quick_add_data.list_type} list not found")
            
            list_id = default_lists[quick_add_data.list_type]
            
            # Determine status based on list type
            status = "solved" if quick_add_data.list_type == "solved" else "not_attempted"
            
            result = self.user_list_repo.add_item_to_list(
                list_id=list_id,
                question_id=quick_add_data.question_id,
                user_question_id=quick_add_data.user_question_id,
                status=status
            )
            
            if "error" in result:
                if "already exists" in result["error"]:
                    return {"message": f"Item already in {quick_add_data.list_type}"}
                raise HTTPException(status_code=400, detail=result["error"])
            
            return {"message": f"Added to {quick_add_data.list_type}"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding to {quick_add_data.list_type}: {str(e)}")
    
    def remove_from_default_list(self, user_id: int, list_type: str, question_id: int = None, user_question_id: int = None) -> Dict[str, str]:
        """Remove item from default list"""
        try:
            default_lists = self.user_list_repo.get_user_default_lists(user_id)
            
            if list_type not in default_lists:
                raise HTTPException(status_code=400, detail=f"Default {list_type} list not found")
            
            list_id = default_lists[list_type]
            success = self.user_list_repo.remove_item_from_list(list_id, question_id, user_question_id)
            
            if not success:
                return {"message": f"Item not in {list_type}"}
            
            return {"message": f"Removed from {list_type}"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error removing from {list_type}: {str(e)}")
