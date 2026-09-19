# FraudGuard AI - Complete Deployment Guide

## Overview

FraudGuard AI is a production-ready fraud detection platform with:
- **Backend**: FastAPI + PostgreSQL + ML Model (XGBoost)
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **ML**: Real trained XGBoost model with SHAP explainability
- **Database**: PostgreSQL with comprehensive schema
- **Security**: JWT authentication, IDOR protection, role-based access

This guide covers local development, Docker deployment, and cloud production deployment.

---

## Prerequisites

### Local Development
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Git

### Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

### Cloud Deployment (Recommended for Production)
- Vercel account (frontend)
- Render.com account (backend)
- Managed PostgreSQL (AWS RDS, Heroku Postgres, etc.)

---

## Part 1: Local Development Setup

### 1.1 Clone & Install Dependencies

```bash
# Clone repository
git clone <repo-url>
cd fraudguard-ai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (in new terminal)
cd frontend
npm install
```

### 1.2 Configure Environment Variables

**Backend** (`backend/.env`):
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fraudguard

# JWT Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your-secure-random-string-minimum-32-chars
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (for frontend)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# ML Model paths (relative to backend root)
MODEL_PATH=../ml/artifacts/fraud_model.joblib
PREPROCESSOR_PATH=../ml/artifacts/preprocessor.joblib
MODEL_METADATA_PATH=../ml/artifacts/model_metadata.json
```

**Frontend** (`frontend/.env`):
```bash
# API endpoint
VITE_API_BASE_URL=http://localhost:8000
```

### 1.3 Setup Database

```bash
# Start PostgreSQL
# On macOS: brew services start postgresql
# On Linux: sudo systemctl start postgresql
# On Windows: Open PostgreSQL pgAdmin and start server

# Create database and schema
psql -U postgres -c "CREATE DATABASE fraudguard;"
psql -U postgres -d fraudguard -f database/schema.sql

# Or use the schema.sql file directly in your SQL client
```

### 1.4 Run Application

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
# Frontend: http://localhost:5173
```

**Terminal 3 - Create Admin User**:
```bash
cd backend
python -m backend.scripts.create_admin
# Follow prompts to create admin account
```

### 1.5 Verify Installation

```bash
# Backend health check
curl http://localhost:8000/api/health

# Frontend loads at
open http://localhost:5173

# API Docs
open http://localhost:8000/docs
```

---

## Part 2: Docker Deployment (Local/Production)

### 2.1 Build and Run with Docker Compose

```bash
# Development (with hot reload)
docker-compose up -d

# Production (optimized)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2.2 Initialize Database

```bash
# Create admin user in Docker
docker exec fraudguard-backend python -m backend.scripts.create_admin

# Or run migrations if using Alembic
docker exec fraudguard-backend alembic upgrade head
```

### 2.3 Verify Docker Deployment

```bash
# Check service health
docker-compose ps

# Test backend
docker exec fraudguard-backend curl http://localhost:8000/api/health

# View database
docker exec -it fraudguard-postgres psql -U fraudguard -d fraudguard -c "\dt"
```

### 2.4 Stop Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Full cleanup (removes everything including data)
docker-compose down -v
```

---

## Part 3: Production Deployment (Recommended Architecture)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CDN (CloudFlare)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                 │
    ┌────▼─────┐                    ┌────▼──────┐
    │  Vercel   │                    │   Render  │
    │ (Frontend)│                    │ (Backend) │
    └────┬─────┘                    └────┬──────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                    ┌────▼────┐
                    │  Nginx   │
                    │ Reverse  │
                    │  Proxy   │
                    └────┬────┘
                         │
                    ┌────▼─────────────┐
                    │   AWS RDS / AWS  │
                    │  Heroku Postgres │
                    └──────────────────┘
```

### 3.1 Option A: Vercel (Frontend) + Render (Backend)

#### Frontend Deployment (Vercel)

```bash
# 1. Push to GitHub
git push origin main

# 2. Connect GitHub to Vercel
# - Go to vercel.com
# - Click "Import Project"
# - Select your repository
# - Framework: Vite
# - Root: ./frontend

# 3. Environment Variables (in Vercel Dashboard)
VITE_API_BASE_URL=https://your-backend.onrender.com
```

#### Backend Deployment (Render)

```bash
# 1. Create render.com account

# 2. Create New Web Service
# - Connect GitHub repository
# - Select your repo
# - Branch: main
# - Environment: Python 3.10
# - Build Command: pip install -r requirements.txt
# - Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Environment Variables (in Render Dashboard)
DATABASE_URL=postgresql://user:pass@host:5432/fraudguard
JWT_SECRET_KEY=your-secure-random-string
CORS_ORIGINS=["https://your-vercel-domain.vercel.app"]
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# 4. Add PostgreSQL service
# - Create new PostgreSQL database
# - Note the connection URL
```

#### Database Setup (AWS RDS or Heroku Postgres)

```bash
# AWS RDS
# 1. Go to AWS Console
# 2. Create RDS PostgreSQL 15 instance
# 3. Security: Allow traffic from Render IP
# 4. Copy connection URL to DATABASE_URL

