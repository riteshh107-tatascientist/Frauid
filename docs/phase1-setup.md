# Phase 1: Backend Foundation - Setup Guide

## Overview

Phase 1 establishes:
- ✅ FastAPI backend foundation
- ✅ PostgreSQL database schema
- ✅ JWT authentication system
- ✅ Database models and ORM setup
- ✅ Health check endpoints
- ✅ Security utilities (password hashing, JWT tokens)
- ✅ Docker and Docker Compose
- ✅ Comprehensive test suite

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Node.js 18+ (for frontend)
- Git
- Docker & Docker Compose (optional but recommended)

## Quick Start (Docker Compose - Recommended)

### 1. Clone and Navigate

```bash
git clone <your-repo>
cd fraudguard-ai
```

### 2. Start Services with Docker Compose

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL on localhost:5432
- Create database and schema
- Start FastAPI backend on localhost:8000

### 3. Verify Backend is Running

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded",
  "environment": "development"
}
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Manual Setup (Without Docker)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate          # macOS/Linux
# or
venv\Scripts\activate            # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Using PostgreSQL Locally

```bash
# Create database user and database
createuser fraudguard --password
# Enter password: fraudguard_dev_pass

# Create database
createdb fraudguard_db --owner fraudguard

# Load schema
psql -U fraudguard -d fraudguard_db -f ../database/schema.sql
```

#### Option B: Using Docker for PostgreSQL Only

```bash
# Start only PostgreSQL container
docker run -d \
  --name fraudguard-postgres \
  -e POSTGRES_USER=fraudguard \
  -e POSTGRES_PASSWORD=fraudguard_dev_pass \
  -e POSTGRES_DB=fraudguard_db \
  -p 5432:5432 \
  -v $(pwd)/database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql \
  postgres:15-alpine
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env (optional for development)
nano .env
```

Default values in `.env.example` are suitable for development.

### 4. Verify Database Connection

```bash
cd backend
python -c "from app.core.database import engine; engine.connect(); print('✅ Database connected')"
```

### 5. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

---

## Testing

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test Class

```bash
pytest tests/test_auth.py::TestAuthentication -v
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest --cov=app tests/
```

### Expected Test Output

Phase 1 includes 15+ tests covering:
- ✅ Health check endpoints
- ✅ User registration
- ✅ User login
- ✅ Duplicate user prevention
- ✅ Invalid credentials handling
- ✅ Password hashing and verification
- ✅ JWT token generation and validation
- ✅ Current user retrieval
- ✅ Authorization checking

---

## API Endpoints - Phase 1

### Health & Status

```bash
GET /api/health
# Response: {"status": "healthy", "database": "connected", "model": "loaded"}

GET /api/ready
# Response: {"ready": true}
```

### Authentication

```bash
# Register
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepassword123"
}

# Response: 201 Created
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_admin": false,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

```bash
# Login
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "securepassword123"
}

# Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": { ... }
}
```

```bash
# Get Current User
GET /api/auth/me
Authorization: Bearer <token>

# Response: 200 OK
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00"
}
```

---

## Database Schema - Phase 1

### Tables Created

1. **users** - User accounts and authentication
   - id (primary key)
   - username (unique)
   - email (unique)
   - hashed_password
   - is_active, is_admin
   - created_at, updated_at

2. **transactions** - Transaction data with predictions
   - id, user_id (foreign key)
   - Transaction details (amount, type, time, etc.)
   - Risk features (new_device, location_change, etc.)
   - ML predictions (fraud_probability, risk_score, risk_level, prediction)
   - Risk factors and SHAP values (as JSON)
   - Metadata (created_at, updated_at)

3. **fraud_alerts** - High-risk transaction alerts
   - id, user_id, transaction_id (foreign keys)
   - status (OPEN, REVIEWED, RESOLVED)
   - risk_score, reason
   - Metadata

4. **model_versions** - ML model tracking
   - version, model_type, training_date
   - Dataset info
   - Performance metrics (precision, recall, f1, roc_auc, pr_auc)
   - Metadata

---

## Troubleshooting

### PostgreSQL Connection Error

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Check DATABASE_URL in .env
echo $DATABASE_URL

# Restart PostgreSQL
# macOS
brew services restart postgresql

# Linux
sudo systemctl restart postgresql

# Docker
docker restart fraudguard-postgres
```

### Port Already in Use

**Error**: `Address already in use` (port 5432 or 8000)

**Solution**:
```bash
# Find process using port
lsof -i :8000  # For backend
lsof -i :5432  # For database

# Kill process
kill -9 <PID>

# Or change port in uvicorn command
uvicorn app.main:app --port 8001
```

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure you're in backend directory
cd backend

# Verify virtual environment is activated
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Schema Not Loaded

**Error**: `relation "users" does not exist`

**Solution**:
```bash
# Manually load schema
cd database
psql -U fraudguard -d fraudguard_db -f schema.sql

# Or using Docker
docker exec fraudguard-postgres psql -U fraudguard -d fraudguard_db -f /docker-entrypoint-initdb.d/01-schema.sql
```

### CORS Issues

**Error**: `CORS policy blocked request`

**Solution**:
- Update CORS_ORIGINS in `.env` to include frontend URL
- Default includes localhost:5173 and localhost:3000

### JWT Secret Key Warning

**Warning**: Using default JWT_SECRET_KEY

**Action Required for Production**:
```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
JWT_SECRET_KEY=<generated-secret>
```

---

## Frontend Setup (Phase 1 - Optional)

Frontend pages are created but not fully functional until Phase 4-5.

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Next Steps

Phase 1 is complete when:
- ✅ Backend starts without errors
- ✅ Database connection verified
- ✅ All tests pass
- ✅ Health check responds
- ✅ Authentication endpoints work

**Next**: Proceed to Phase 2 - ML Pipeline & Dataset

---

## Contact & Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in backend console
3. Check PostgreSQL logs
4. Verify `.env` configuration
