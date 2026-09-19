#!/bin/bash

# FraudGuard AI - Setup and Deployment Preparation Script
# This script helps prepare the project for deployment

set -e

echo "🚀 FraudGuard AI - Setup Script"
echo "================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python 3 found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Docker (optional)
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker found: $DOCKER_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Docker not found (optional, needed for Docker deployment)"
fi

echo ""
echo -e "${BLUE}Prerequisites check complete!${NC}"
echo ""

# Choose setup option
echo "Choose setup option:"
echo "1) Local development (Python + Node)"
echo "2) Docker deployment"
echo "3) Production deployment (Vercel + Render)"
echo "4) Just prepare environment files"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Setting up for local development...${NC}"
        echo ""
        
        # Backend setup
        echo "Setting up backend..."
        cd backend
        
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        echo "Activating virtual environment..."
        source venv/bin/activate
        
        echo "Installing dependencies..."
        pip install -r requirements.txt
        
        # Create .env if not exists
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            cp .env.example .env
            echo -e "${YELLOW}⚠${NC} Please edit backend/.env with your settings"
        fi
        
        cd ..
        
        # Frontend setup
        echo ""
        echo "Setting up frontend..."
        cd frontend
        
        echo "Installing dependencies..."
        npm install
        
        # Create .env if not exists
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            cp .env.example .env
        fi
        
        cd ..
        
        echo ""
        echo -e "${GREEN}✓ Local development setup complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Edit backend/.env with your database credentials"
        echo "2. Edit frontend/.env if needed"
        echo "3. Start PostgreSQL"
        echo "4. Run: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
        echo "5. Run: cd frontend && npm run dev"
        echo ""
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}Setting up for Docker deployment...${NC}"
        echo ""
        
        # Check docker-compose
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}✗${NC} docker-compose not found"
            exit 1
        fi
        
        # Create environment files
        echo "Creating environment files..."
        
        if [ ! -f "backend/.env" ]; then
            cp backend/.env.example backend/.env
            echo -e "${YELLOW}⚠${NC} Please edit backend/.env"
        fi
        
        if [ ! -f "frontend/.env" ]; then
            cp frontend/.env.example frontend/.env
        fi
        
        echo ""
        echo -e "${GREEN}✓ Docker setup complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Edit backend/.env with your settings"
        echo "2. Run: docker-compose up -d"
        echo "3. Run: docker exec fraudguard-backend python -m backend.scripts.create_admin"
        echo "4. Open: http://localhost:3000"
        echo ""
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}Setting up for production deployment...${NC}"
        echo ""
        
        # Create environment files
        echo "Creating environment files..."
        
        if [ ! -f "backend/.env.production" ]; then
            cp backend/.env.production.example backend/.env.production
            echo -e "${YELLOW}⚠${NC} Please edit backend/.env.production with production settings"
        fi
        
        if [ ! -f ".env.production" ]; then
            cp .env.production.example .env.production
            echo -e "${YELLOW}⚠${NC} Please edit .env.production"
        fi
        
        echo ""
        echo -e "${GREEN}✓ Production setup prepared!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Read DEPLOYMENT_GUIDE.md (Part 3)"
        echo "2. Choose deployment option:"
        echo "   - Option A: Vercel + Render (recommended)"
        echo "   - Option B: AWS/GCP/Azure"
        echo "3. Set up accounts and services"
        echo "4. Configure environment variables"
        echo "5. Deploy!"
        echo ""
        ;;
        
    4)
        echo ""
        echo -e "${BLUE}Preparing environment files...${NC}"
        echo ""
        
        if [ ! -f "backend/.env" ]; then
            cp backend/.env.example backend/.env
            echo -e "${GREEN}✓${NC} Created backend/.env"
        else
            echo -e "${YELLOW}⚠${NC} backend/.env already exists"
        fi
        
        if [ ! -f "frontend/.env" ]; then
            cp frontend/.env.example frontend/.env
            echo -e "${GREEN}✓${NC} Created frontend/.env"
        else
            echo -e "${YELLOW}⚠${NC} frontend/.env already exists"
        fi
        
        if [ ! -f "backend/.env.production" ]; then
            cp backend/.env.production.example backend/.env.production
            echo -e "${GREEN}✓${NC} Created backend/.env.production"
        else
            echo -e "${YELLOW}⚠${NC} backend/.env.production already exists"
        fi
        
        if [ ! -f ".env.production" ]; then
            cp .env.production.example .env.production
            echo -e "${GREEN}✓${NC} Created .env.production"
        else
            echo -e "${YELLOW}⚠${NC} .env.production already exists"
        fi
        
        echo ""
        echo -e "${YELLOW}⚠${NC} Remember to edit these files with your actual settings!"
        echo ""
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Final instructions
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo "📚 Documentation:"
echo "  - QUICK_START.md       → Get running in 5 minutes"
echo "  - DEPLOYMENT_GUIDE.md  → Complete deployment guide"
echo "  - README.md            → Project overview"
echo "  - docs/explainability.md → SHAP guide"
echo ""
echo "🚀 Quick commands:"
echo "  - Local:   docker-compose up -d"
echo "  - Frontend: npm run dev"
echo "  - Backend:  uvicorn app.main:app --reload"
echo "  - Tests:    pytest tests/"
echo ""
echo "📞 Support:"
echo "  - Issues: GitHub Issues"
echo "  - Questions: GitHub Discussions"
echo ""
echo -e "${BLUE}Happy deploying! 🎉${NC}"
