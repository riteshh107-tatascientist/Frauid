"""
FraudGuard AI - FastAPI Main Application

Entry point for the fraud detection backend with ML integration.
"""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.api.router import api_router
from app.services.ml_service import initialize_ml_service, get_ml_service
from app.services.risk_engine import initialize_risk_engine
from app.services.explainability_service import ExplainabilityService

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    
    Startup tasks:
    - Load ML model artifacts
    - Initialize risk engine
    - Verify database connection
    
    Shutdown:
    - Clean up resources
    """
    # ====== STARTUP ======
    logger.info("=" * 70)
    logger.info("FRAUDGUARD AI STARTING UP")
    logger.info("=" * 70)
    
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize ML Service
    logger.info("\n📦 Initializing ML Service...")
    ml_success = initialize_ml_service(
        model_path=settings.model_path,
        preprocessor_path=settings.preprocessor_path,
        metadata_path=settings.model_metadata_path
    )
    
    if ml_success:
        logger.info("✓ ML Service loaded successfully")
    else:
        logger.error("✗ Failed to load ML Service")
        logger.error(f"  Model path: {settings.model_path}")
        logger.error(f"  Preprocessor path: {settings.preprocessor_path}")
        logger.error(f"  Metadata path: {settings.model_metadata_path}")
    
    # Initialize Risk Engine
    logger.info("\n⚙️  Initializing Risk Engine...")
    risk_engine = initialize_risk_engine(
        low_threshold=0.3,
        high_threshold=0.7,
        prediction_threshold=0.5
    )
    logger.info("✓ Risk Engine initialized")
    
    # Initialize Explainability Service (SHAP)
    logger.info("\n🔍 Initializing SHAP Explainability Service...")
    try:
        if ml_success:
            ml_service = get_ml_service()
            explainability_service = ExplainabilityService.initialize(
                model=ml_service.model,
                preprocessor=ml_service.preprocessor,
                metadata=ml_service.metadata
            )
            if explainability_service and explainability_service.is_available():
                logger.info("✓ SHAP Explainability Service initialized successfully")
            else:
                logger.warning("⚠️  SHAP Explainability Service failed to initialize")
        else:
            logger.warning("⚠️  Skipping Explainability Service (ML Service not loaded)")
    except Exception as e:
        logger.error(f"⚠️  Failed to initialize Explainability Service: {str(e)}")
    
    logger.info("\n✅ FraudGuard AI is ready")
    logger.info("=" * 70 + "\n")
    
    yield
    
    # ====== SHUTDOWN ======
    logger.info("=" * 70)
    logger.info("FRAUDGUARD AI SHUTTING DOWN")
    logger.info("=" * 70)


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description="AI-Powered Fraud Detection and Risk Intelligence Platform",
    version=settings.api_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FraudGuard AI API",
        "version": settings.api_version,
        "description": "AI-Powered Fraud Detection Platform",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/api/health",
            "predict": "/api/transactions/predict",
            "model_info": "/api/model/info",
            "transactions": "/api/transactions",
            "dashboard": "/api/dashboard/summary"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
