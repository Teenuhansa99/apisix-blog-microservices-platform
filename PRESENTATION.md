# Apache APISIX API Gateway Demo Presentation

## 1. Project Introduction

### What This System Is
A **production-ready blog API system** built with microservices architecture using Apache APISIX as the API Gateway. It provides authentication and blog post management through two separate Flask microservices, unified by a single gateway.

### Why This System Was Created
- To demonstrate microservices architecture in action
- To show how API Gateways solve common API management problems
- To provide hands-on experience with modern API security (JWT)
- To understand containerization benefits using Docker

### What Problem It Solves
| Problem | Traditional Approach | This Solution |
|---------|-------------------|---------------|
| Multiple services | Each service on different ports | Single gateway entry point |
| Authentication | Repeated in each service | Centralized at gateway |
| Rate limiting | Implemented per service | Applied globally |
| Service discovery | Hard-coded URLs | Dynamic routing via etcd |

### What Apache APISIX Is
Apache APISIX is a **dynamic, real-time, high-performance API gateway**. It provides:
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and traffic control
- Observability and monitoring
- Plugin-based extensibility

### What an API Gateway Is
An API Gateway is a **single entry point** that:
- Routes requests to appropriate backend services
- Handles cross-cutting concerns (auth, rate limiting, logging)
- Provides security and traffic management
- Decouples clients from backend services

### Why API Gateways Are Important in Microservices
1. **Single Entry Point**: Clients don't need to know all service locations
2. **Centralized Security**: One place to enforce authentication
3. **Traffic Management**: Rate limiting, load balancing, retries
4. **Service Abstraction**: Backend changes don't affect clients

---

