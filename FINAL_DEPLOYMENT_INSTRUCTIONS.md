# 🎯 FraudGuard AI - FINAL DEPLOYMENT INSTRUCTIONS

## Complete Guide to Deploy Production-Ready Fraud Detection Platform

---

## 📦 Getting the Project

### Option 1: From GitHub
```bash
git clone https://github.com/yourusername/fraudguard-ai.git
cd fraudguard-ai
```

### Option 2: Extract from ZIP
```bash
unzip fraudguard-ai.zip
cd fraudguard-ai
```

### Option 3: Use Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

---

## 🚀 THREE DEPLOYMENT PATHS

Choose ONE based on your needs:

---

## PATH 1: Docker (Local/Self-Hosted) - 5 MINUTES

**Best for**: Quick demo, staging, self-hosted production

### Step 1: Prepare Environment
```bash
# Edit configuration
nano backend/.env

# Must have:
DATABASE_URL=postgresql://fraudguard:password@postgres:5432/fraudguard
JWT_SECRET_KEY=your-secure-random-string-minimum-32-chars
CORS_ORIGINS=["http://localhost:3000"]
```

### Step 2: Start All Services
```bash
# Start everything
docker-compose up -d

# Wait for services (30 seconds)
docker-compose ps

# All should show "healthy" or "running"
```

### Step 3: Create Admin User
```bash
docker exec fraudguard-backend python -m backend.scripts.create_admin

# Follow prompts:
# Email: your@email.com
# Full Name: Your Name
# Password: strongpassword123
```

### Step 4: Access Application
```
Frontend:  http://localhost:3000
API:       http://localhost:8000
Docs:      http://localhost:8000/docs
Database:  localhost:5432
```

### Step 5: Verify Everything Works
```bash
# Backend health
curl http://localhost:8000/api/health

# Database
curl http://localhost:8000/api/ready

# SHAP service
curl http://localhost:8000/api/health/explainer
```

### Stop/Cleanup
```bash
# Stop but keep data
docker-compose stop

# Stop and remove
docker-compose down

# Full cleanup (removes data!)
docker-compose down -v
```

---

## PATH 2: Vercel + Render (RECOMMENDED) - 20 MINUTES

**Best for**: Small teams, low maintenance, free tier available

### Step 1: Push to GitHub

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Add remote
git remote add origin https://github.com/yourusername/fraudguard-ai.git

# Push
git push -u origin main
```

### Step 2: Deploy Frontend (Vercel)

```bash
# Visit vercel.com
# 1. Click "Import Project"
# 2. Select your GitHub repository
# 3. Configure:
#    - Framework: Vite
#    - Root directory: ./frontend
# 4. Environment Variables:
#    - VITE_API_BASE_URL: https://your-backend.onrender.com/api
# 5. Click Deploy
```

**Result**: Frontend deployed to `https://your-name.vercel.app`

### Step 3: Deploy Backend (Render)

```bash
# Visit render.com
# 1. Click "New +" → "Web Service"
# 2. Connect GitHub repository
# 3. Configure:
#    - Name: fraudguard-backend
#    - Root directory: ./backend
#    - Runtime: Python 3.10
#    - Build command: pip install -r requirements.txt
#    - Start command: gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 2
# 4. Environment Variables (click "Add Environment Variable"):
#    - DATABASE_URL: postgresql://...
#    - JWT_SECRET_KEY: your-secret-key-min-32-chars
#    - CORS_ORIGINS: ["https://your-name.vercel.app"]
#    - ENVIRONMENT: production
#    - DEBUG: False
#    - LOG_LEVEL: WARNING
# 5. Click Deploy
```

**Result**: Backend deployed to `https://fraudguard-backend.onrender.com`

### Step 4: Setup Database

#### Option A: AWS RDS (Recommended)

```bash
# 1. Go to aws.amazon.com
# 2. RDS → Databases → Create Database
# 3. Select PostgreSQL 15
# 4. Instance class: t3.micro (free tier eligible)
# 5. Allocated storage: 20GB
# 6. Set master username: fraudguard
# 7. Set strong password
# 8. VPC Security: Allow access from Render's IP
# 9. Create database

# Copy connection URL: 
# postgresql://fraudguard:password@host:5432/fraudguard

# Copy to Render Dashboard → Environment Variables → DATABASE_URL

# Initialize schema:
psql $DATABASE_URL < database/schema.sql
```

