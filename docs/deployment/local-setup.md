# Local Development Setup

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **Git**
- **Docker & Docker Compose** (optional but recommended)

## Backend Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd civic-collaboration-platform
```

### 2. Backend Environment Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb civic_platform

# Or using psql:
psql -U postgres
CREATE DATABASE civic_platform;
\q
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Update database credentials, secret key, etc.
```

### 5. Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 6. Start Backend Server

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## Mobile App Setup

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Configure API Endpoint

Edit `src/constants/Config.ts`:

```typescript
// For Android Emulator
export const API_URL = "http://10.0.2.2:8000/api/v1";

// For iOS Simulator
export const API_URL = "http://localhost:8000/api/v1";

// For Physical Device (use your computer's IP)
export const API_URL = "http://192.168.1.XXX:8000/api/v1";
```

### 3. Start Development Server

```bash
npm start

# Then press:
# 'a' for Android
# 'i' for iOS
# 'w' for web
```

## Docker Setup (Recommended)

### 1. Start All Services

```bash
# From project root
docker-compose up --build

# Run in background
docker-compose up -d
```

### 2. Access Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### 3. View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f db
```

### 4. Stop Services

```bash
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Testing

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py
```

### Mobile Tests

```bash
cd mobile
npm test
```

## Common Issues

### Issue: Database Connection Error

**Solution**: Ensure PostgreSQL is running and credentials in `.env` are correct.

```bash
# Check PostgreSQL status
# On macOS:
brew services list

# On Linux:
sudo systemctl status postgresql

# On Windows:
# Check Services app
```

### Issue: Port Already in Use

**Solution**: Change the port or kill the process using it.

```bash
# Find process on port 8000
# On macOS/Linux:
lsof -i :8000

# On Windows:
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Module Import Errors

**Solution**: Ensure virtual environment is activated and dependencies are installed.

```bash
pip install -r requirements.txt
```

### Issue: Alembic Migration Errors

**Solution**: Reset migrations if in development.

```bash
# Drop all tables
alembic downgrade base

# Reapply migrations
alembic upgrade head
```

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Tests**
   ```bash
   pytest  # Backend
   npm test  # Mobile
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Useful Commands

### Backend

```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/

# Create new migration
alembic revision --autogenerate -m "description"
```

### Mobile

```bash
# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check

# Clear cache
expo start -c
```

## Next Steps

- Read the [API Documentation](../api/openapi.yaml)
- Review [Architecture](../architecture/system-design.md)
- Check [Database Schema](../architecture/database-schema.md)
- Explore example API calls in [Postman Collection](../api/postman-collection.json)
