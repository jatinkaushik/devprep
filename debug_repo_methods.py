#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/jatinkaushik/Documents/devprep/backend')

from app.repositories.question_repository import QuestionRepository
from app.schemas.question_schemas import QuestionFilters

# Create repository instance
repo = QuestionRepository()

# Create filters that match the failing API call
filters = QuestionFilters(
    page=1,
    per_page=1,
    sort_by="frequency", 
    sort_order="desc"
)

print("Testing the exact methods called by the service:")

try:
    # Call get_filtered_questions (regular questions)
    print("\n1. Testing get_filtered_questions (regular questions)...")
    regular_questions, regular_total = repo.get_filtered_questions(filters, user_id=None)
    print(f"   Regular questions: {len(regular_questions)}, total: {regular_total}")
    
    if regular_questions:
        q = regular_questions[0]
        print(f"   First regular question ID: {q.get('id')}")
        print(f"   Has added_by: {'added_by' in q}")
        print(f"   All fields: {list(q.keys())}")
    
    # Call get_user_questions_for_display (user questions)  
    print("\n2. Testing get_user_questions_for_display (user questions)...")
    user_questions, user_total = repo.get_user_questions_for_display(filters, user_id=None)
    print(f"   User questions: {len(user_questions)}, total: {user_total}")
    
    if user_questions:
        q = user_questions[0]
        print(f"   First user question ID: {q.get('id')}")
        print(f"   Has added_by: {'added_by' in q}")
        print(f"   All fields: {list(q.keys())}")
        
        # Try Pydantic validation
        from app.schemas.question_schemas import Question
        try:
            question_obj = Question(**q)
            print(f"   ✓ Pydantic validation successful")
        except Exception as ve:
            print(f"   ✗ Pydantic validation failed: {ve}")
    
    # Combine them like the service does
    print("\n3. Testing combined list...")
    all_questions = regular_questions + user_questions
    print(f"   Combined: {len(all_questions)} questions")
    
    # Test each combined question
    for i, q in enumerate(all_questions):
        print(f"\n   Question {i+1}: ID {q.get('id')}")
        print(f"     Has added_by: {'added_by' in q}")
        if 'added_by' in q:
            print(f"     added_by value: {q['added_by']}")
        
        try:
            question_obj = Question(**q)
            print(f"     ✓ Pydantic validation successful")
        except Exception as ve:
            print(f"     ✗ Pydantic validation failed: {ve}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
