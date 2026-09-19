"""
Prediction API routes for FraudGuard AI
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.prediction import (
    TransactionPredictionRequest,
    PredictionResponse,
    ModelInfoResponse,
)
from app.services.ml_service import get_ml_service
from app.services.risk_engine import get_risk_engine
from app.models.models import Transaction, User
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/transactions/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict fraud probability",
    description="Make a fraud prediction on a transaction using the trained ML model."
)
async def predict_transaction(
    request: TransactionPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict fraud probability for a transaction.
    
    The prediction is based on the trained XGBoost model from Phase 2.
    Probabilities are converted to risk scores and risk levels.
    Prediction is stored in PostgreSQL database.
    
    Args:
        request: Transaction features (Time, V1-V28, Amount)
        db: Database session
        
    Returns:
        PredictionResponse with fraud probability and risk level
    """
    try:
        # Get services
        ml_service = get_ml_service()
        risk_engine = get_risk_engine()
        
        # Validate features
        features_dict = request.dict()
        is_valid, error_msg = ml_service.validate_features(features_dict)
        
        if not is_valid:
            logger.warning(f"Invalid features: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        
        # Get prediction from real model
        fraud_probability, model_prediction = ml_service.predict(features_dict)
        
        # Classify risk
        risk_classification = risk_engine.classify(fraud_probability)
        
        # Get model info
        model_info = ml_service.get_model_info()
        
        # Prepare response
        response = PredictionResponse(
            prediction=model_prediction,
            fraud_probability=fraud_probability,
            risk_score=risk_classification['risk_score'],
            risk_level=risk_classification['risk_level'],
            model_version=model_info['model_version'],
            explanation_available=False  # Phase 7
        )
        
        # Store in database associated with current user
        try:
            transaction = Transaction(
                user_id=current_user.id,
                amount=request.Amount,
                transaction_type='credit_card',
                transaction_hour=int((request.Time % 86400) / 3600),
                device_type='unknown',
                location='unknown',
                fraud_probability=fraud_probability,
                risk_score=risk_classification['risk_score'],
                risk_level=risk_classification['risk_level'],
                prediction=model_prediction,
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            logger.info(
                f"Prediction stored: ID={transaction.id}, "
                f"Prob={fraud_probability:.4f}, "
                f"RiskLevel={risk_classification['risk_level']}"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to store prediction: {str(e)}")
            # Don't fail the prediction if storage fails
            # But log it for monitoring
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction service error"
        )


@router.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Get model information",
    description="Get information about the trained fraud detection model."
)
async def get_model_info():
    """
    Get information about the trained ML model.
    
    Returns model name, version, threshold, features, and evaluation metrics.
    All data comes from Phase 2 model metadata.
    
    Returns:
        ModelInfoResponse with complete model information
    """
    try:
        ml_service = get_ml_service()
        
        if not ml_service.is_loaded:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model not available"
            )
        
        model_info = ml_service.get_model_info()
        
        return ModelInfoResponse(**model_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model information"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status of API and ML service
    """
    try:
        ml_service = get_ml_service()
        status = ml_service.get_status()
        
        return {
            "status": "healthy" if status['model_loaded'] else "degraded",
            "ml_model": status['status'],
            "model_name": status['model_name'],
            "model_version": status['model_version'],
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "ml_model": "unavailable",
            "error": str(e)
        }
