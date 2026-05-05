# Civic Collaboration Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React Native](https://img.shields.io/badge/React%20Native-0.73-blue.svg)](https://reactnative.dev/)

## 🌟 Overview

A production-ready, AI-powered civic engagement platform that transforms citizen-reported problems into actionable, government-ready solutions. Built with modern technologies and designed to scale nationally.

### Key Features

- 🎯 **Smart Problem Reporting**: Geo-tagged civic issues with image support
- 🤖 **AI-Powered Analysis**: Automated solution clustering and ranking
- 📊 **Government Dashboard**: Decision-ready insights and analytics
- 📱 **Mobile-First**: Native iOS & Android experience
- 🔐 **Enterprise Security**: JWT authentication with RBAC
- 🚀 **Production Ready**: Dockerized, scalable architecture

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Mobile App     │────▶│   FastAPI        │────▶│   PostgreSQL    │
│  (React Native) │     │   Backend        │     │   Database      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  AI Pipeline │
                        │  - NLP       │
                        │  - Clustering│
                        │  - Ranking   │
                        └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for mobile development)
- Python 3.11+ (for local backend development)

### Running with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd civic-collaboration-platform

# Start all services
docker-compose up --build

# API will be available at http://localhost:8000
# API Documentation at http://localhost:8000/docs
```

### Backend Development Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Mobile App Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo development server
npm start

# Press 'a' for Android or 'i' for iOS
```

## 📁 Project Structure

```
civic-collaboration-platform/
├── backend/                 # Python FastAPI Backend
│   ├── app/
│   │   ├── ai/             # AI/ML Pipeline
│   │   ├── api/            # REST API Endpoints
│   │   ├── core/           # Security & Config
│   │   ├── models/         # SQLAlchemy Models
│   │   └── schemas/        # Pydantic Schemas
│   ├── alembic/            # Database Migrations
│   └── tests/              # Backend Tests
├── mobile/                 # React Native App
│   ├── src/
│   │   ├── screens/        # App Screens
│   │   ├── navigation/     # Navigation Config
│   │   ├── store/          # Redux Store
│   │   └── api/            # API Client
├── admin-dashboard/        # Government Admin Portal
├── infrastructure/         # Deployment Configs
└── docs/                   # Documentation

```

## 🤖 AI Pipeline

The platform uses a sophisticated AI pipeline:

1. **Text Preprocessing**: Cleans and normalizes user input
2. **Semantic Embeddings**: Uses SentenceTransformers for vector representation
3. **Clustering**: DBSCAN algorithm groups similar solutions
4. **Ranking Algorithm**: Weighted scoring based on:
   - Public votes (40%)
   - Feasibility score (30%)
   - Impact assessment (20%)
   - Cost efficiency (10%)

## 🔐 Security

- JWT-based authentication
- Role-Based Access Control (Citizen, Government, Admin)
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Mobile tests
cd mobile
npm test
```

## 🚢 Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Key environment variables (see `.env.example`):

- `SECRET_KEY`: JWT secret key
- `POSTGRES_*`: Database credentials
- `OPENAI_API_KEY`: Optional, for advanced AI features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📧 Support

For issues and questions, please open a GitHub issue or contact the development team.

---

**Built with ❤️ for civic engagement and democratic participation**
