# 🚀 FraudGuard AI - Quick Start Guide

Get up and running in 5 minutes!

## Option 1: Docker (Recommended for Quick Demo)

```bash
# 1. Clone and navigate
git clone <repo-url>
cd fraudguard-ai

# 2. Start all services
docker-compose up -d

# 3. Wait for services to start
docker-compose ps

# 4. Create admin account
docker exec fraudguard-backend python -m backend.scripts.create_admin
# Follow the prompts to create your admin account

# 5. Open in browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## Option 2: Local Development (For Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15

### Setup

**Terminal 1: Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start server
uvicorn app.main:app --reload
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Terminal 2: Frontend**
```bash
cd frontend
npm install
npm run dev
# Frontend: http://localhost:5173
```

**Terminal 3: Admin Setup**
```bash
cd backend
python -m backend.scripts.create_admin
```

## Option 3: Production Deploy (Vercel + Render)

### 1. Setup Frontend (Vercel)

```bash
# Push to GitHub
git push origin main

# Go to vercel.com → Import Project
# - Select your repository
# - Root directory: ./frontend
# - Framework: Vite
# - Environment: VITE_API_BASE_URL=https://your-backend.onrender.com
# - Deploy
```

### 2. Setup Backend (Render)

```bash
# Go to render.com → Create Web Service
# - Connect GitHub repository
# - Root directory: ./backend
# - Build command: pip install -r requirements.txt
# - Start command: gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 2
# - Environment variables:
#   - DATABASE_URL=postgresql://...
#   - JWT_SECRET_KEY=your-secret-key
#   - CORS_ORIGINS=["https://your-vercel-url"]
#   - ENVIRONMENT=production
#   - DEBUG=False
# - Deploy
```

### 3. Setup Database

```bash
# Option A: AWS RDS
# - Create RDS PostgreSQL instance
# - Copy connection URL to DATABASE_URL in Render

# Option B: Heroku Postgres
# - Create Postgres add-on
# - Copy DATABASE_URL to Render

# Initialize database
psql $DATABASE_URL < database/schema.sql

# Create admin user (SSH into Render backend)
python -m backend.scripts.create_admin
```

## Verify Installation

```bash
# Check backend
curl http://localhost:8000/api/health

# Check database
psql $DATABASE_URL -c "SELECT * FROM users LIMIT 1;"

# Check SHAP
curl http://localhost:8000/api/health/explainer

# View API docs
open http://localhost:8000/docs
```

## First Steps After Setup

1. **Login with admin account**
   - Email: Your admin email
   - Password: Your admin password

2. **Test prediction**
   ```bash
   curl -X POST http://localhost:8000/api/transactions/predict \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "Time": 0.0,
       "V1": 1.234,
       "V2": -0.445,
       "V3": 0.5,
       "V4": -1.2,
       "V5": 0.8,
       "V6": 0.3,
       "V7": -0.6,
       "V8": 0.4,
       "V9": -0.2,
       "V10": 0.7,
       "V11": -0.9,
       "V12": 0.5,
       "V13": 0.2,
       "V14": -1.5,
       "V15": 0.6,
       "V16": -0.4,
       "V17": 0.8,
       "V18": -0.3,
       "V19": 0.5,
       "V20": -0.7,
       "V21": 0.2,
       "V22": 0.6,
       "V23": -0.4,
       "V24": 0.3,
       "V25": -0.1,
       "V26": 0.5,
       "V27": 0.2,
       "V28": -0.6,
       "Amount": 123.45
     }'
   ```

3. **Get explanation**
   ```bash
   curl http://localhost:8000/api/transactions/{id}/explanation \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **View dashboard**
   - Go to http://localhost:5173
   - Navigate to Transactions
   - Click on any transaction
   - Click "Why this prediction?"

## Environment Variables

### Backend (backend/.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/fraudguard
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

### Frontend (frontend/.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

## Docker Useful Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Stop services
docker-compose stop

# Remove containers
docker-compose down

# Full cleanup (removes data!)
docker-compose down -v

# Rebuild containers
docker-compose up -d --build

# Execute command in container
docker exec fraudguard-backend python -m backend.scripts.create_admin
```

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # Database

# Kill process
kill -9 <PID>
```

### Database connection failed
```bash
# Check PostgreSQL is running
pg_isready -h localhost

# Check credentials
psql -U user -d fraudguard -c "SELECT 1;"

# Verify DATABASE_URL format
# postgresql://username:password@host:port/database
```

### Frontend can't reach API
```bash
# Check API is running
curl http://localhost:8000/api/health

# Check CORS setting
# CORS_ORIGINS should include your frontend URL

# Check frontend environment variable
# VITE_API_BASE_URL=http://localhost:8000
```

### ML Model not found
```bash
# Check artifacts exist
ls -la ml/artifacts/

# Should see:
# - fraud_model.joblib
# - preprocessor.joblib
# - model_metadata.json

# Check paths in .env
MODEL_PATH=../ml/artifacts/fraud_model.joblib
```

## Next Steps

1. **Read full documentation**
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
   - [docs/explainability.md](docs/explainability.md) - SHAP guide
   - [API Docs](http://localhost:8000/docs) - Interactive API docs

2. **Explore the application**
   - Login as admin
   - Create test users
   - Make predictions
   - View explanations
   - Manage alerts

3. **Deploy to production**
   - Follow DEPLOYMENT_GUIDE.md
   - Setup Vercel + Render
   - Configure database
   - Enable monitoring

## Support

- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions
- **Email**: support@fraudguard.ai

---

**Ready to detect fraud?** 🚀

Deploy now and start getting real fraud predictions!
