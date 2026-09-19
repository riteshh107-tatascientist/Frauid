"""
API routes initialization

Assembles all route modules into a single router.
"""

from fastapi import APIRouter

from app.api.routes import prediction, transactions, dashboard, admin, explanations
from app.api import health

# Create main router
api_router = APIRouter(prefix="/api")

# Include health check routes
api_router.include_router(health.router)

# Include prediction routes
api_router.include_router(prediction.router)

# Include transaction routes
api_router.include_router(transactions.router)

# Include dashboard routes
api_router.include_router(dashboard.router)

# Include admin routes (prefixed with /admin)
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Include explanation routes (SHAP explainability)
api_router.include_router(explanations.router, tags=["Explainability"])
