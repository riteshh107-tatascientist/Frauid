# FraudGuard AI

**AI-Powered Transaction Fraud Detection & Risk Intelligence Platform**

A production-ready fraud detection system combining machine learning, rule-based risk signals, and anomaly detection to identify fraudulent transactions in real-time.

## Project Status

🔨 **Phase 1: Backend Foundation (IN PROGRESS)**
- Project structure
- PostgreSQL schema
- FastAPI foundation
- Authentication setup

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd fraudguard-ai

# Phase 1: Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
# (Will be implemented in Phase 2)

# Start backend
uvicorn app.main:app --reload

# In another terminal, Phase 1 doesn't require frontend yet
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React/Vite)                 │
├─────────────────────────────────────────────────────────┤
│                   FastAPI Backend                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Authentication │ Prediction API │ Risk Engine   │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│              ML Model + SHAP Explanations               │
├─────────────────────────────────────────────────────────┤
│                  PostgreSQL Database                    │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Recharts, Vite
- **Backend**: Python 3.10+, FastAPI, Pydantic, SQLAlchemy
- **ML**: Scikit-learn, XGBoost, SHAP, Pandas, NumPy
- **Database**: PostgreSQL
- **Deployment**: Vercel (frontend), Render/Railway (backend)
- **Auth**: JWT, bcrypt

## Project Structure

```
fraudguard-ai/
├── backend/              # FastAPI application
├── frontend/            # React application
├── ml/                  # ML pipeline and models
├── database/            # SQL schemas
├── docs/                # Documentation
└── docker-compose.yml   # Local development
```

## Development Phases

1. ✅ **Phase 1**: Backend foundation + database
2. ⏳ **Phase 2**: ML pipeline + dataset + training
3. ⏳ **Phase 3**: Prediction API
4. ⏳ **Phase 4**: Authentication
5. ⏳ **Phase 5**: React dashboard
6. ⏳ **Phase 6**: Transaction history + alerts
7. ⏳ **Phase 7**: Explainable AI (SHAP)
8. ⏳ **Phase 8**: Testing
9. ⏳ **Phase 9**: Docker
10. ⏳ **Phase 10**: Deployment configuration
11. ⏳ **Phase 11**: README + interview docs

## Key Features (Target)

- ✅ User authentication (JWT)
- ✅ Real ML-based fraud prediction
- ✅ Multi-layer risk scoring (ML + rules + anomaly)
- ✅ Transaction history and search
- ✅ Fraud alerts system
- ✅ SHAP explainability
- ✅ Admin dashboard
- ✅ Real-time analytics
- ✅ PostgreSQL persistence

## Important Disclaimer

**This is an educational/portfolio prototype** for demonstrating fraud detection concepts. It is not intended for production banking use. Real financial fraud systems require regulatory compliance, advanced infrastructure, real-time processing, and extensive security hardening.

## License

MIT
