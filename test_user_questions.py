#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/jatinkaushik/Documents/devprep/backend')

from app.repositories.question_repository import QuestionRepository
from app.schemas.question_schemas import QuestionFilters

# Create repository instance
repo = QuestionRepository()

# Create simple filters
filters = QuestionFilters(
    page=1,
    per_page=1
)

try:
    # Call the method that's failing
    user_questions, total = repo.get_user_questions_for_display(filters, user_id=None)
    
    print(f"Found {len(user_questions)} user questions, total: {total}")
    
    if user_questions:
        print("\nFirst user question:")
        for key, value in user_questions[0].items():
            print(f"  {key}: {value!r}")
            
        print(f"\nKeys in result: {list(user_questions[0].keys())}")
        print(f"'added_by' in result: {'added_by' in user_questions[0]}")
        
        # Test Pydantic validation
        from app.schemas.question_schemas import Question
        try:
            question_obj = Question(**user_questions[0])
            print(f"\nPydantic validation successful: {question_obj}")
        except Exception as e:
            print(f"\nPydantic validation failed: {e}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
