# DevPrep Company-wise Problems Database

This project imports DevPrep company-wise problems data from CSV files into a SQLite database and provides tools to query the data.

## Database Schema

The database consists of three main tables:

1. **questions**: Stores unique DevPrep questions
   - id (Primary Key)
   - title (Unique)
   - difficulty (EASY/MEDIUM/HARD)
   - acceptance_rate
   - link (Unique DevPrep URL)
   - topics
   - created_at

2. **companies**: Stores company information
   - id (Primary Key)
   - name (Unique)
   - created_at

3. **company_questions**: Stores relationships between companies and questions
   - id (Primary Key)
   - company_id (Foreign Key)
   - question_id (Foreign Key)
   - time_period (30_days/3_months/6_months/more_than_6_months/all_time)
   - frequency
   - created_at

## Files

- `import_devprep_data.py`: Main import script that creates the database and imports all CSV data
- `query_devprep_data.py`: Interactive query tool to explore the imported data
- `devprep_problems.db`: SQLite database file (created after running import script)
- `import_log.txt`: Log file with detailed import information

## Usage

### 1. Import Data

First, run the import script to create the database and import all CSV files:

```bash
python3 import_devprep_data.py
```

This script will:
- Create a SQLite database (`devprep_problems.db`)
- Scan all company folders in the `Q/` directory
- Import questions from CSV files (handles duplicates automatically)
- Create relationships between companies and questions with time periods
- Generate detailed logs

### 2. Query Data

After importing, use the query tool to explore the data:

```bash
python3 query_devprep_data.py
```

The query tool provides an interactive menu with options to:
- View database summary and statistics
- List all companies
- Get questions for a specific company and time period
- Search questions by title or topic
- Find which companies ask a specific question
- View most frequently asked questions
- Filter questions by difficulty level

## Time Periods

The CSV files are categorized by time periods:
- `1. Thirty Days.csv` → `30_days`
- `2. Three Months.csv` → `3_months`
- `3. Six Months.csv` → `6_months`
- `4. More Than Six Months.csv` → `more_than_6_months`
- `5. All.csv` → `all_time`

## Example Queries

### Find questions asked by Google in the last 30 days:
```sql
SELECT q.title, q.difficulty, cq.frequency
FROM questions q
JOIN company_questions cq ON q.id = cq.question_id
JOIN companies c ON cq.company_id = c.id
WHERE c.name = 'Google' AND cq.time_period = '30_days'
ORDER BY cq.frequency DESC;
```

### Find which companies ask "Two Sum":
```sql
SELECT c.name, cq.time_period, cq.frequency
FROM companies c
JOIN company_questions cq ON c.id = cq.company_id
JOIN questions q ON cq.question_id = q.id
WHERE q.title = 'Two Sum'
ORDER BY cq.frequency DESC;
```

### Most popular questions across all companies:
```sql
SELECT q.title, COUNT(*) as company_count, AVG(cq.frequency) as avg_frequency
FROM questions q
JOIN company_questions cq ON q.id = cq.question_id
GROUP BY q.id
ORDER BY company_count DESC, avg_frequency DESC
LIMIT 20;
```

## Features

### Duplicate Handling
- Questions are identified by title and DevPrep URL
- If a question already exists, only the company-question relationship is added
- No duplicate questions are stored

### Data Integrity
- Foreign key constraints ensure data consistency
- Indexes on key columns for better performance
- Transaction-based imports to prevent partial data corruption

### Logging
- Detailed logging of import process
- Error handling with continued processing
- Statistics and summary information

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)
- SQLite3 (included with Python)

## Troubleshooting

### Import Issues
- Check that the `Q/` directory exists and contains company folders
- Verify CSV files have the correct format with headers: `Difficulty,Title,Frequency,Acceptance Rate,Link,Topics`
- Check the `import_log.txt` file for detailed error information

### Database Issues
- If the database becomes corrupted, delete `devprep_problems.db` and re-run the import
- For partial imports, the script can be run multiple times safely (duplicates are handled)

### Performance
- The import process may take several minutes depending on the number of companies and questions
- Database operations are optimized with indexes and batch commits
