# System Architecture

## Overview

The Civic Collaboration Platform follows a modern, microservices-inspired architecture with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │   Mobile App     │              │  Admin Dashboard │         │
│  │  (React Native)  │              │     (React)      │         │
│  └────────┬─────────┘              └────────┬─────────┘         │
│           │                                  │                   │
└───────────┼──────────────────────────────────┼───────────────────┘
            │                                  │
            │         HTTP/REST API            │
            └──────────────┬───────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                   Application Layer                              │
├──────────────────────────┼───────────────────────────────────────┤
│                          │                                        │
│              ┌───────────▼──────────┐                            │
│              │   FastAPI Backend    │                            │
│              │                      │                            │
│              │  ┌────────────────┐  │                            │
│              │  │  API Routes    │  │                            │
│              │  │  (v1)          │  │                            │
│              │  └────────┬───────┘  │                            │
│              │           │          │                            │
│              │  ┌────────▼───────┐  │                            │
│              │  │  Services      │  │                            │
│              │  │  - Auth        │  │                            │
│              │  │  - Problems    │  │                            │
│              │  │  - Solutions   │  │                            │
│              │  └────────┬───────┘  │                            │
│              │           │          │                            │
│              │  ┌────────▼───────┐  │                            │
│              │  │  Repositories  │  │                            │
│              │  │  (Data Access) │  │                            │
│              │  └────────┬───────┘  │                            │
│              └───────────┼──────────┘                            │
│                          │                                        │
└──────────────────────────┼────────────────────────────────────────┘
                           │
┌──────────────────────────┼────────────────────────────────────────┐
│                    AI/ML Layer                                    │
├──────────────────────────┼────────────────────────────────────────┤
│                          │                                        │
│              ┌───────────▼──────────┐                            │
│              │   AI Pipeline        │                            │
│              │                      │                            │
│              │  ┌────────────────┐  │                            │
│              │  │ Preprocessor   │  │                            │
│              │  └────────┬───────┘  │                            │
│              │           │          │                            │
│              │  ┌────────▼───────┐  │                            │
│              │  │ Embeddings     │  │                            │
│              │  │ (Transformers) │  │                            │
│              │  └────────┬───────┘  │                            │
│              │           │          │                            │
│              │  ┌────────▼───────┐  │                            │
│              │  │ Clustering     │  │                            │
│              │  │ (DBSCAN)       │  │                            │
│              │  └────────┬───────┘  │                            │
│              │           │          │                            │
│              │  ┌────────▼───────┐  │                            │
│              │  │ Ranking        │  │                            │
│              │  │ Algorithm      │  │                            │
│              │  └────────────────┘  │                            │
│              └─────────────────────┘                            │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼────────────────────────────────────────┐
│                    Data Layer                                     │
├──────────────────────────┼────────────────────────────────────────┤
│                          │                                        │
│              ┌───────────▼──────────┐                            │
│              │   PostgreSQL         │                            │
│              │                      │                            │
│              │  - Users             │                            │
│              │  - Problems          │                            │
│              │  - Solutions         │                            │
│              │  - Votes             │                            │
│              │  - Comments          │                            │
│              └──────────────────────┘                            │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Mobile App (React Native)
- User authentication and session management
- Problem submission with geolocation and images
- Solution browsing and voting
- Real-time notifications
- Offline-first architecture

### Admin Dashboard (React)
- Government official interface
- AI-processed insights visualization
- Problem status management
- Analytics and reporting
- Export functionality

### FastAPI Backend
- RESTful API endpoints
- JWT-based authentication
- Request validation
- Business logic orchestration
- Database operations
- Background task management

### AI Pipeline
- **Preprocessor**: Text cleaning, normalization, stopword removal
- **Embeddings**: Semantic vector generation using SentenceTransformers
- **Clustering**: Duplicate/similar solution detection using DBSCAN
- **Ranking**: Multi-factor scoring algorithm

### PostgreSQL Database
- Relational data storage
- ACID compliance
- PostGIS support for geospatial queries
- Full-text search capabilities

## Data Flow

### Problem Submission Flow
1. Citizen submits problem via mobile app
2. Backend validates and stores in database
3. Returns confirmation to user
4. Triggers background AI analysis (optional)

### Solution Analysis Flow
1. Citizen proposes solution
2. Backend stores solution
3. AI pipeline processes:
   - Text preprocessing
   - Embedding generation
   - Clustering with existing solutions
   - Score calculation
4. Updated rankings stored in database
5. Results available via API

## Security Architecture

### Authentication
- JWT tokens with configurable expiration
- Password hashing using bcrypt
- Refresh token support (future enhancement)

### Authorization
- Role-Based Access Control (RBAC)
- Three roles: Citizen, Government, Admin
- Endpoint-level permission checks

### Data Protection
- HTTPS/TLS in production
- SQL injection prevention via ORM
- Input validation with Pydantic
- CORS configuration
- Rate limiting (recommended for production)

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Async I/O for concurrent requests

### Caching Strategy (Future)
- Redis for session storage
- API response caching
- AI embedding caching

### Database Optimization
- Indexed columns for frequent queries
- Async database operations
- Connection pooling

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Mobile | React Native + Expo | Cross-platform mobile app |
| Frontend | React + Material UI | Admin dashboard |
| Backend | FastAPI + Python 3.11 | REST API server |
| Database | PostgreSQL 15 | Primary data store |
| AI/ML | SentenceTransformers, scikit-learn | NLP and clustering |
| Deployment | Docker + Docker Compose | Containerization |
| API Docs | OpenAPI/Swagger | Auto-generated docs |

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│            Load Balancer / CDN              │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐   ┌───▼────┐   ┌───▼────┐
│ API    │   │ API    │   │ API    │
│ Server │   │ Server │   │ Server │
│ (1)    │   │ (2)    │   │ (N)    │
└───┬────┘   └───┬────┘   └───┬────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │   PostgreSQL   │
         │   (Primary)    │
         └────────────────┘
```

## Future Enhancements

1. **Microservices Split**: Separate AI pipeline into independent service
2. **Message Queue**: RabbitMQ/Kafka for async processing
3. **Caching Layer**: Redis for performance
4. **CDN Integration**: Static asset delivery
5. **Real-time Features**: WebSocket support for live updates
6. **Search Engine**: Elasticsearch for advanced search
7. **Monitoring**: Prometheus + Grafana
8. **Logging**: ELK stack integration
