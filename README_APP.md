# CodeQuest Questions Browser

A modern web application to browse and filter CodeQuest questions by company, difficulty, time period, and topics.

## ✨ Features

- **🏢 Company Filter**: Browse questions asked by specific companies
- **📊 Difficulty Levels**: Filter by Easy, Medium, Hard difficulty
- **⏰ Time Periods**: Filter by when questions were asked (30 days, 3 months, 6 months, etc.)
- **🏷️ Topics**: Filter by algorithm/data structure topics
- **🔍 Search**: Search questions by title
- **📱 Responsive Design**: Works great on desktop and mobile
- **⚡ Fast & Modern**: Built with React, TypeScript, and FastAPI
- **📈 Statistics**: View difficulty distribution and company stats

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm

### Setup & Run

1. **Clone and navigate to the project:**
   ```bash
   cd codequest-company-wise-problems-main
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the application:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Manual Setup

If you prefer to set up manually:

### Backend Setup

```bash
# Install Python dependencies
pip3 install fastapi uvicorn[standard] pydantic python-multipart jinja2 aiofiles

# Make sure your database is ready
python3 import_codequest_data.py

# Start backend server
python3 backend/main.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📖 Usage Guide

### 🔍 Filtering Questions

1. **Company Filter**: Select one or more companies to see their questions
2. **Difficulty Filter**: Choose Easy, Medium, or Hard difficulty levels
3. **Time Period Filter**: Filter by when questions were recently asked
4. **Topics Filter**: Select specific algorithm/data structure topics
5. **Search**: Type to search question titles

### 📊 Understanding the Data

- **Frequency**: How often a question appears (higher = more common)
- **Time Period**: When the question was asked:
  - 30 Days: Recently asked
  - 3 Months: Asked in last quarter
  - 6 Months: Asked in last half year
  - More than 6 Months: Older questions
  - All Time: Historical data

### 🎯 Tips for Best Results

- Use multiple filters to narrow down questions
- Sort by frequency to see most commonly asked questions
- Check time periods to focus on recent interview questions
- Click on question titles to go directly to CodeQuest

## 🏛️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.8+
- **Database**: SQLite3 with optimized queries
- **API**: RESTful API with automatic documentation
- **Features**: CORS enabled, pagination, filtering, sorting

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS for modern, responsive design
- **State Management**: React Query for server state
- **UI Components**: Custom components with Lucide icons
- **Features**: Real-time search, filter persistence, responsive design

### Database Schema
- **questions**: Unique CodeQuest questions with metadata
- **companies**: Company information
- **company_questions**: Relationships with frequency and time data

## 🛠️ Development

### Project Structure
```
├── backend/
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── types.ts           # TypeScript types
│   │   └── utils/             # Utility functions
│   ├── package.json
│   └── vite.config.ts
├── import_codequest_data.py     # Database import script
├── query_codequest_data.py      # Database query tool
├── codequest_problems.db        # SQLite database
├── setup.sh                   # Setup script
└── start.sh                   # Start script
```

### API Endpoints

- `GET /api/companies` - Get all companies
- `GET /api/difficulties` - Get difficulty levels
- `GET /api/time-periods` - Get time periods
- `GET /api/topics` - Get all topics
- `GET /api/questions` - Get filtered questions (with pagination)
- `GET /api/stats` - Get overall statistics

### Adding New Features

1. **Backend**: Add new endpoints in `backend/main.py`
2. **Frontend**: Add new components in `frontend/src/components/`
3. **Types**: Update TypeScript types in `frontend/src/types.ts`

## 🔧 Configuration

### Backend Configuration
- Default port: 8000
- Database: `codequest_problems.db`
- CORS enabled for localhost:3000 and localhost:5173

### Frontend Configuration
- Default port: 3000
- API proxy configured for backend
- Tailwind CSS for styling

## 📊 Database Information

- **1,923** unique coding questions
- **470** companies
- **18,668** company-question relationships
- Covers difficulty levels: Easy, Medium, Hard
- Time periods from 30 days to all-time data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Coding questions and company data belong to their respective owners.

## 🆘 Troubleshooting

### Common Issues

1. **Database not found**: Run `python3 import_devpreps_data.py`
2. **Port already in use**: Change ports in configuration files
3. **Dependencies missing**: Run the setup script again
4. **Frontend won't start**: Check Node.js version (16+ required)

### Getting Help

1. Check the logs in terminal
2. Verify all dependencies are installed
3. Ensure database file exists
4. Check that both frontend and backend ports are available

---

**Happy coding! 🚀** Use this tool to ace your next technical interview!