# OR Heroku Postgres
# 1. heroku login
# 2. heroku addons:create heroku-postgresql:standard-0 -a your-app-name
# 3. Get DATABASE_URL from config vars

# Initialize schema
psql $DATABASE_URL < database/schema.sql

# Create admin user (connect via SSH to backend)
python -m backend.scripts.create_admin
```

### 3.2 Option B: AWS/GCP/Azure (Complete Control)

#### Using AWS (Recommended)

```bash
# 1. ECS Fargate for containers
# 2. RDS PostgreSQL for database
# 3. S3 for ML artifacts
# 4. CloudFront for CDN
# 5. Route53 for DNS

# Quick deployment with AWS CLI
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin
docker build -t fraudguard-backend ./backend
docker tag fraudguard-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/fraudguard:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/fraudguard:latest
```

#### Using Kubernetes (Advanced)

```bash
# If using Docker Swarm or Kubernetes
docker stack deploy -c docker-compose.yml fraudguard

# Or with Kubernetes
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/postgres.yml
kubectl apply -f k8s/backend.yml
kubectl apply -f k8s/frontend.yml
kubectl apply -f k8s/ingress.yml
```

---

## Part 4: Production Security Checklist

### 4.1 Environment Security

```bash
# ✅ NEVER commit .env file
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore

# ✅ Use strong JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# ✅ Use strong database password
openssl rand -base64 32

# ✅ Enable HTTPS everywhere
# Vercel: automatic
# Render: automatic
# Custom: use Let's Encrypt/Certbot

# ✅ Configure CORS properly
CORS_ORIGINS=["https://your-frontend-domain.com"]

# ✅ Set secure cookies
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### 4.2 Database Security

```bash
# ✅ Enable SSL for PostgreSQL connections
DATABASE_URL=postgresql://user:pass@host:5432/fraudguard?sslmode=require

# ✅ Regular backups
# AWS RDS: Automatic backups enabled
# Heroku: Automated backups
# Manual: pg_dump -U username dbname > backup.sql

# ✅ Restrict database access
# Allow only backend service
# Deny public internet access
```

### 4.3 Application Security

```bash
# ✅ Use secure dependencies
pip install --upgrade --upgrade-strategy eager -r requirements.txt
npm audit --production

# ✅ Enable security headers
# Already in place: CORS, CSRF, etc.

# ✅ Rate limiting
# Consider adding for production

# ✅ Monitor logs
# Render: Built-in logging
# AWS: CloudWatch

# ✅ Set up alerts
# Monitor error rates
# Monitor database connections
```

---

## Part 5: Monitoring & Maintenance

### 5.1 Health Checks

```bash
# Backend health
curl https://your-backend.onrender.com/api/health

# Database connection
curl https://your-backend.onrender.com/api/ready

# SHAP explainability
curl https://your-backend.onrender.com/api/health/explainer

# Model info
curl https://your-backend.onrender.com/api/model/info
```

### 5.2 Logging

```bash
# View backend logs
docker logs fraudguard-backend

# Render logs (web UI)
# Settings → Logs

# AWS CloudWatch
aws logs tail /fraudguard/backend --follow

# Stream to ELK/DataDog
# Configure in Docker Compose
```

### 5.3 Backups

```bash
# Automated backups (configure in your provider)

# Manual backup
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore from backup
psql $DATABASE_URL < backup-20240101.sql
```

### 5.4 Updates & Patches

```bash
# Update Python dependencies
pip list --outdated
pip install --upgrade package-name

# Update Node dependencies
npm outdated
npm update

# Update Docker base images
docker pull python:3.10-slim
docker pull node:18-alpine

# Rebuild and redeploy
docker-compose up -d --build
```

---

## Part 6: Performance Optimization

### 6.1 Database Optimization

```sql
-- Already indexed:
CREATE INDEX idx_transaction_user_id ON transactions(user_id);
CREATE INDEX idx_transaction_created ON transactions(created_at);
CREATE INDEX idx_prediction_risk ON predictions(risk_level);
CREATE INDEX idx_alert_status ON fraud_alerts(status);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM transactions WHERE user_id = 1;
```

### 6.2 Backend Optimization

```bash
# Use production ASGI server (Gunicorn + Uvicorn)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Enable caching
# Implement Redis for session caching
# Cache model predictions if needed

# Monitor performance
# Memory usage
# CPU usage
# Database query times
```

### 6.3 Frontend Optimization

