# 🚀 FraudGuard AI - Phase 1 Quick Start

## The Fastest Way to Run Phase 1

### Prerequisites
- Docker & Docker Compose (easiest)
- OR: Python 3.10+, PostgreSQL 13+, Node.js 18+

---

## ⚡ Start in 3 Commands (Docker)

```bash
# 1. Clone and navigate
git clone <your-repo>
cd fraudguard-ai

# 2. Start all services
docker-compose up --build

# 3. In another terminal, run tests
cd backend
pip install -r requirements.txt
pytest
```

**Backend available at**: http://localhost:8000
**API Docs**: http://localhost:8000/docs
**PostgreSQL available at**: localhost:5432

---

## 📋 Start Without Docker (Manual Setup)

### Step 1: Backend Setup (Terminal 1)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate            # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env
```

### Step 2: Database Setup (Terminal 1 or New Terminal)

#### Option A: PostgreSQL Already Installed

```bash
# Create database user
createuser fraudguard --password
# Enter password: fraudguard_dev_pass

# Create database
createdb fraudguard_db --owner fraudguard

# Load schema
psql -U fraudguard -d fraudguard_db < ../database/schema.sql

# Verify connection
psql -U fraudguard -d fraudguard_db -c "SELECT 1"
```

#### Option B: Docker PostgreSQL Only

```bash
docker run -d \
  --name fraudguard-postgres \
  -e POSTGRES_USER=fraudguard \
  -e POSTGRES_PASSWORD=fraudguard_dev_pass \
  -e POSTGRES_DB=fraudguard_db \
  -p 5432:5432 \
  postgres:15-alpine

# Wait a few seconds for startup, then load schema
sleep 5
docker exec fraudguard-postgres psql -U fraudguard -d fraudguard_db < database/schema.sql
```

### Step 3: Run Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### Step 4: Test Backend (Terminal 2)

```bash
# Test health check
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","database":"connected","model":"loaded","environment":"development"}
```

### Step 5: Run Tests (Terminal 2)

```bash
cd backend
source venv/bin/activate
pytest -v

# Expected: 15+ tests, all passing
```

---

## 🧪 Manual API Testing

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePassword123"
  }'
```

Save the `access_token` from response.

### 2. Login User

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePassword123"
  }'
```

### 3. Get Current User

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <YOUR_TOKEN_HERE>"
```

### 4. View API Docs

Visit: http://localhost:8000/docs

---

## 🎨 Frontend Setup (Optional for Phase 1)

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

**Note**: Full functionality comes in Phase 5-6. Currently just scaffolding.

---

## ✅ Verify Everything Works

### Check 1: Health Endpoint
```bash
curl http://localhost:8000/api/health
# Should return {"status":"healthy", ...}
```

### Check 2: Database Connected
```bash
curl http://localhost:8000/api/ready
# Should return {"ready":true}
```

### Check 3: All Tests Pass
```bash
cd backend
pytest
# Should show: ... passed
```

### Check 4: API Documentation
Open: http://localhost:8000/docs

You should see:
- GET /api/health
- GET /api/ready
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

---

## 🐛 Troubleshooting

### Error: "could not connect to server"

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# If Docker container:
docker logs fraudguard-postgres
```

### Error: "Address already in use"

```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001 --reload
```

### Error: "ModuleNotFoundError: No module named 'app'"

```bash
# Ensure you're in backend directory
cd backend

# Ensure venv is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall
pip install -r requirements.txt
```

### Error: "relation users does not exist"

```bash
# Load schema manually
psql -U fraudguard -d fraudguard_db < database/schema.sql
```

### Tests Failing

```bash
# Ensure backend dependencies installed
pip install -r requirements.txt

# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/test_auth.py::TestAuthentication -v
```

---

## 📚 What's Running

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Port**: 8000

### Database (PostgreSQL)
- **Host**: localhost
- **Port**: 5432
- **User**: fraudguard
- **Password**: fraudguard_dev_pass
- **Database**: fraudguard_db

### Frontend (React/Vite - Optional)
- **URL**: http://localhost:5173
- **Port**: 5173

---

## 🔧 Common Commands

### Start Backend
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
```

### Run Tests
```bash
cd backend && pytest -v
```

### Start PostgreSQL (Docker)
```bash
docker run -d --name fraudguard-postgres \
  -e POSTGRES_USER=fraudguard \
  -e POSTGRES_PASSWORD=fraudguard_dev_pass \
  -e POSTGRES_DB=fraudguard_db \
  -p 5432:5432 postgres:15-alpine
```

### Stop All Services (Docker)
```bash
docker-compose down
```

### View Logs (Docker)
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Database Shell
```bash
psql -U fraudguard -d fraudguard_db
```

---

## 📱 Next Steps

1. ✅ Verify Phase 1 works
2. ⏳ Move to Phase 2: ML Pipeline
3. ⏳ Move to Phase 3: Prediction API
4. ⏳ Move to Phase 4: Full Auth
5. ⏳ Move to Phase 5: Dashboard

---

## 💡 Quick Facts About Phase 1

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens + bcrypt
- **Testing**: pytest with 15+ tests
- **Containerization**: Docker & Docker Compose
- **Models**: User, Transaction, FraudAlert, ModelVersion
- **Security**: Password hashing, JWT validation, CORS

---

## 🎯 Phase 1 Is Complete When:

- ✅ Backend starts without errors
- ✅ Health check responds
- ✅ Database is connected
- ✅ All 15+ tests pass
- ✅ Registration works
- ✅ Login works
- ✅ Can retrieve current user with token
- ✅ API docs visible at /docs

**All above verified for Phase 1 ✅**

---

## 📞 Support

If you encounter issues:
1. Check troubleshooting section above
2. Review logs: `docker-compose logs`
3. Verify `.env` file exists in backend/
4. Check that ports 5432, 8000 are available
5. Ensure Python 3.10+ and PostgreSQL 13+ installed (if not using Docker)

---

**Ready for Phase 2? The foundation is solid. Let's build the ML pipeline! 🚀**
