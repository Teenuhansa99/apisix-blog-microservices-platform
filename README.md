# Blog API MVP - Production-Ready APISIX Microservices System

A production-ready blog API system with microservices architecture using Apache APISIX gateway, PostgreSQL database, SQLAlchemy ORM, and JWT authentication with refresh tokens.

## Architecture

```
                        APISIX Gateway (Port 9080)
                        
  /auth/*     -> Auth Service (Flask:5001) - PostgreSQL
  /posts/*    -> Blog Service (Flask:5000) - PostgreSQL
  
                        Services:
  PostgreSQL    - Persistent database (Port 5432)
  etcd          - Configuration store (Port 2379)
  APISIX        - API Gateway (Port 9080, 9180)
```

## Features

- PostgreSQL database with SQLAlchemy ORM
- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Email validation
- Comprehensive error handling
- Structured logging
- Health check endpoints
- Pagination support for posts
- Environment variables (.env) configuration

## Quick Start

### Windows (PowerShell)

```
docker compose up -d
.\setup-routes.bat
docker ps
```

### macOS/Linux

```
cp .env.example .env
docker compose up -d
./scripts/create_route.sh
./scripts/create_auth_route.sh
docker ps
```

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| /auth/register | POST | Register new user |
| /auth/login | POST | Login & get tokens |
| /auth/refresh | POST | Refresh access token |
| /auth/logout | POST | Revoke refresh token |

### Blog Posts

| Endpoint | Method | Description |
|----------|--------|-------------|
| /posts | GET | Get all posts (paginated) |
| /posts | POST | Create new post |
| /posts/{id} | GET | Get specific post |
| /posts/{id} | PUT | Update post |
| /posts/{id} | DELETE | Delete post |

## Environment Variables

```
DATABASE_URL=postgresql://postgres:password@postgres:5432/blogdb
JWT_SECRET_KEY=change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7
```

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| apisix | 9080 | API Gateway |
| auth-service | 5001 | Authentication |
| blog-service | 5002 | Blog API |
| postgres | 5432 | PostgreSQL database |
| etcd | 2379 | Config store |

## Project Structure

```
blog-api-mvp/
├── auth-service/       # Authentication microservice (Flask/SQLAlchemy)
├── blog-service/       # Blog CRUD microservice (Flask/SQLAlchemy)
├── frontend/           # Web frontend
├── scripts/            # Setup and test scripts
├── init-scripts/       # Database initialization
├── docker-compose.yml
├── .env.example
└── README.md
```