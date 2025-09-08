# CodeQuest Company-wise Problems - Docker Deployment

This application provides a comprehensive platform for browsing CodeQuest problems organized by companies, with user authentication and advanced filtering capabilities.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- Ports 9000 and 9001 available

### Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   # 1. Navigate to project directory
cd /Users/jatinkaushik/Documents/codequest-company-wise-problems-main
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

3. **Access the application**
   - Frontend: http://localhost:9000
   - Backend API: http://localhost:9001
   - Health Check: http://localhost:9001/health

### Services

#### Frontend (Port 9000)
- React 18 with TypeScript
- Tailwind CSS for styling
- Nginx reverse proxy
- Automatically proxies API calls to backend

#### Backend (Port 9001)
- FastAPI with Python 3.11
- SQLite database
- JWT authentication
- Comprehensive question filtering

### Docker Configuration

#### Frontend Dockerfile
- Multi-stage build with Node.js 18
- Production optimized with Nginx
- Automatic API proxying to backend

#### Backend Dockerfile
- Python 3.11 slim base image
- Includes all required dependencies
- Health check endpoint
- Auto-reload in development

### Environment Variables

The application uses the following environment variables (configured in docker-compose.yml):

#### Backend
- `SECRET_KEY`: JWT signing key (change in production)
- `ALGORITHM`: JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (30 minutes)

### Development vs Production

#### Development Mode
```bash
# Frontend
cd frontend && npm run dev

# Backend  
cd backend && uvicorn app.main:app --reload
```

#### Production Mode (Docker)
```bash
docker-compose up -d --build
```

### Networking

- Both services run on a custom Docker network (`codequest-network`)
- Frontend communicates with backend through internal Docker networking
- External access only through exposed ports (9000, 9001)

### Data Persistence

- Backend data is stored in SQLite database
- Volume mapping ensures data persistence: `./backend/data:/app/data`

### Health Monitoring

- Backend includes health check endpoint: `/health`
- Docker health checks configured with 30s intervals
- Automatic container restart on failure

### API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:9001/docs
- ReDoc: http://localhost:9001/redoc

### Troubleshooting

#### Check service status
```bash
docker-compose ps
```

#### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs frontend
docker-compose logs backend
```

#### Restart services
```bash
docker-compose restart
```

#### Rebuild containers
```bash
docker-compose down
docker-compose up -d --build
```

### Security Notes

- Change the `SECRET_KEY` in production
- Consider using environment files for sensitive configuration
- The current setup is suitable for development/demo purposes
- For production, implement proper SSL/TLS termination

### Features

- **User Authentication**: JWT-based login/signup
- **Company Filtering**: Multi-select with AND/OR logic  
- **Difficulty Filtering**: Easy, Medium, Hard
- **Topic Filtering**: Data structures, algorithms, etc.
- **Time Period Filtering**: Recent questions, company-specific periods
- **Dark Mode**: Complete theme switching
- **Mobile Responsive**: Optimized for all screen sizes
- **Advanced Search**: Real-time question filtering
- **Pagination**: Efficient data loading

### Technology Stack

#### Frontend
- React 18 + TypeScript
- Tailwind CSS
- React Query (TanStack Query)
- React Router
- Axios
- React Select
- Lucide React (icons)

#### Backend
- FastAPI
- SQLite
- Pydantic
- JWT authentication
- bcrypt password hashing

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker: `docker-compose up --build`
5. Submit a pull request

---

🎯 **Access the app at http://localhost:9000 after running `docker-compose up -d --build`**
