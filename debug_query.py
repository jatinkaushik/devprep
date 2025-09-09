#!/usr/bin/env python3

import sqlite3
import sys

# Connect to the database
conn = sqlite3.connect('/Users/jatinkaushik/Documents/devprep/backend/devprep_problems.db')
conn.row_factory = sqlite3.Row  # This enables dict-like access

cursor = conn.cursor()

# Test the exact query that's causing issues
query = """
SELECT 
    1000000 + uq.id as id,
    uq.title,
    uq.difficulty,
    NULL as acceptance_rate,
    COALESCE(uq.link, '#') as link,
    uq.topics,
    uq.created_at,
    uq.description,
    uq.created_by as added_by,
    uq.is_approved,
    uq.is_public,
    0 as max_frequency
FROM user_questions uq
WHERE uq.is_public = 1 AND uq.is_approved = 1
ORDER BY uq.created_at DESC
LIMIT 1
"""

cursor.execute(query)
result = cursor.fetchone()

if result:
    # Convert to dict
    result_dict = dict(result)
    
    # Convert boolean fields
    result_dict['is_approved'] = bool(result_dict['is_approved'])
    result_dict['is_public'] = bool(result_dict['is_public'])
    
    print("Fixed result dict:")
    for key, value in result_dict.items():
        print(f"  {key}: {value!r} (type: {type(value)})")
    
    print(f"\nAll keys: {list(result_dict.keys())}")
    print(f"'added_by' in result: {'added_by' in result_dict}")
    print(f"added_by value: {result_dict.get('added_by')}")
else:
    print("No results found")

conn.close()
