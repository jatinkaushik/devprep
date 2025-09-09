#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/jatinkaushik/Documents/devprep/backend')

from app.services.question_service import QuestionService
from app.schemas.question_schemas import QuestionFilters

# Create service instance
service = QuestionService()

# Create simple filters
filters = QuestionFilters(
    page=1,
    per_page=1
)

try:
    print("Testing service layer...")
    
    # Call the service method (this should trigger the error)
    result = service.get_filtered_questions(filters, user_id=None)
    
    print(f"Success! Got {len(result.questions)} questions")
    
except Exception as e:
    print(f"Error in service: {e}")
    import traceback
    traceback.print_exc()
    
    # Let's try to call the repository methods directly to see the difference
    print("\n" + "="*50)
    print("Testing repository layer directly...")
    
    from app.repositories.question_repository import QuestionRepository
    repo = QuestionRepository()
    
    try:
        # Get regular questions
        regular_questions, regular_total = repo.get_filtered_questions(filters, user_id=None)
        print(f"Regular questions: {len(regular_questions)}, total: {regular_total}")
        
        # Get user questions
        user_questions, user_total = repo.get_user_questions_for_display(filters, user_id=None)
        print(f"User questions: {len(user_questions)}, total: {user_total}")
        
        # Combine them like the service does
        all_questions = regular_questions + user_questions
        print(f"\nCombined questions: {len(all_questions)}")
        
        for i, q in enumerate(all_questions):
            print(f"\nQuestion {i+1}:")
            print(f"  ID: {q.get('id')}")
            print(f"  Title: {q.get('title')}")
            print(f"  Difficulty: {q.get('difficulty')}")
            print(f"  Keys: {list(q.keys())}")
            print(f"  Has added_by: {'added_by' in q}")
            if 'added_by' in q:
                print(f"  added_by value: {q['added_by']}")
                
            # Try Pydantic validation on this specific question
            from app.schemas.question_schemas import Question
            try:
                question_obj = Question(**q)
                print(f"  ✓ Pydantic validation successful")
            except Exception as ve:
                print(f"  ✗ Pydantic validation failed: {ve}")
                
    except Exception as re:
        print(f"Repository error: {re}")
        import traceback
        traceback.print_exc()
