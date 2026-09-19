#!/bin/bash
# Phase 1 Verification Script
# Checks that all Phase 1 components are properly set up

echo "🔍 FraudGuard AI - Phase 1 Verification"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for checks
PASSED=0
FAILED=0

# Function to check if command exists
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $2 (Not found: $1)"
        ((FAILED++))
    fi
}

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $2 (File not found: $1)"
        ((FAILED++))
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $2 (Directory not found: $1)"
        ((FAILED++))
    fi
}

echo "📋 System Dependencies"
echo "---------------------"
check_command "python" "Python 3.10+"
check_command "psql" "PostgreSQL"
check_command "node" "Node.js"
check_command "docker" "Docker (optional)"
echo ""

echo "📁 Project Structure"
echo "-------------------"
check_dir "backend" "Backend directory"
check_dir "frontend" "Frontend directory"
check_dir "database" "Database directory"
check_dir "ml" "ML directory"
check_dir "docs" "Documentation directory"
check_file "docker-compose.yml" "Docker Compose file"
check_file ".gitignore" "Git ignore file"
echo ""

echo "🔧 Backend Configuration"
echo "-----------------------"
check_file "backend/requirements.txt" "Backend requirements"
check_file "backend/.env.example" "Backend environment template"
check_file "backend/Dockerfile" "Backend Dockerfile"
check_file "backend/pytest.ini" "Pytest configuration"
echo ""

echo "📝 Backend Source Files"
echo "----------------------"
check_file "backend/app/main.py" "Main FastAPI app"
check_file "backend/app/core/config.py" "Configuration"
check_file "backend/app/core/database.py" "Database setup"
check_file "backend/app/core/security.py" "Security utilities"
check_file "backend/app/models/models.py" "Database models"
check_file "backend/app/schemas/user.py" "Pydantic schemas"
check_file "backend/app/api/auth.py" "Authentication routes"
check_file "backend/app/api/health.py" "Health check routes"
echo ""

echo "🧪 Backend Tests"
echo "----------------"
check_file "backend/tests/test_auth.py" "Authentication tests"
echo ""

echo "🎨 Frontend Configuration"
echo "------------------------"
check_file "frontend/package.json" "Frontend package"
check_file "frontend/.env.example" "Frontend environment template"
check_file "frontend/vite.config.ts" "Vite configuration"
check_file "frontend/tsconfig.json" "TypeScript configuration"
check_file "frontend/tailwind.config.js" "Tailwind configuration"
check_file "frontend/postcss.config.js" "PostCSS configuration"
check_file "frontend/index.html" "HTML entry point"
echo ""

echo "📦 Frontend Source Files"
echo "------------------------"
check_file "frontend/src/main.tsx" "Main entry point"
check_file "frontend/src/App.tsx" "Main App component"
check_file "frontend/src/index.css" "Global CSS"
check_file "frontend/src/pages/LoginPage.tsx" "Login page"
check_file "frontend/src/pages/RegisterPage.tsx" "Register page"
check_file "frontend/src/pages/DashboardPage.tsx" "Dashboard page"
check_file "frontend/src/pages/NotFoundPage.tsx" "404 page"
echo ""

echo "💾 Database"
echo "-----------"
check_file "database/schema.sql" "Database schema"
echo ""

echo "📚 Documentation"
echo "----------------"
check_file "docs/phase1-setup.md" "Phase 1 setup guide"
check_file "README.md" "Main README"
echo ""

echo "======================================"
echo "Verification Summary"
echo "======================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Phase 1 Structure Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Set up your environment:"
    echo "   cd backend && cp .env.example .env"
    echo "   python -m venv venv && source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "2. Set up database:"
    echo "   docker-compose up -d postgres"
    echo "   # or manually create PostgreSQL database"
    echo ""
    echo "3. Run tests:"
    echo "   pytest"
    echo ""
    echo "4. Start backend:"
    echo "   uvicorn app.main:app --reload"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some files are missing. Check above.${NC}"
    exit 1
fi