#### Option B: Heroku Postgres (Simpler)

```bash
# 1. heroku login
# 2. heroku addons:create heroku-postgresql:standard-0 -a your-app-name
# 3. Get DATABASE_URL from config vars
# 4. Copy to Render Dashboard
# 5. Initialize schema:
psql $DATABASE_URL < database/schema.sql
```

### Step 5: Create Admin User

```bash
# SSH into Render backend (Render Dashboard → your-app → Shell)
python -m backend.scripts.create_admin

# Or use Render's one-time command:
# In Render Dashboard → click your backend service → click "Run Command"
# Command: python -m backend.scripts.create_admin
```

### Step 6: Test Production

```bash
# Test backend
curl https://fraudguard-backend.onrender.com/api/health

# Login
curl -X POST https://fraudguard-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Open in browser
open https://your-name.vercel.app
```

### Vercel + Render Benefits
- ✅ Auto-deploys on git push
- ✅ Free tier available
- ✅ Minimal maintenance
- ✅ Built-in monitoring
- ✅ Scales automatically
- ✅ Easy environment management

---

## PATH 3: AWS (Advanced) - 1 HOUR

**Best for**: Large scale, high availability, full control

### Step 1: Setup ECS & RDS

```bash
# Create RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier fraudguard-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username fraudguard \
  --master-user-password YourStrongPassword123 \
  --allocated-storage 20

# Create ECR repositories
aws ecr create-repository --repository-name fraudguard-backend
aws ecr create-repository --repository-name fraudguard-frontend
```

### Step 2: Build & Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Build & push backend
docker build -t fraudguard-backend ./backend
docker tag fraudguard-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/fraudguard-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/fraudguard-backend:latest

# Build & push frontend
docker build -t fraudguard-frontend ./frontend
docker tag fraudguard-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/fraudguard-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/fraudguard-frontend:latest
```

### Step 3: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name fraudguard

# Create task definitions
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
aws ecs register-task-definition --cli-input-json file://frontend-task-def.json
```

### Step 4: Setup Load Balancer

```bash
# Create ALB (Application Load Balancer)
# Configure to route to backend and frontend
# Setup SSL certificates
```

### Step 5: Deploy Services

```bash
# Create services
aws ecs create-service \
  --cluster fraudguard \
  --service-name backend \
  --task-definition fraudguard-backend \
  --desired-count 2

aws ecs create-service \
  --cluster fraudguard \
  --service-name frontend \
  --task-definition fraudguard-frontend \
  --desired-count 2
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

After any deployment:

```bash
# 1. Test health endpoints
curl https://your-api/api/health

# 2. Test database connection
curl https://your-api/api/ready

# 3. Test login
# Go to frontend, try logging in

# 4. Test prediction
# Make a test prediction

# 5. Test SHAP
# View explanation for a prediction

# 6. Review logs
# Check for errors

# 7. Setup monitoring
# Configure alerts in Render/AWS

# 8. Setup backups
# Configure automated backups
```

---

## 🔧 Common Issues & Solutions

### Issue: "Database connection refused"
```bash
# Check DATABASE_URL format
# Must be: postgresql://user:pass@host:port/db

# Test connection locally
psql $DATABASE_URL -c "SELECT 1;"

# For Render: ensure it's set in Environment Variables
```

### Issue: "CORS errors"
```bash
# Update CORS_ORIGINS in environment
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Restart backend
# (Vercel/Render auto-redeploy)
```

### Issue: "ML model not found"
```bash
# Check files exist
ls ml/artifacts/
# Should show:
# - fraud_model.joblib
# - preprocessor.joblib
# - model_metadata.json

# Check paths in .env
# MODEL_PATH=../ml/artifacts/fraud_model.joblib
```

### Issue: "JWT secret not set"
```bash
# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update in environment variables
JWT_SECRET_KEY=your-new-secret
```

### Issue: "Frontend can't reach API"
```bash
# Check API_BASE_URL in frontend .env
VITE_API_BASE_URL=https://your-backend.onrender.com