```bash
# Production build
npm run build

# Gzip compression (automatic on Vercel)
# Code splitting (React Router)
# Lazy loading (Recharts)
# Image optimization

# Monitor Core Web Vitals
# LCP: Largest Contentful Paint
# FID: First Input Delay
# CLS: Cumulative Layout Shift
```

---

## Part 7: Troubleshooting

### Issue: "Database connection refused"

```bash
# Check PostgreSQL is running
psql postgres

# Verify connection string
echo $DATABASE_URL

# Correct format:
# postgresql://username:password@host:port/database

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: "ML model not found"

```bash
# Check model artifacts exist
ls -la ml/artifacts/

# Files should be:
# - fraud_model.joblib
# - preprocessor.joblib
# - model_metadata.json

# Check paths in .env
MODEL_PATH=../ml/artifacts/fraud_model.joblib
PREPROCESSOR_PATH=../ml/artifacts/preprocessor.joblib
MODEL_METADATA_PATH=../ml/artifacts/model_metadata.json
```

### Issue: "CORS errors"

```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Reload application
# Render: Auto-redeployment
# Docker: docker-compose restart backend
# Local: Restart uvicorn
```

### Issue: "JWT token expired"

```bash
# This is normal. Frontend handles refresh.
# Check JWT_ACCESS_TOKEN_EXPIRE_MINUTES
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Increase if needed (security tradeoff)
```

### Issue: "Out of memory"

```bash
# Increase container memory
docker-compose.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G

# Or on Render: Upgrade instance size
```

---

## Part 8: Cost Estimation

### Free Tier Options
- **Vercel**: Free tier includes frontend hosting
- **Render**: Free tier ($0/month) for backend with limitations
- **Heroku Postgres**: Free tier removed, use AWS RDS free tier (12 months)
- **AWS RDS**: Free tier (12 months, t3.micro)

### Minimal Production Setup (Monthly)
- **Vercel Frontend**: $0 (free tier) or $20/month
- **Render Backend**: $7/month (Starter)
- **PostgreSQL**: $15/month (AWS RDS) or $50/month (Managed)
- **Total**: $22-65/month

### Recommended Production (Monthly)
- **Vercel Frontend**: $20/month
- **Render Backend**: $25/month (Professional)
- **PostgreSQL**: $30/month (AWS RDS)
- **Monitoring**: $0-30/month
- **Total**: $75-105/month

---

## Part 9: Quick Deployment Checklist

```bash
# Pre-deployment
☐ All tests passing (npm test, pytest)
☐ No console errors (npm run build)
☐ Environment variables set
☐ Database backups taken
☐ SSL/TLS certificates valid
☐ Security headers configured
☐ Rate limiting enabled
☐ Monitoring set up
☐ Error logging configured
☐ Secrets managed (no .env in repo)

# Deployment
☐ Push code to GitHub
☐ Vercel auto-deploys frontend
☐ Render auto-deploys backend
☐ Database migrations run
☐ Health checks pass
☐ Admin user created
☐ Test login works
☐ API endpoints respond
☐ Frontend connects to API

# Post-deployment
☐ Monitor error logs (first 24h)
☐ Test critical paths
☐ Verify database backups
☐ Set up alerts
☐ Document deployment details
☐ Train team on maintenance
```

---

## Part 10: Production URLs

Once deployed, you'll have:

```
Frontend: https://your-app.vercel.app
Backend API: https://your-app-backend.onrender.com
API Docs: https://your-app-backend.onrender.com/docs

Database: postgres://user:pass@host:port/fraudguard
```

---

## Maintenance Commands

### Daily
```bash
# Check health
curl https://your-app-backend.onrender.com/api/health
```

### Weekly
```bash
# Review logs
# Backup database
pg_dump $DATABASE_URL | gzip > backup-weekly.sql.gz
```

### Monthly
```bash
# Security updates
pip install --upgrade -r requirements.txt
npm upgrade

# Performance review
# Database analysis
ANALYZE;
VACUUM;

# Rebuild indexes
REINDEX DATABASE fraudguard;
```

### Quarterly
```bash
# Full security audit
# Dependency audit (npm audit, pip check)
# Performance tuning
# Capacity planning
```

---

## Support & Documentation

- **API Docs**: `/docs` (Swagger UI)
- **API Schema**: `/openapi.json`
- **GitHub Issues**: Use for bugs
- **Discussions**: Use for questions
- **Email**: For security issues

---

## Next Steps

1. **Choose deployment method** (Vercel + Render recommended)
2. **Set up accounts** (Vercel, Render, AWS/Heroku Postgres)
3. **Follow deployment steps** above
4. **Test thoroughly** before production
5. **Set up monitoring** and alerts
6. **Document your setup** for team
7. **Regular maintenance** (weekly backups, monthly updates)

---

## Production Deployment is Now Ready! 🚀

You have a **production-grade fraud detection platform** ready to deploy.