## 2. Full System Architecture Explanation

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (BROWSER)                          │
│                      Frontend (index.html)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Apache APISIX Gateway                          │
│                   Port: 9080 (API), 9180 (Admin)                │
├─────────────────────────────────────────────────────────────────┤
│  Routes:                                                         │
│  • /auth/* → Auth Service                                       │
│  • /posts* → Blog Service                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                             ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│    AUTH SERVICE          │     │    BLOG SERVICE          │
│    Flask:5001            │     │    Flask:5000            │
│    • /register          │     │    • /posts (GET/POST)   │
│    • /login            │     │    • /posts/<id> (GET/PUT/DEL)│
│    • /refresh          │     │    • /health             │
│    • /logout           │     │    • /health             │
└───────────────────────────┘     └───────────────────────────┘
                │                             │
                └───────────────┬───────────────┘
                                ▼
                ┌───────────────────────────────┐
                │        POSTGRESQL           │
                │        Port: 5432           │
                │        • users table        │
                │        • posts table        │
                │        • refresh_tokens     │
                └───────────────────────────────┘
```

### Request Flow Step-by-Step
1. **User submits request** from frontend to `localhost:9080`
2. **APISIX receives request** at gateway port 9080
3. **Route matching**: APISIX checks `/auth/*` or `/posts*` patterns
4. **Upstream selection**: Routes to appropriate service container
5. **Service processes request**: Auth or Blog service handles business logic
6. **Database interaction**: Service queries PostgreSQL for data
7. **Response returns**: Data flows back through the same path
8. **Frontend displays result**: User sees updated content

---

## 3. Technologies Used

| Technology | Why Selected |
|------------|--------------|
| **Apache APISIX** | Modern, high-performance gateway with dynamic configuration via etcd; supports plugins for auth, rate limiting, and observability |
| **Docker** | Containerization ensures consistent environments across dev/prod; isolates services for easy scaling |
| **Flask/Python** | Lightweight framework for microservices; easy to understand; good for APIs |
| **HTML/CSS/JS Frontend** | Simple, no build tools needed; demonstrates direct API consumption |
| **JWT Authentication** | Stateless authentication; scalable; works well with microservices |
| **etcd** | Distributed configuration store; APISIX uses it for dynamic route updates |
| **PostgreSQL** | Reliable relational database; ACID compliance; good for structured data |

---

## 4. How to Run the Project

### Prerequisites
- Docker and Docker Compose installed
- PowerShell (Windows) or Terminal (macOS/Linux)

### Docker Setup
```powershell
# 1. Navigate to project directory
cd C:\Users\teenu\blog-api-mvp

# 2. Start all containers
docker compose up -d

# 3. Check running containers
docker ps

# 4. Wait for services to be healthy (30-60 seconds)
```

### Expected Running Containers
```
CONTAINER ID   IMAGE                    STATUS
blog-api-mvp-etcd-1        quay.io/coreos/etcd     healthy
blog-api-mvp-postgres-1      postgres:15-alpine    healthy
blog-api-mvp-apisix-1        apache/apisix:latest  running
blog-api-mvp-auth-service-1  auth-service          running
blog-api-mvp-blog-service-1  blog-service          running
```

### Create APISIX Routes
```powershell
# Run the setup script (Windows)
.\setup-routes.bat

# Or run these commands manually:
curl -X PUT "http://127.0.0.1:9180/apisix/admin/upstreams/auth-upstream" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -H "Content-Type: application/json" -d "{\"nodes\":{\"auth-service:5001\":1},\"type\":\"roundrobin\"}"

curl -X PUT "http://127.0.0.1:9180/apisix/admin/upstreams/blog-upstream" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -H "Content-Type: application/json" -d "{\"nodes\":{\"blog-service:5000\":1},\"type\":\"roundrobin\"}"

curl -X PUT "http://127.0.0.1:9180/apisix/admin/routes/1" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -H "Content-Type: application/json" -d "{\"uri\":\"/auth/*\",\"upstream_id\":\"auth-upstream\",\"methods\":[\"POST\",\"GET\"]}"

curl -X PUT "http://127.0.0.1:9180/apisix/admin/routes/2" -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" -H "Content-Type: application/json" -d "{\"uri\":\"/posts*\",\"upstream_id\":\"blog-upstream\",\"methods\":[\"GET\",\"POST\",\"PUT\",\"DELETE\"]}"
```

### Open Frontend
- Navigate to `frontend/index.html` in your browser
- Or serve with Python: `python -m http.server 8000` in frontend folder

### Testing APIs
```bash
# Test auth service health
curl http://localhost:9080/auth/health

# Test blog service health  
curl http://localhost:9080/posts

# Run full demo flow
bash scripts/test_full_flow.sh
```

---

## 5. APISIX Gateway Functions Demonstration

### 1. API Routing
**What it does**: Directs incoming requests to correct backend service based on URL patterns.

**Why important**: Clients use one endpoint; gateway handles where to send requests internally.

**This project uses**: 
- `/auth/*` routes to auth-service
- `/posts*` routes to blog-service

**Test it**:
```bash
curl http://localhost:9080/auth/health  # Goes to auth-service
curl http://localhost:9080/posts        # Goes to blog-service
```

### 2. Reverse Proxy
**What it does**: Forward requests and return responses without client knowing backend location.

**Why important**: Hides internal architecture; enables load balancing and security.

**This project uses**: Requests to port 9080 are proxied to Flask services on ports 5000/5001.

**Test it**:
```bash
# Direct to backend (works)
curl http://blog-service:5000/posts

# Via gateway (same result)
curl http://localhost:9080/posts
```

### 3. JWT Authentication
**What it does**: Validates JWT tokens before allowing access to protected endpoints.

**Why important**: Prevents unauthorized access; stateless authentication.

**This project uses**: APISIX can validate JWT using `jwt-auth` plugin (can be enabled on routes).

**Setup example**:
```bash
curl -X PUT "http://127.0.0.1:9180/apisix/admin/routes/3" \
  -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" \
  -H "Content-Type: application/json" \
  -d '{"uri":"/protected/*","plugins":{"jwt-auth":{"secret":"super-secret-key"}},"upstream_id":"blog-upstream"}'
```

### 4. Rate Limiting
**What it does**: Limits number of requests per time period.

**Why important**: Prevents abuse; protects backend services.

**This project uses**: Can be added to routes via `limit-req` plugin.

**Setup example**:
```bash
curl -X PUT "http://127.0.0.1:9180/apisix/admin/routes/2" \
  -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1" \
  -H "Content-Type: application/json" \
  -d '{"uri":"/posts*","upstream_id":"blog-upstream","plugins":{"limit-req":{"rate":10,"burst":20}}}'
```

### 5. Request Forwarding
**What it does**: Takes incoming requests and forwards them with modified paths.

**Why important**: Clean URLs for clients; flexible backend routing.

**This project uses**: `/auth/login` becomes `/login` in auth-service via `proxy-rewrite`.

### 6. Microservices Communication
**What it does**: Enables services to communicate through the gateway.

**Why important**: Decouples services; enables independent scaling.

**This project uses**: Frontend talks only to gateway; gateway routes to services.

### 7. Centralized API Management
**What it does**: Single place to configure all API policies.

**Why important**: Changes to auth/rate limiting don't require service code changes.

**This project uses**: All routes configured in one place via Admin API.

---

## 6. Postman Testing Guide

### Step 1: Register User
```
POST http://localhost:9080/auth/register
Headers: Content-Type: application/json
Body: {
  "username": "testuser",
  "password": "testpass123",
  "email": "test@example.com"
}

Expected: {"message": "User registered successfully"}
Status: 201 Created
```

### Step 2: Login User
```
POST http://localhost:9080/auth/login
Headers: Content-Type: application/json
Body: {
  "username": "testuser",
  "password": "testpass123"
}

Expected: {
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
Status: 200 OK
```

### Step 3: Get JWT Token
Token is received in Step 2 login response. Save the `access_token` value for protected requests.

### Step 4: Create Blog Post
```
POST http://localhost:9080/posts
Headers: Content-Type: application/json
Body: {
  "title": "My First Post",
  "description": "Post content here",
  "category": "technology"
}

Expected: {
  "message": "Post created successfully",
  "post": {
    "id": 1,
    "title": "My First Post",
    "description": "Post content here",
    "category": "technology",
    "created_date": "2024-01-15 10:30:00"
  }
}
Status: 201 Created
```

### Step 5: Get All Posts
```
GET http://localhost:9080/posts

Expected: {
  "posts": [...],
  "total": 1,
  "page": 1,
  "pages": 1
}
Status: 200 OK
```

### Step 6: Delete Post
```
DELETE http://localhost:9080/posts/1

Expected: {"message": "Post deleted successfully"}
Status: 200 OK
```

---

## 7. System Workflow Scenario

### Real-World User Journey

1. **User opens frontend** - Opens `frontend/index.html` in browser
   - Frontend loads `script.js` which sets `API_URL = 'http://localhost:9080/posts'`

2. **User registers account** - Fills username/password and clicks register
   - Frontend sends POST to `http://localhost:9080/auth/register`
   - APISIX routes to auth-service based on `/auth/*` pattern

3. **Auth service validates and stores** - `auth-service/app.py`
   - Validates username/password requirements
   - Hashes password with bcrypt
   - Stores user in PostgreSQL `users` table
   - Returns success message

4. **User logs in** - Enters credentials
   - Frontend sends POST to `http://localhost:9080/auth/login`
   - APISIX routes to auth-service

5. **JWT token generated** - `auth-service/app.py`
   - Verifies credentials
   - Creates access token (30 min expiry) and refresh token (7 day expiry)
   - Stores refresh token in database
   - Returns tokens to frontend

6. **User creates blog post** - Fills title/description/category
   - Frontend sends POST to `http://localhost:9080/posts`
   - APISIX routes to blog-service

7. **Blog service processes** - `blog-service/app.py`
   - Receives post data
   - Validates required fields
   - Creates new record in PostgreSQL `posts` table
   - Returns created post

8. **User views posts** - Clicks "Load Posts"
   - Frontend sends GET to `http://localhost:9080/posts`
   - APISIX routes to blog-service

9. **Posts retrieved** - `blog-service/app.py`
   - Queries all posts from database
   - Returns paginated results
   - Frontend displays posts in HTML

---

## 8. Frontend and Backend Explanation

### Frontend (`frontend/`)
- **index.html**: Basic form with inputs for title, description, category
- **style.css**: Simple styling for layout
- **script.js**: Makes fetch requests to APISIX gateway (port 9080)
- Does NOT talk directly to microservice ports
- All communication goes through single gateway endpoint

### Auth Service (`auth-service/`)
- **Endpoints**:
  - `/register`: Creates new user with hashed password
  - `/login`: Validates credentials, returns JWT tokens
  - `/refresh`: Generates new access token using refresh token
  - `/logout`: Invalidates refresh token
  - `/health`: Health check endpoint
- Uses PostgreSQL for user storage
- Implements password hashing with bcrypt

### Blog Service (`blog-service/`)
- **Endpoints**:
  - `/posts`: GET (list all), POST (create)
  - `/posts/<id>`: GET (one), PUT (update), DELETE (remove)
  - `/health`: Health check endpoint
- Uses PostgreSQL for post storage
- Implements pagination

### APISIX Gateway
- Routes: `/auth/*` → auth-service:5001
- Routes: `/posts*` → blog-service:5000
- Uses etcd for configuration storage
- Provides single API entry point

### Communication Flow
```
Frontend → HTTP Request → APISIX:9080 → Route Match → Microservice → PostgreSQL → Response Reverse
```

---

## 9. Supervisor Demo Presentation Guide

### What to Explain First
1. **Start with the big picture** - Show architecture diagram
2. **Explain the problem** - Why do we need API Gateways?
3. **Demo the running system** - Show containers, test APIs

### Commands to Show
```powershell
# Show architecture
docker ps

# Test health endpoints
curl http://localhost:9080/auth/health
curl http://localhost:9080/posts

# Show route configuration
curl http://localhost:9180/apisix/admin/routes -H "X-API-KEY: edd1c9f034335f136f87ad84b625c8f1"
```

### Features to Demonstrate
1. **Routing** - Same gateway, different services
2. **Authentication** - Register and login flow
3. **Create/View/Delete** - Full CRUD operations
4. **Proxy-rewrite** - Clean URL paths

### Important Technical Points
- Dynamic configuration via etcd (no restart needed)
- Microservices independently deployable
- JWT tokens for stateless auth
- Docker networking (services communicate by container name)
- Single entry point (9080) for all APIs

---

## 10. Future Improvements

### Database
- **MySQL/PostgreSQL improvements**: Connection pooling, read replicas, backups

### Frontend
- **React frontend**: Component-based, state management, better UX

### Security
- **HTTPS/TLS**: Encrypt all traffic
- **Role-based authentication**: Admin/user permissions
- **API key management**: For third-party integrations

### Infrastructure
- **Kubernetes deployment**: Auto-scaling, service discovery
- **Load balancing**: Multiple instances of each service
- **Monitoring**: Grafana dashboards for API metrics

### Observability
- **Logging systems**: ELK stack for centralized logs
- **Tracing**: Jaeger for request tracing
- **Alerting**: Slack/email notifications on errors

### Advanced Features
- **Caching**: Redis cache for frequently accessed posts
- **Rate limiting**: Per-user/per-IP limits
- **API versioning**: `/v1/posts`, `/v2/posts`
- **Webhooks**: Real-time notifications

---

## 11. Learning Outcomes

### API Gateway Concepts
- Single entry point for multiple services
- Centralized traffic management
- Service abstraction and decoupling

### APISIX Configuration
- Dynamic route configuration via Admin API
- Plugin-based architecture
- etcd integration for configuration storage

### Docker Containerization
- Multi-container orchestration
- Service isolation and networking
- Environment variables for configuration

### JWT Authentication
- Stateless token-based auth
- Access and refresh token patterns
- Secure password storage with bcrypt

### Microservices Architecture
- Service separation of concerns
- Independent development and deployment
- Database sharing patterns

### API Routing
- URI-based routing rules
- Upstream load balancing
- Proxy rewriting for clean URLs

### Reverse Proxy Concepts
- Request forwarding
- Response handling
- Protocol mediation

### Environment Variables (.env)
DATABASE_URL=postgresql://postgres:password@postgres:5432/blogdb
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7

### API Security
- Authentication at gateway level
- Rate limiting protection
- Input validation

---

## Quick Reference Commands

### Start System
```powershell
docker compose up -d
.\setup-routes.bat
```

### Test APIs
```bash
curl http://localhost:9080/auth/health
curl http://localhost:9080/posts
```

### Stop System
```powershell
docker compose down -v
```