# Check CORS on backend
CORS_ORIGINS includes your frontend URL
```

---

## 📊 Production Monitoring

### Health Checks
```bash
# Setup these as monitoring endpoints:
GET /api/health              # Backend health
GET /api/ready               # Database ready
GET /api/health/explainer    # SHAP service
GET /api/model/info          # Model info
```

### Logs & Alerts
```bash
# Render: View logs in dashboard
# AWS CloudWatch: Monitor via CLI
# Setup alerts for:
# - Error rate > 1%
# - Response time > 1s
# - Database connections > 10
```

### Backups
```bash
# Automated:
# - AWS RDS: Enable automated backups (7 days)
# - Heroku: Automatic daily backups

# Manual:
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
```

---

## 🔐 Security Hardening

### Before Going Live

```bash
# 1. Update JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Set strong database password
# 16+ chars, mixed case, numbers, symbols

# 3. Enable HTTPS
# Vercel: Automatic
# Render: Automatic
# AWS: Use ACM certificates

# 4. Configure security headers
# Already configured in FastAPI

# 5. Enable database backups
# AWS RDS: Enable automated backups
# Heroku: Automatic daily backups

# 6. Setup monitoring
# Monitor for errors and anomalies

# 7. Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

---

## 💰 Cost Estimation

### Monthly Costs

| Service | Free Tier | Starter | Pro |
|---------|-----------|---------|-----|
| Frontend (Vercel) | $0 | $20 | $50+ |
| Backend (Render) | $0* | $7 | $25 |
| Database (AWS RDS) | $0** | $15 | $50+ |
| **Total** | **$0-15** | **$42** | **$125+** |

*Render free tier has limitations  
**AWS RDS free tier only for 12 months

---

## 🚀 Deployment Decision Matrix

| Need | Recommendation | Cost | Time |
|------|----------------|------|------|
| Quick demo | Docker | Free | 5 min |
| Small team | Vercel + Render | $42/mo | 20 min |
| Production | Vercel + RDS | $40/mo | 30 min |
| Enterprise | AWS/GCP | $200+/mo | 2+ hrs |

---

## 📚 Additional Resources

### Documentation
- **README.md** - Project overview
- **QUICK_START.md** - 5-minute setup
- **DEPLOYMENT_GUIDE.md** - Comprehensive guide
- **docs/explainability.md** - SHAP guide
- **API Docs** - Interactive at `/docs`

### Getting Help
- **GitHub Issues** - Report bugs
- **GitHub Discussions** - Ask questions
- **Email** - Critical issues

### Monitoring Tools
- **Render Dashboard** - Built-in monitoring
- **AWS CloudWatch** - AWS monitoring
- **DataDog** - Third-party monitoring
- **Sentry** - Error tracking

---

## 🎯 Quick Reference

### Docker
```bash
docker-compose up -d                              # Start
docker-compose stop                               # Stop
docker-compose logs -f backend                    # View logs
docker exec fraudguard-backend curl /api/health   # Test
```

### Vercel + Render
```bash
git push origin main                              # Auto-deploys
# Monitor in Vercel & Render dashboards
# No manual deployment needed
```

### Environment Variables
```bash
# Must have (all paths)
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=... (min 32 chars)
CORS_ORIGINS=[...]

# Should have (production)
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
```

### Testing
```bash
curl http://localhost:8000/api/health             # Health check
curl -X POST http://localhost:8000/api/auth/login # Login
python -m pytest tests/                           # Run tests
npm test                                          # Frontend tests
```

---

## ✨ You're Ready!

You have everything needed to deploy FraudGuard AI:

✅ **Complete project** - All code included  
✅ **Multiple deployment options** - Docker, Vercel+Render, AWS  
✅ **Detailed guides** - Step-by-step instructions  
✅ **Production ready** - Security, monitoring, backups  
✅ **Real ML model** - Trained XGBoost with SHAP  
✅ **Full documentation** - API docs, guides, tutorials  

**Choose your deployment path above and get started!**

---

## 🎉 Final Thoughts

This is a **production-grade fraud detection platform**:
- Real ML model (not fake)
- Real predictions (not hardcoded)
- Real security (JWT + IDOR protection)
- Real explainability (SHAP values)
- Real database (PostgreSQL)
- Ready for millions of predictions

**You're now equipped to detect fraud at scale!** 🚀

---

## 📞 Questions?

- Deployment issues? → See DEPLOYMENT_GUIDE.md Part 7
- How to use? → See QUICK_START.md
- API questions? → See /docs endpoint
- SHAP questions? → See docs/explainability.md

**Happy fraud detecting!** 🎯
