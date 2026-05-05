# Backend README

## Overview

FastAPI-based backend for the Civic Collaboration Platform, providing RESTful APIs for problem reporting, solution management, and AI-powered analysis.

## Features

- 🔐 JWT Authentication with RBAC
- 📊 RESTful API with OpenAPI documentation
- 🤖 AI-powered solution ranking
- 🗄️ PostgreSQL with async SQLAlchemy
- 🔄 Database migrations with Alembic
- 📝 Comprehensive logging
- ✅ Input validation with Pydantic
- 🧪 Test coverage with pytest

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── ai/              # AI/ML pipeline
│   ├── api/             # API endpoints
│   │   └── v1/          # API version 1
│   ├── core/            # Core functionality
│   │   ├── security.py  # Auth & security
│   │   ├── deps.py      # Dependencies
│   │   ├── exceptions.py # Custom exceptions
│   │   └── middleware.py # Middleware
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # Application entry
├── alembic/             # Database migrations
├── tests/               # Test suite
├── logs/                # Application logs
└── requirements.txt     # Dependencies
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/users/signup` - User registration

### Users
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/` - List users (admin only)

### Problems
- `GET /api/v1/problems/` - List problems
- `POST /api/v1/problems/` - Create problem
- `GET /api/v1/problems/{id}` - Get problem
- `PUT /api/v1/problems/{id}` - Update problem

### Solutions
- `POST /api/v1/solutions/` - Propose solution
- `GET /api/v1/solutions/problem/{id}` - Get solutions for problem

## Configuration

Environment variables (`.env`):

```env
SECRET_KEY=your-secret-key
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=civic_platform
```

## Development

### Running Tests

```bash
pytest
pytest --cov=app
pytest -v tests/test_auth.py
```

### Code Quality

```bash
# Format
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## AI Pipeline

The AI system processes solutions through multiple stages:

1. **Text Preprocessing**: Cleans and normalizes text
2. **Embedding Generation**: Creates semantic vectors using SentenceTransformers
3. **Clustering**: Groups similar solutions using DBSCAN
4. **Ranking**: Scores solutions based on multiple factors

### Ranking Algorithm

Solutions are scored using weighted criteria:

- **Votes** (40%): Public support
- **Feasibility** (30%): Implementation viability
- **Impact** (20%): Expected benefit
- **Cost Efficiency** (10%): Resource optimization

## Deployment

### Docker

```bash
docker build -t civic-backend .
docker run -p 8000:8000 civic-backend
```

### Docker Compose

```bash
docker-compose up -d
```

## Security

- Password hashing with bcrypt
- JWT tokens with configurable expiration
- CORS protection
- SQL injection prevention via ORM
- Input validation
- Rate limiting (recommended for production)

## Performance

- Async I/O with asyncio
- Database connection pooling
- Efficient query optimization
- Caching strategies (future)

## Monitoring

Logs are written to:
- Console (development)
- `logs/app.log` (production)

Log rotation is configured with 10MB max size and 5 backup files.

## Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Run test suite
5. Submit pull request

## License

MIT License - see LICENSE file
